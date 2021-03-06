import difflib

import formatter

from CONFIG import PRECISION
from errors import (
  add,
  DatabaseError,
  MissingKeywordError,
  TimeoutError,
  QueryError
)

PRECISION_DIVISOR = float(10 ** PRECISION)

class SuccessType(object):
  """
  Class: SuccessType
  ------------------
  The result of a test (if it is successful).
  """
  SUCCESS = True
  FAILURE = False
  UNDETERMINED = "UNDETERMINED"


class ProblemType(object):
  """
  Class: ProblemType
  ------------------
  A generic problem type. To be implemented for specific types of problems. If
  initialized with all its parameters set as None, it would be used as
  a static class.
  """

  def __init__(self, assignment=None, db=None, specs=None, response=None, output=None):
    # Which assignment this is for.
    self.assignment = assignment

    # The database connection.
    self.db = db

    # The specifications for this problem.
    self.specs = specs

    # The student's response for this problem.
    self.response = response

    # The graded problem output.
    self.output = output

    # The number of points the student has gotten on this question. They start
    # out with the maximum number of points, and points get deducted as the
    # tests go on.
    self.got_points = (0 if not self.specs else self.specs["points"])


  def get_errors(self, errors, points):
    """
    Function: get_errors
    --------------------
    Gets the number of points to deduct for a set of QueryErrors.

    errors: The errors.
    points: The number of points the problem is worth.
    returns: A tuple of the form (deductions, error list), where deductions
             is the number of points to take off for the errors in 'error list'.
    """
    deductions = 0
    error_list = []
    for e in errors:
      deductions += QueryError.deduction(e, points)
      error_list.append(QueryError.to_string(e, points))
    return (deductions if deductions < points else points, error_list)


  def preprocess(self):
    """
    Function: preprocess
    --------------------
    Check for certain things before running the tests and add them to the
    graded problem output. This includes:
      - Comments
      - Checking their SQL for certain keywords
      - Printing out their actual SQL
    """
    # Comments and SQL.
    self.output["comments"] = self.response.comments
    self.output["sql"] = self.response.sql

    # Check if they included certain keywords.
    if self.specs.get("keywords"):
      missing = []
      for keyword in self.specs["keywords"]:
        if keyword not in self.response.sql:
          missing.append(keyword)
      # Add the missing keywords to the graded output.
      if len(missing) > 0:
        add(self.output["errors"], MissingKeywordError(missing))


  def grade(self):
    """
    Function: grade
    ---------------
    Runs all the tests for a particular problem and computes the number of
    points received for the student's response.

    returns: The number of points received for this response.
    """
    # Run each test for the problem.
    for test in self.specs["tests"]:
      lost_points = 0
      graded_test = {
        "errors": [],
        "deductions": [],
        "success": SuccessType.FAILURE
      }
      self.output["tests"].append(graded_test)

      # Set a new connection timeout if specified.
      if test.get("timeout"):
        self.db.get_db_connection(test["timeout"])

      # Grade the test with the specific handler.
      try:
        lost_points += self.grade_test(test, graded_test)

      # If their query times out, restart the connection and output an error.
      # Retry their query first (so all queries are tried at most twice).
      except TimeoutError as e:
        print "[timed out, trying again]"
        self.db.kill_query()
        self.db.get_db_connection(test.get("timeout"), False)
        add(self.output["errors"], e)

        # Retry their query. If it still doesn't work, then give up.
        try:
          lost_points += self.grade_test(test, graded_test)
        except TimeoutError as e:
          lost_points += test["points"]
          self.db.kill_query()
          self.db.get_db_connection(test.get("timeout"), False)
          self.output["got_points"] = 0
          continue

      # If there was a database error, print out the error that occurred.
      except DatabaseError as e:
        lost_points += test["points"]
        add(self.output["errors"], e)

      # Run the teardown query no matter what.
      finally:
        try:
          if test.get("teardown"):
            # print("RUNNING TEARDOWN FROM PROBLEMTYPES")
            self.db.execute_sql(test["teardown"])
        except DatabaseError as e:
          lost_points += test["points"]
          add(self.output["errors"], e)

      # Apply deductions.
      if graded_test.get("deductions"):
        (deductions, errors) = self.get_errors(graded_test["deductions"],
                                               test["points"])
        self.output["errors"] += errors
        lost_points += deductions

      self.got_points -= lost_points
      points = test["points"] - lost_points
      graded_test["got_points"] = points if points > 0 else 0

    # Get the total number of points received.
    self.got_points = (self.got_points if self.got_points > 0 else 0)
    self.output["got_points"] = self.got_points
    return self.got_points


  def grade_test(self, test, output):
    """
    Function: grade_test
    --------------------
    Runs a test.

    test: The specs for the test to run.
    output: The graded output for this test.

    returns: The number of points to deduct.
    """
    raise NotImplementedError("Must be implemented!")


  def do_output(self, o, output, problem_specs, hide_solutions):
    """
    Function: do_output
    -------------------
    Output the graded results for this problem to the given output string.

    o: The HTML output for this problem.
    output: The graded output for all the tests.
    problem_specs: The specs for this problem.
    hide_solutions: Whether or not to hide solution output.
    """
    # Show minimal information if hiding solutions.
    if hide_solutions:
      o.write("<div class='test-results'>")
      if any([test["success"] == SuccessType.UNDETERMINED for test in output]):
        o.write("Test results are <div class='uncertain'>UNDETERMINED</div>" +
                " and require TA input.\n")
      elif any([test["success"] == SuccessType.FAILURE for test in output]):
        o.write("Some tests have <div class='failed'>FAILED</div>!\n")
      else:
        o.write("All tests <div class='passed'>PASSED</div>!\n")
      o.write("</div>")

    # Otherwise show full test output.
    else:
      has_printed_test = False
      for (i, test) in enumerate(output):
        specs = problem_specs[i]

        # Only print the "Test" header once.
        if not has_printed_test:
          has_printed_test = True
          o.write("<b>Tests</b>\n<ul>\n")

        # Print whether or not the test was successful.
        if test["success"] == SuccessType.UNDETERMINED:
          o.write("<li><div class='uncertain'>UNDETERMINED")
        elif test["success"]:
          o.write("<li><div class='passed'>PASSED")
        else:
          o.write("<li><div class='failed'>FAILED")

        # Other test details such as the number of points received, and the
        # description of the test. Only print the number of points if the test
        # result is not undetermined.
        if test["success"] != SuccessType.UNDETERMINED:
          o.write(" (" + str(test.get("got_points", 0)) + "/" +
                  str(specs["points"]) + " Points)")
        o.write("</div><br>\n")
        if specs.get("desc"):
          o.write("<i>" + specs["desc"] + "</i><br>")
        if specs.get("query"):
          o.write("<div class='test-specs' contenteditable='true' " +
                  "onclick='document.execCommand(\"selectAll\", false,null)'>" +
                  specs["query"] + "</div>")

        # Specific test printouts (different for different problem types).
        self.output_test(o, test, specs)

        if has_printed_test:
          o.write("</li>\n")

      if has_printed_test:
        o.write("</ul>")


  def output_test(self, o, test, specs):
    """
    Function: output_test
    ---------------------
    Outputs the test results of a particular problem type.

    o: The HTML output.
    test: The graded test.
    specs: Specs for this test.
    """
    raise NotImplementedError("Must be implemented!")

