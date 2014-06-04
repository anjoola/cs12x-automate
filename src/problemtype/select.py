from types import *

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

    # Run the test query and the student's query.
    expected = self.db.execute_sql(test["query"], test.get("setup"), \
                                   test.get("teardown"), True)
    try:
      actual = self.db.execute_sql(self.response.sql, test.get("setup"), \
                                   test.get("teardown"), True)
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
    expected_results = expected.results
    actual_results = actual.results
    if not test.get("ordered"):
      expected.results = sorted(expected.results)
      actual.results = sorted(actual.results)

    # If we don't need to check that the columns are ordered in the same way,
    # then sort each tuple for easier checking.
    if not test.get("column-order"):
      expected.results = [sorted(x) for x in expected.results]
      actual.results = [sorted(x) for x in actual.results]

    # Compare the student's code to the results.
    if not self.equals(expected.results, actual.results):
      output["expected"] = expected.output
      output["actual"] = actual.output
      deductions = test_points

      # Check to see if they forgot to ORDER BY.
      if test.get("ordered"):
        eresults = sorted(expected.results)
        aresults = sorted(actual.results)
        if aresults == eresults:
          deductions = 0
          output["deductions"].append("OrderByError")

      # See if they chose the wrong column order.
      if test.get("column-order"):
        eresults = [sorted(x) for x in expected_results]
        aresults = [sorted(x) for x in actual_results]
        if eresults == aresults:
          deductions = 1 # TODO deductions?
          output["deductions"].append("ColumnOrderError")

      success = False

    # Check to see if they named aggregates.
    if test.get("rename"):
      for col in actual.col_names:
        if col.find("(") + col.find(")") != -2:
          output["deductions"].append("RenameValueError")
          success = False
          break

    # More or fewer columns included.
    if len(expected.col_names) != len(actual.col_names):
      output["deductions"].append("WrongNumColumnsError")

    # TODO selecting something that is not grouped on

    output["success"] = success
    return deductions


  def output_test(self, o, test, specs):
    # Don't output anything if they are successful.
    if test["success"] or "expected" not in test:
      return

    # Expected and actual output.
    o.write("<pre class='results'>")
    self.generate_diffs(test["expected"].split("\n"), \
                        test["actual"].split("\n"), o)
    o.write("</pre>")
