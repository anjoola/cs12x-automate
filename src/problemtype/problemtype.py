import cgi
from cStringIO import StringIO
import difflib

import mysql.connector

from errors import *

class ProblemType(object):
  """
  Class: ProblemType
  ------------------
  A generic problem type. To be implemented for specific types of problems. If
  initialized with all its parameters set as None, then it would be used as
  a static class.
  """

  def __init__(self, db=None, specs=None, response=None, output=None,
               cache=None):
    # The database connection.
    self.db = db

    # The specifications for this problem.
    self.specs = specs

    # The student's response for this problem.
    self.response = response

    # The graded problem output.
    self.output = output

    # Reference to the cache to store results of query runs to avoid having to
    # run the same query multiple times.
    self.cache = cache

    # The number of points the student has gotten on this question. They start
    # out with the maximum number of points, and points get deducted as the
    # tests go on.
    self.got_points = (0 if not self.specs else self.specs["points"])


  def preprocess(self):
    """
    Function: preprocess
    --------------------
    Check for certain things before running the tests and add them to the
    graded problem output. This includes:
      - Comments
      - Attaching results of query
      - Checking their SQL for certain keywords
      - Printing out their actual SQL
    """
    # Comments, query results, and SQL.
    self.output["comments"] = self.response.comments
    self.output["submitted-results"] = self.response.results # TODO might not include submitted results
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
    self.preprocess()

    # Run each test for the problem.
    for test in self.specs["tests"]:
      lost_points = 0
      graded_test = {"errors": [], "deductions": [], "success": False}
      self.output["tests"].append(graded_test)

      try:
        lost_points += self.grade_test(test, graded_test)

        # Apply any other deductions.
        if graded_test.get("deductions"): # TODO2
          for deduction in graded_test["deductions"]:
            lost = SQL_DEDUCTIONS[deduction]
            self.output["errors"].append("[-" + str(lost) + "]" + \
                                         repr(deduction()))
            lost_points += lost

      # If their query times out.
      #except timeouts.TimeoutError:
      #  self.output["errors"].append("Query timed out.") # TODO errors
      #  lost_points += test["points"]
      #  if test.get("teardown"): self.db.run_query(test["teardown"])

      # If there was a MySQL error, print out the error that occurred and the
      # code that caused the error.
      except mysql.connector.errors.Error as e:
        self.output["errors"].append(repr(MySQLError(e)))
        lost_points += test["points"]
        if test.get("teardown"): self.db.run_query(test["teardown"])

      self.got_points -= lost_points
      graded_test["got_points"] = test["points"] - lost_points

    # Run problem teardown queries.
    if self.specs.get("teardown"):
      for q in self.specs["teardown"]: self.db.run_query(q)

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


  def do_output(self, o, output, problem_specs):
    """
    Function: do_output
    -------------------
    Output the graded results for this problem to the given output string.

    o: The HTML output for this problem.
    output: The graded output for all the tests.
    problem_specs: The specs for this problem.
    """
    has_printed_test = False
    for (i, test) in enumerate(output):
      specs = problem_specs[i]

      # Only print the "Test" header once.
      if not has_printed_test:
        has_printed_test = True
        o.write("<b>Tests</b>\n<ul>\n")

      # Print whether or not the test was successful.
      if test["success"] == "UNDETERMINED":
        o.write("<li><div class='uncertain'>UNDETERMINED")
      elif test["success"]:
        o.write("<li><div class='passed'>PASSED")
      else:
        o.write("<li><div class='failed'>FAILED")

      # Other test details such as the number of points received, and the
      # description of the test.
      o.write(" (" + str(test["got_points"]) + "/" + \
        str(specs["points"]) + " Points)</div><br>\n")
      if specs.get("desc"):
        o.write("<i>" + specs["desc"] + "</i><br>")
      if specs.get("query"):
        o.write("<div class='test-specs'>" + specs["query"] + "</div>")

      # Specific test printouts (different for different problem types).
      self.output_test(o, test, specs)

      if has_printed_test: o.write("</li>\n")
    if has_printed_test: o.write("</ul>")


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

  def e(self, text):
    """
    Function: e
    -----------
    Escapes text so it can be outputted as HTML.
    """
    return cgi.escape(text.encode('ascii', 'xmlcharrefreplace'))


  def equals(self, lst1, lst2):
    """
    Function: equals
    ----------------
    Compares two lists of tuples to see if their contents are equal.
    """
    return [tuple(unicode(x).lower() for x in y) for y in lst1] == \
           [tuple(unicode(x).lower() for x in y) for y in lst2]


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

    # Get the diffs.
    (one, two) = ([], [])
    diff = difflib.ndiff([x.lower() for x in lst1], \
      [x.lower() for x in lst2], is_line_junk)

    # True if last added to "one".
    last_added = True
    # True if we've just seen a close match and need to modify the NEXT
    # row coming in.
    close_match = False

    # TODO: This diff stuff doesn't actually work?
    for item in diff:
      # If just a whitespace change, ignore.
      if len(item[2: ].strip()) == 0:
        continue

      # If the previous thing was a close match.
      if close_match and item.startswith("+"):
        close_match = False
        two.append(("", item.replace("+ ", "")))
      # A subtraction; goes in the "one" list.
      elif item.startswith("-"):
        last_added = True
        one.append(("remove", item.replace("- ", "")))
      # An addition, goes in the "two" list.
      elif item.startswith("+"):
        last_added = False
        two.append(("add", item.replace("+ ", "")))
      # Similar lines, but not the same. Don't count them as the same line.
      elif item.find("?") != -1 and item.find("^") != -1:
        continue
      # Close match for the previous two elements. Don't mark them as being
      # added or removed.
      elif item.find("?") != -1:
        if not last_added:
          one[len(one)-1] = ("", one[len(one)-1][1])
          two[len(two)-1] = ("", two[len(two)-1][1])
        else:
          one[len(one)-1] = ("", one[len(one)-1][1])
          close_match = True
      # If the lines match completely.
      else:
        one.append(("", item[2:]))
        two.append(("", item[2:]))

    return (one, two)
