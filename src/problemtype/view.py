import re

from errors import DatabaseError, QueryError
from models import Result
from sqltools import check_valid_query, find_valid_sql
from types import ProblemType

class View(ProblemType):
  """
  Class: View
  -----------
  Tests a create view statement. Runs the student's create view query, and
  selects from it to see if it contains the same rows as the solution query.
  """

  def check_updatable(self, viewname, output):
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


  def grade_test(self, test, output):
    # See if they actually put a CREATE VIEw statement.
    sql = self.response.sql
    if not (check_valid_query(sql, "create view") or
            check_valid_query(sql, "create or replace view")):
      output["deductions"].append(QueryError.BAD_QUERY)
      sql = find_valid_sql(sql, "create view") or \
            find_valid_sql(sql, "create or replace view")
      if sql is None:
        return test["points"]

    # Get the rows that are expected.
    expected = self.db.execute_sql(test['select'])

    # Run the student's create view statement and select from that view to see
    # what is in the view.
    viewname = test["view"]
    try:
      self.db.execute_sql(sql)
    except DatabaseError as e:
      raise e
    try:
      actual = self.db.execute_sql('SELECT * FROM %s' % viewname)
    except DatabaseError as e:
      # If an exception occurs, they must have not named the view correctly.
      # Attempt to interpret the view name.
      start_idx = self.response.sql.upper().find("CREATE VIEW ") + \
                  len("CREATE VIEW ")
      if start_idx == -1:
        start_idx = self.response.sql.upper().find("CREATE OR REPLACE VIEW ") +\
                    len("CREATE OR REPLACE VIEW ")

      end_idx = self.response.sql.upper().find(" AS")
      viewname = self.response.sql[start_idx:end_idx]
      try:
        actual = self.db.execute_sql('SELECT * FROM %s' % viewname)
      # Give up, some other error.
      except DatabaseError as e:
        raise e

      output["deductions"].append(QueryError.INCORRECT_VIEW_NAME)

    # Check if the view is updatable, if necessary. If not, take points off.
    if test.get('updatable') and not self.check_updatable(viewname, output):
      output["deductions"].append(QueryError.NOT_UPDATABLE)

    # If we don't need to check that the columsn are ordered in the same way,
    # then sort each tuple for easier checking.
    if not test.get("column-order"):
      expected.results = [sorted(x) for x in expected.results]
      actual.results = [sorted(x) for x in actual.results]

    # If the view does not contain the same rows as the solution select
    # statement, then their query is wrong.
    if (len(expected.results) != len(actual.results) or
        not self.equals(expected.results, actual.results)):
      # See if they chose the wrong column order.
      if test.get("column-order"):
        eresults = [sorted(x) for x in expected.results]
        aresults = [sorted(x) for x in actual.results]
        if eresults == aresults:
          deductions = 0
          output["deductions"].append(QueryError.COLUMN_ORDER)

      output['expected'] = expected.output
      output['actual'] = actual.output
      return test['points']

    # Otherwise, their CREATE VIEW statement is corret.
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
