from cStringIO import StringIO
from CONFIG import TYPE_OUTPUTS

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
    elif test_type == "stored-procedure":
      return self.sp


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
      if test["success"]:
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
      TODO
    """
    # Expected and actual output.
    if not test["success"] and "expected" in test:
      o.write("<pre class='results'>")
      (ediff, adiff) = get_diffs(test["expected"].split("\n"), \
        test["actual"].split("\n"))

      (eindex, aindex) = (0, 0)
      space = " " * (len(ediff[eindex][1]) + 6)
      while eindex < len(ediff):
        (diff_type, evalue) = ediff[eindex]
        # An expected result not found in the actual results.
        if diff_type == "remove":
          o.write("<font color='red'>" + evalue + "</font>\n")
          eindex += 1
          continue

        (diff_type, avalue) = adiff[aindex]
        # Matching actual and expected results.
        if diff_type == "":
          o.write(evalue + "      " + avalue + "\n")
          aindex += 1
          eindex += 1
        # An actual result not found in the expected results.
        elif diff_type == "add":
          o.write(space + "<font color='red'>" + avalue + "</font>\n")
          aindex += 1

      # Any remaining actual results.
      while aindex < len(adiff):
        (_, avalue) = adiff[aindex]
        o.write(space + "<font color='red'>" + avalue + "</font>\n")
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


  def sp(self, test, specs):
    """
    Function: sp
    ------------
    Outputs the result of a stored procedure test. This includes the following:
    TODO
    """
    pass
