import datetime
import time

from sqltools import check_valid_query, find_valid_sql
from errors import DatabaseError, QueryError
from types import ProblemType, SuccessType

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
    sql = self.response.sql

    # Make sure the student did not submit a malicious query or malformed query.
    if not check_valid_query(sql, "select"):
      output["deductions"].append(QueryError.BAD_QUERY)
      sql = find_valid_sql(sql, "select")
      if sql is None:
        return test["points"]

    # Run the test query and the student's query.
    try:
      expected = self.db.execute_sql(test["query"], test.get("setup"), \
                                     test.get("teardown"), True)
      actual = self.db.execute_sql(sql, test.get("setup"), \
                                   test.get("teardown"), True)
    except DatabaseError:
      raise

    # If the results aren't equal in length, then they are automatically wrong.
    if len(expected.results) != len(actual.results):
      output["expected"] = expected.output
      output["actual"] = actual.output
      output["success"] = SuccessType.FAILURE
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
      expected.results = \
          [tuple(sorted([str(x) for x in row])) for row in expected.results]
      actual.results = \
          [tuple(sorted([str(x) for x in row])) for row in actual.results]

    # Compare the student's code to the results.
    if not self.equals(expected.results, actual.results):
      output["expected"] = expected.output
      output["actual"] = actual.output
      deductions = test_points

      # Check to see if they forgot to ORDER BY. Convert each row to a string
      # for easier comparison.
      if test.get("ordered"):
        eresults = sorted([str(x) for x in expected.results])
        aresults = sorted([str(x) for x in actual.results])
        if aresults == eresults:
          deductions = 0
          output["deductions"].append(QueryError.ORDER_BY)

      # See if they chose the wrong column order. Convert each column to a
      # string for easier comparison.
      if test.get("column-order"):
        eresults = \
            [tuple(sorted([str(x) for x in row])) for row in expected_results]
        aresults = \
            [tuple(sorted([str(x) for x in row])) for row in actual_results]
        if eresults == aresults:
          deductions = 0
          output["deductions"].append(QueryError.COLUMN_ORDER)

      success = False

    # Check to see if they named aggregates.
    if test.get("rename"):
      for col in actual.col_names:
        if col.find("(") + col.find(")") != -2:
          output["deductions"].append(QueryError.RENAME_VALUE)
          success = False
          break

    # More or fewer columns included.
    if len(expected.col_names) != len(actual.col_names):
      output["deductions"].append(QueryError.WRONG_NUM_COLUMNS)

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
