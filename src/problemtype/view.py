from types import *

import re

# Disallowed keywords for updatable views.
DISALLOWED_KEYWORDS = [ \
  "SUM(", "MIN(", "MAX(", "COUNT(", \
  "DISTINCT ", "GROUP BY", " HAVING ", " UNION "
]

# Disallowed joins for updatable tables. Technically multi-table views can be
# updatable if the tables can be processed with the MERGE command, but there
# are no such tables in this class.
# Really, only "JOIN" is necessary, this is just for illustrative purposes.
DISALLOWED_JOINS = [ \
  "JOIN", "CROSS JOIN", "INNER JOIN", "STRAIGHT_JOIN", "NATURAL JOIN", \
  "LEFT JOIN", "LEFT OUTER JOIN", "NATURAL LEFT OUTER JOIN", \
  "RIGHT JOIN", "RIGHT OUTER JOIN", "NATURAL RIGHT OUTER JOIN", \
  "OUTER JOIN", "LEFT OUTER JOIN", "RIGHT OUTER JOIN"
]

# Regular expression matching a column and not a literal value.
COL_RE = re.compile('[A-Za-z_]([A-Za-z_0-9])*')

class View(ProblemType):
  """
  Class: View
  -----------
  Tests a create view statement. Runs the student's create view query, and
  selects from it to see if it contains the same rows as the solution query.
  """

  def check_updatable(self, test, output):
    """
    Function: check_updatable
    -------------------------
    Checks to see if view is updatable. Updatable views as defined in
    http://dev.mysql.com/doc/refman/5.7/en/view-updatability.html.

    returns: True if the view is updatable, False otherwise.
    """
    uppercase_sql = self.response.sql.upper()

    # Can't have certain keywords or joins.
    for keyword in DISALLOWED_KEYWORDS + DISALLOWED_JOINS:
      if keyword in uppercase_sql: return False

    # No subquery in the SELECT list. This means the index of the second SELECT
    # must either be -1 (there is no other one), or greater than the index of
    # the FROM clause.
    select_idx = uppercase_sql.find('SELECT', 1)
    from_idx = uppercase_sql.find('FROM')
    if select_idx != -1 and select_idx < from_idx: return False

    # Referring only to literal values. Get the columns being selected.
    select_clause = uppercase_sql[select_idx + len('SELECT') + 1:from_idx - 1]
    select_cols = select_clause.split(' ')
    for col in select_cols:
      if not COL_RE.match(col): return False

    # Multiple references to any column of the base table.
    if len(select_cols) != len(set(select_cols)): return False

    # No subquery in the WHERE clause that refers to a table in the FROM clause.
    if uppercase_sql.find('WHERE') != -1:
      # Isolate the FROM clause.
      start_idx = uppercase_sql.find('FROM') + len('FROM') + 1
      end_idx = uppercase_sql.find('WHERE') - 1
      from_clause = uppercase_sql[start_idx:end_idx].split(' ')

      # Isolate the WHERE clause. It may or may not be followed by a HAVING
      # clause, which must be removed.
      start_idx = uppercase_sql.rfind('WHERE') + len('WHERE') + 1
      end_idx = uppercase_sql.rfind('HAVING')
      end_idx = end_idx if end_idx != -1 else len(uppercase_sql) - 1
      where_clause = uppercase_sql[start_idx:end_idx].split(' ')

      # There is a table in the WHERE clause also in the FROM clause.
      if len(set(from_clause).intersection(set(where_clause))) != 0:
        return False

    return True


  def grade_test(self, test, output):
    # Get the rows that are expected.
    expected = self.db.run_query(test["select"])

    # Run the student's create view statement and select from that view to see
    # what is in the view.
    self.db.run_query(self.response.sql)
    actual = self.db.run_query("SELECT * FROM " + test["view"])

    # Check if the view is updatable, if necessary. If not, take points off.
    if test.get("updatable"):
      # TODO
      #points -= 0 if self.check_updatable(test, output) 1 otherwise
      self.check_updatable(test, output)

    # If the view does not contain the same rows as the solution select
    # statement, then their query is wrong.
    if len(expected.results) != len(actual.results) or not \
       self.equals(set(expected.results), set(actual.results)):
      # TODO check column order?
      output["expected"] = stringify(expected.results)
      output["actual"] = stringify(actual.results)
      return test["points"]

    # Otherwise, their CREATE VIEW statement is corret.
    output["success"] = True
    return 0


  def output_test(self, o, test, specs):
    # TODO
    pass
