from errors import DatabaseError, QueryError
from sqltools import check_valid_query, find_valid_sql
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

  def check_view(self, sql):
    """
    Function: check_view
    --------------------
    Check to see if the student tried to create a view for the select statement.
    Returns (view_sql, select_sql), where view_sql is the SQL for the view
    and select_sql is the SQL for the SELECT statement. view_sql is blank if
    they did not create a view.
    """
    if (sql.upper().strip().startswith("CREATE VIEW") or
        sql.upper().strip().startswith("CREATE OR REPLACE VIEW")):
      view_sql = sql[0:sql.find(";") + 1]
      sql = sql[sql.find(";") + 1:]
      return (view_sql, sql)

    elif (sql.upper().strip().startswith("DROP VIEW") and
          ("CREATE VIEW" in sql.upper() or
           "CREATE OR REPLACE VIEW" in sql.upper())):
      view_sql = sql[0:sql.find(";", sql.upper().find("CREATE")) + 1]
      sql = sql[sql.find(";", sql.upper().find("CREATE")) + 1:]
      return (view_sql, sql)

    return ("", sql)


  def grade_test(self, test, output):
    success = True
    deductions = 0
    test_points = test["points"]

    # See if they suck and did a CREATE VIEW statement.
    (view_sql, sql) = self.check_view(self.response.sql)

    # Make sure the student did not submit a malicious query or malformed query.
    if not check_valid_query(sql, "select"):
      output["deductions"].append(QueryError.BAD_QUERY)
    sql = find_valid_sql(sql, "select")
    if sql is None:
      return test["points"]

    # Run the test query and the student's query.
    try:
      if len(view_sql.strip()) > 0:
        self.db.execute_sql(view_sql)
      expected = self.db.execute_sql(test["query"],
                                     test.get("setup"),
                                     test.get("teardown"))
      actual = self.db.execute_sql(sql,
                                   test.get("setup"),
                                   test.get("teardown"))
    except DatabaseError:
      raise

    # Compare the student's code to the results. May not need to check for
    # row order or column order.
    if not self.equals(expected,
                       actual,
                       test.get("ordered"),
                       test.get("column-order")):
      output["expected"] = expected.output
      output["actual"] = actual.output
      deductions = test_points

      # Check to see if they forgot to ORDER BY. Order the results and do a
      # comparison again.
      checked = False
      if test.get("ordered") and \
         self.equals(expected, actual, False, test.get("column-order")):
        deductions = 0
        output["deductions"].append(QueryError.ORDER_BY)
        checked = True

      # See if they chose the wrong column order. Order the results and do a
      # comparison again.
      if test.get("column-order") and \
         self.equals(expected, actual, test.get("ordered"), False):
        deductions = 0
        output["deductions"].append(QueryError.COLUMN_ORDER)
        checked = True

      # If they did both the wrong column order and wrong ORDER BY.
      if test.get("ordered") and test.get("column-order") and \
         self.equals(expected, actual) and not checked:
        deductions = 0
        output["deductions"].append(QueryError.ORDER_BY)
        output["deductions"].append(QueryError.COLUMN_ORDER)

      success = SuccessType.FAILURE

    # Check to see if they named aggregates.
    if test.get("rename"):
      for col in actual.col_names:
        if col.find("(") + col.find(")") != -2:
          output["deductions"].append(QueryError.RENAME_VALUE)
          success = SuccessType.FAILURE
          break

    # More or fewer columns included.
    if len(expected.col_names) != len(actual.col_names):
      output["deductions"].append(QueryError.WRONG_NUM_COLUMNS)

    # If the expected output is empty, then there is probably something wrong
    # with the state of the database.
    if len(expected.output) == 0:
      success = SuccessType.UNDETERMINED
    output["success"] = success
    return deductions


  def output_test(self, o, test, specs):
    # If the expected results was empty, result is undetermiend.
    if test["success"] == SuccessType.UNDETERMINED:
      o.write("<pre class='results'>")
      o.write("Expected output was empty. This may be an error with the " +
              "tool!")
      o.write("</pre>")

    # Test passed.
    elif test["success"] == SuccessType.SUCCESS or "expected" not in test:
      return

    # Expected and actual output for failed test.
    else:
      o.write("<pre class='results'>")
      self.generate_diffs(test["expected"].split("\n"),
                          test["actual"].split("\n"),
                          o)
      o.write("</pre>")
