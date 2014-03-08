from problemtype import *

class Select(ProblemType):
  """
  Class: Select
  -------------
  Runs a test SELECT statement and compares it to the student's SELECT
    statement. Checks for the following things (if required):
      - Order of rows
      - Order of columns
      - Whether or not derived relations are renamed
  """

  def grade_test(self, test, output):
    success = True
    deductions = 0
    test_points = test["points"]

    expected = self.cache.get(self.db.run_query, test["query"], \
                              test.get("setup"), test.get("teardown"))
    try:
      actual = self.db.run_query(self.response.sql, test.get("setup"), \
                                 test.get("teardown"))
    except mysql.connector.errors.ProgrammingError as e:
      raise

    # If the results aren't equal in length, then they are automatically wrong.
    if len(expected.results) != len(actual.results):
      output["expected"] = expected.output
      output["actual"] = actual.output
      output["success"] = False
      return test_points

    # If we don't need to check that the results are ordered, then sort the
    # results for easier checking.
    if not test.get("ordered"):
      expected.results = set(expected.results)
      actual.results = set(actual.results)

    # If we don't need to check that the columns are ordered in the same way,
    # then sort each tuple for easier checking.
    if not test.get("column-order"):
      expected.results = [set(x) for x in expected.results]
      actual.results = [set(x) for x in actual.results]

    # Compare the student's code to the results.
    if not self.equals(expected.results, actual.results):
      output["expected"] = expected.output
      output["actual"] = actual.output
      deductions = test_points

      # Check to see if they forgot to ORDER BY.
      if test.get("ordered"):
        eresults = set(expected.results)
        aresults = set(actual.results)
        if aresults == eresults:
          deductions = 0
          output["deductions"].append("OrderBy")

      # See if they chose the wrong column order.
      if test.get("column-order"):
        eresults = [set(x) for x in expected.results]
        aresults = [set(x) for x in actual.results]
        if self.equals(eresults, aresults):
          deductions = 0
          output["deductions"].append("ColumnOrder")

      success = False

    # Check to see if they named aggregates.
    if test.get("rename"):
      for col in actual.col_names:
        if col.find("(") + col.find(")") != -2:
          output["deductions"].append("RenameValues")
          success = False
          break

    # More or fewer columns included.
    if len(expected.col_names) != len(actual.col_names):
      output["deductions"].append("WrongNumColumns")

    # TODO selecting something that is not grouped on

    output["success"] = success
    return deductions


  def output_test(self, o, test, specs):
    if test["success"] or "expected" not in test:
      return

    # Expected and actual output.
    o.write("<pre class='results'>")
    (ediff, adiff) = self.get_diffs(test["expected"].split("\n"), \
      test["actual"].split("\n"))

    (eindex, aindex) = (0, 0)
    space = " " * (len(ediff[eindex][1]) + 6)
    while eindex < len(ediff):
      (diff_type, evalue) = ediff[eindex]
      # An expected result not found in the actual results.
      if diff_type == "remove":
        o.write("<font color='red'>" + self.e(evalue) + "</font>\n")
        eindex += 1
        continue

      (diff_type, avalue) = adiff[aindex]
      # Matching actual and expected results.
      if diff_type == "":
        o.write(self.e(evalue + "      " + avalue) + "\n")
        aindex += 1
        eindex += 1
      # An actual result not found in the expected results.
      elif diff_type == "add":
        o.write(space + "<font color='red'>" + self.e(avalue) + "</font>\n")
        aindex += 1

    # Any remaining actual results.
    while aindex < len(adiff):
      (_, avalue) = adiff[aindex]
      o.write(space + "<font color='red'>" + self.e(avalue) + "</font>\n")
      aindex += 1

    o.write("</pre>")