# ----------------------------- Utility Functions ---------------------------- #

  def equals(self, res1, res2, check_row_order=False, check_col_order=False):
    """
    Function: equals
    ----------------
    Compares two query results to see if they are equals.

    res1: The first result.
    res2: The second result.
    check_row_order: Whether or not to check for the row order of results.
    check_col_order: Whether ot not the check for the column order of results.
    """

    def roundn(val, input_type):
      """
      Function: roundn
      ----------------
      Rounds numeric values to the specified PRECISION in CONFIG.py if this
      is a numeric value.
      """
      if input_type != float:
        return val
      val = 0.0 if val is None else float(val)
      return round(val * PRECISION_DIVISOR) / PRECISION_DIVISOR


    # If the results do not have the same number of rows or the same number of,
    # columns, then they are definitely not equal.
    if len(res1.results) != len(res2.results) or \
       len(res1.schema) != len(res2.schema):
      return False

    # Sort the rows if the row order does not matter.
    lst1 = sorted(res1.results) if not check_row_order else res1.results
    lst2 = sorted(res2.results) if not check_row_order else res2.results

    for row1, row2 in zip(lst1, lst2):
      (row_converted1, row_converted2) = ([], [])
      for i, (col1, col2) in enumerate(zip(row1, row2)):
        row_converted1.append(roundn(col1, res1.col_types[i]))
        row_converted2.append(roundn(col2, res2.col_types[i]))

      # If the column order doesn't matter, sort the columns.
      if not check_col_order:
        try:
          row_converted1 = sorted(row_converted1)
          row_converted2 = sorted(row_converted2)
        except TypeError as e:
          print("Couldn't sort columns.")
          print("row_converted1 = %s" % str(row_converted1))
          print("row_converted2 = %s" % str(row_converted2))
          return False

      if row_converted1 != row_converted2:
        return False
    return True


  def get_diffs(self, lst1, lst2):
    """
    Function: get_diffs
    -------------------
    Gets the diffs of two lists.

    lst1: The first list.
    lst2: The second list.
    returns: A tuple containing two lists (one for lst1, one for lst2). The list
             contains tuples of the form (type, value) where type can either be
             "add", "remove", or "".
    """

    def is_line_junk(string):
      """
      Function: is_line_junk
      ----------------------
      Returns whether or not a line is junk and should be ignored when doing
      a diff.
      """
      return string == " " or string == "-" or string == "+"

    # Get the diffs. We want to do a lowercase comparison.
    (one, two) = ([], [])
    diff = difflib.ndiff([x.lower() for x in lst1],
                         [x.lower() for x in lst2], is_line_junk)
    # Need to keep a dictionary of the lowercase results vs. the original
    # because we want to output in the original case.
    case_dict = dict([(x.lower(), x) for x in lst1] +
                     [(x.lower(), x) for x in lst2])

    # True if last added to "one".
    last_added = True
    # True if we've just seen a close match and need to modify the NEXT
    # row coming in.
    close_match = False

    for item in diff:
      # If just a whitespace change, ignore.
      if len(item[2: ].strip()) == 0:
        continue

      # If the previous thing was a close match.
      if close_match and item.startswith("+"):
        close_match = False
        two.append(("", case_dict[item[2:]]))
      # A subtraction; goes in the "one" list.
      elif item.startswith("-"):
        last_added = True
        one.append(("remove", case_dict[item[2:]]))
      # An addition, goes in the "two" list.
      elif item.startswith("+"):
        last_added = False
        two.append(("add", case_dict[item[2:]]))
      # Similar lines, but not the same. Don't count them as the same line.
      elif item.find("?") != -1 and item.find("^") != -1:
        continue
      # Close match for the previous two elements. Don't mark them as being
      # added or removed.
      elif item.find("?") != -1:
        if not last_added:
          one[len(one) - 1] = ("", one[len(one) - 1][1])
          two[len(two) - 1] = ("", two[len(two) - 1][1])
        else:
          one[len(one) - 1] = ("", one[len(one) - 1][1])
          close_match = True
      # If the lines match completely.
      else:
        one.append(("", case_dict[item[2:]]))
        two.append(("", case_dict[item[2:]]))

    return (one, two)


  def generate_diffs(self, lst1, lst2, o):
    """
    Function: generate_diffs
    ------------------------
    Generates the HTML output for a diff between lst1 and lst2.

    lst1: The first list.
    lst2: The second list.
    o: The output pointer.
    """
    (ediff, adiff) = self.get_diffs(lst1, lst2)
    (eindex, aindex) = (0, 0)

    # Heading for expected and actual.
    expected_length = len("Expected") if len(ediff) == 0 else len(ediff[0][1])
    o.write("<b>Expected</b>" +
            " " * (expected_length - len("Expected") + 6) + "<b>Actual</b>\n")
    space = " " * (max(expected_length, len("Expected")) + 6)

    while eindex < len(ediff):
      (diff_type, evalue) = ediff[eindex]
      # An expected result not found in the actual results.
      if diff_type == "remove":
        o.write("<font color='red'>" + formatter.escape(evalue) + "</font>\n")
        eindex += 1
        continue

      (diff_type, avalue) = adiff[aindex]
      # Matching actual and expected results.
      if diff_type == "":
        o.write(formatter.escape(evalue + "      " + avalue) + "\n")
        aindex += 1
        eindex += 1
      # An actual result not found in the expected results.
      elif diff_type == "add":
        o.write(space + "<font color='red'>" + formatter.escape(avalue) +
                "</font>\n")
        aindex += 1

    # Any remaining actual results.
    while aindex < len(adiff):
      (_, avalue) = adiff[aindex]
      o.write(space + "<font color='red'>" + formatter.escape(avalue) +
              "</font>\n")
      aindex += 1
