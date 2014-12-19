from errors import (
  add,
  DatabaseError,
  ParseError,
  QueryError
)
from types import ProblemType

class View(ProblemType):
  """
  Class: View
  -----------
  Tests a create view statement. Runs the student's create view query, and
  selects from it to see if it contains the same rows as the solution query.
  """

  def check_updatable(self, viewname):
    """
    Function: check_updatable
    -------------------------
    Checks to see if view is updatable. Updatable views as defined in
    http://dev.mysql.com/doc/refman/5.7/en/view-updatability.html.

    returns: True if the view is updatable, False otherwise.
    """
    result = self.db.execute_sql(
      "SELECT is_updatable FROM information_schema.views WHERE "
      "table_name='%s'" % viewname
    ).results
    return result[0][0] == "YES"


  def get_view_name(self):
    """
    Function: get_view_name
    -----------------------
    Gets the name of a view from the CREATE VIEW statement.
    """
    sql = self.response.sql

    start_idx = sql.upper().find("CREATE VIEW ") + len("CREATE VIEW ")
    if start_idx - len("CREATE VIEW ") == -1:
      start_idx = sql.upper().find("CREATE OR REPLACE VIEW ") + \
                  len("CREATE OR REPLACE VIEW ")

    end_idx = sql.upper().find(" AS")

    # Could not get their view name. Most likely a malformed CREATE VIEW.
    if start_idx - len("CREATE OR REPLACE VIEW ") == -1 or end_idx == -1:
      raise ParseError
    return sql[start_idx:end_idx]


  def grade_test(self, test, output):
    # Get the rows that are expected.
    expected = self.db.execute_sql(test['select'])

    # Run the student's create view statement and select from that view to see
    # what is in the view.
    viewname = test["view"]
    self.db.execute_sql_list(self.sql_list)
    try:
      actual = self.db.execute_sql('SELECT * FROM %s' % viewname)
    except DatabaseError:
      try:
        # If an exception occurs, they must have not named the view correctly.
        # Attempt to interpret the view name.
        viewname = self.get_view_name()
        actual = self.db.execute_sql('SELECT * FROM %s' % viewname)

      # Could not interpret view name.
      except ParseError as e:
        add(self.output["errors"], e)
        return test['points']

      # Give up, some other error.
      except DatabaseError as e:
        raise e

      output["deductions"].append(QueryError.INCORRECT_VIEW_NAME)

    # Check if the view is updatable, if necessary. If not, take points off.
    if test.get('updatable') and not self.check_updatable(viewname):
      output["deductions"].append(QueryError.NOT_UPDATABLE)

    # If the view does not contain the same rows as the solution select
    # statement, then their query is wrong.
    if not self.equals(expected, actual, False, test.get("column-order")):
      # See if they chose the wrong column order. Check by ignoring the column
      # order of the results.
      if test.get("column-order") and \
         self.equals(expected, actual, True, False):
        output["deductions"].append(QueryError.COLUMN_ORDER)

      output['expected'] = expected.output
      output['actual'] = actual.output
      return test['points']

    # Otherwise, their CREATE VIEW statement is correct.
    output['success'] = True
    return 0


  def output_test(self, o, test, specs):
    # Don't output anything if they are successful.
    if test["success"] or "expected" not in test:
      return

    # Expected and actual output.
    o.write("<pre class='results'>")
    self.generate_diffs(test["expected"].split("\n"),
                        test["actual"].split("\n"),
                        o)
    o.write("</pre>")
