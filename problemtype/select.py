from problemtype import *

class Select(ProblemType):
  """
  Class: Select
  -------------
  Runs a test SELECT statement and compares it to the student's SELECT
    statement. Possibly checks for the following things:
      - Order of rows
      - Order of columns
      - Whether or not derived relations are renamed
  """

  def grade_test(self, test, output):
    success = True
    deductions = 0
    test_points = test["points"]

    # TODO make sure they aren't doing SQL injection
    expected = self.cache.get(self.db.run_query, test["query"], \
      setup=test.get("setup"), teardown=test.get("teardown"))
    try:
      actual = self.db.run_query(self.response.sql, setup=test.get("setup"), \
        teardown=test.get("teardown"))
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
          output["deductions"].append("orderby") # TODO

      # See if they chose the wrong column order.
      if test.get("column-order"):
        eresults = [set(x) for x in expected.results]
        aresults = [set(x) for x in actual.results]
        if self.equals(eresults, aresults):
          deductions = 0
          output["deductions"].append("columnorder") # TODO

      success = False

    # Check to see if they named aggregates.
    # TODO check for other things? must contain a certain word in col name?
    if test.get("rename"):
      for col in actual.col_names:
        if col.find("(") + col.find(")") != -2:
          output["deductions"].append("renamecolumns") # TODO
          success = False
          break

    # TODO more or fewer columns?
    output["success"] = success
    return deductions
