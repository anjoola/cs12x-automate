import cgi
from cStringIO import StringIO
from CONFIG import TYPE_OUTPUTS
import difflib

class TestOutput:
  """
  Class: TestOutput
  -----------------
  Handles the different kinds of output for the tests.
  """

  def __init__(self, o):
    # The output TODO
    self.o = o


  def get_function(self, specs):
    """
    Function: get_function
    ----------------------
    Finds the right function to call on for the specified test type.

    specs: The specs for the test.
    returns: A function object.
    """
    test_type = specs["type"]
    if test_type == "select":
      return self.select
    elif test_type == "create":
      return self.create
    elif test_type == "insert":
      return self.insert
    elif test_type == "stored-procedure":
      return self.sp
    elif test_type == "function":
      return self.function


  def output(self, tests, specs):
    """
    Function: output
    ----------------
    Output the details for the test results.

    tests: The list of test results for a particular student.
    specs: The specs for the tests.
    """
    o = self.o
    has_printed_test = False
    for (i, test) in enumerate(tests):
      test_specs = specs[i]

      # Don't print output if not specified in the CONFIG file.
      if test_specs["type"] not in TYPE_OUTPUTS:
        continue

      if not has_printed_test:
        has_printed_test = True
        o.write("<b>Tests</b>\n<ul>\n")

      # General test details.
      if test["success"] == "UNDETERMINED":
        o.write("<li><div class='uncertain'>UNDETERMINED")
      elif test["success"]:
        o.write("<li><div class='passed'>PASSED")
      else:
        o.write("<li><div class='failed'>FAILED")
      o.write(" (" + str(test["got_points"]) + "/" + \
        str(test_specs["points"]) + " Points)</div><br>\n")
      if test_specs.get("desc"):
        o.write("<i>" + test_specs["desc"] + "</i><br>")
      o.write("<div class='test-specs'>" + test_specs["query"] + "</div>")

      # Specific test printouts.
      f = self.get_function(test_specs)
      f(test, test_specs)

      if has_printed_test: o.write("</li>\n")
    if has_printed_test: o.write("</ul>")


  def select(self, test, specs):
    """
    Function: select
    ----------------
    Outputs the results of a SELECT test. This includes the following:
      - Expected results
      - Actual results
    """
    o = self.o
    if test["success"] or "expected" not in test:
      return

    # Expected and actual output.
    o.write("<pre class='results'>")
    (ediff, adiff) = get_diffs(test["expected"].split("\n"), \
      test["actual"].split("\n"))

    (eindex, aindex) = (0, 0)
    space = " " * (len(ediff[eindex][1]) + 6)
    while eindex < len(ediff):
      (diff_type, evalue) = ediff[eindex]
      # An expected result not found in the actual results.
      if diff_type == "remove":
        o.write("<font color='red'>" + e(evalue) + "</font>\n")
        eindex += 1
        continue

      (diff_type, avalue) = adiff[aindex]
      # Matching actual and expected results.
      if diff_type == "":
        o.write(e(evalue + "      " + avalue) + "\n")
        aindex += 1
        eindex += 1
      # An actual result not found in the expected results.
      elif diff_type == "add":
        o.write(space + "<font color='red'>" + e(avalue) + "</font>\n")
        aindex += 1

    # Any remaining actual results.
    while aindex < len(adiff):
      (_, avalue) = adiff[aindex]
      o.write(space + "<font color='red'>" + e(avalue) + "</font>\n")
      aindex += 1

    o.write("</pre>")


  def create(self, test, specs):
     """
     Function: create
     ----------------
     Outputs the result of a CREATE test. This includes the following:
     TODO
     """
     pass


  def insert(self, test, specs):
    """
    Function: insert
    ----------------
    Outputs the result of an INSERT test. TODO
    """
    pass


  def sp(self, test, specs):
    """
    Function: sp
    ------------
    Outputs the result of a stored procedure test. This includes the following:
      - Changes to the table affected by the stored procedure call.
    """
    o = self.o
    # If there are no changes in the table, don't print anything out.
    if not test.get("adds") and not test.get("subs"):
      return

    # Get table differences before and after the call on the stored procedure.
    o.write("<b>Changes to " + specs["table"] + "</b><br>\n")
    o.write("<pre class='results'>")
    (subs, adds) = get_diffs(test["subs"].split("\n"), \
      test["adds"].split("\n"))

    (sindex, aindex) = (0, 0)
    while sindex < len(subs):
      (diff_type, svalue) = subs[sindex]
      # A value that was removed.
      if diff_type == "remove":
        o.write("<font color='red'>- " + e(svalue) + "</font>\n")
        sindex += 1

      if aindex >= len(adds):
        continue
      (diff_type, avalue) = adds[aindex]
      # Matching values. Only print it out once.
      if diff_type == "":
        o.write("  " + e(svalue) + "\n")
        aindex += 1
        sindex += 1
      # A value that was added.
      elif diff_type == "add":
        o.write("<font color='green'>+ " + e(avalue) + "</font>\n")
        aindex += 1

    # Any remaining additions.
    while aindex < len(adds):
      (_, avalue) = adds[aindex]
      o.write("<font color='green'>+ " + e(avalue) + "</font>\n")
      aindex += 1

    o.write("</pre>")


  def function(self, test, specs):
    """
    Function: function
    ------------------
    Outputs the result of a function test. This includes the following:
      - Comparison of the actual results versus the expected results.
    """
    o = self.o
    # If the test failed, print out the differences.
    if not test["success"] and test.get("expected"):
      o.write("<b>Expected</b>\n")
      o.write("<pre>" + e(test["expected"]) + "</pre>\n")
      o.write("<b>Actual</b>\n")
      o.write("<pre>" + e(test["actual"]) + "</pre>\n")


# ---------------------------- Utility Functions ---------------------------- #

def e(text):
  """
  Function: e
  -----------
  Escapes text so it can be outputted as HTML.
  """
  return cgi.escape(text)


def get_diffs(lst1, lst2):
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
