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
    result = self.db.run_query(
      "SELECT is_updtable FROM information_schema.views WHERE "
      "table_name='%s'" % test['view']
    ).result
    print "asdfasdf", result
    return result == "YES"


  def grade_test(self, test, output):
    # Get the rows that are expected.
    expected = self.db.run_query(test['select'])

    # Run the student's create view statement and select from that view to see
    # what is in the view.
    self.db.run_query(self.response.sql)
    actual = self.db.run_query('SELECT * FROM %s' % test['view'])

    # Check if the view is updatable, if necessary. If not, take points off.
    if test.get('updatable'):
      # TODO
      #points -= 0 if self.check_updatable(test, output) 1 otherwise
      self.check_updatable(test, output)

    # If the view does not contain the same rows as the solution select
    # statement, then their query is wrong.
    if len(expected.results) != len(actual.results) or not \
       self.equals(set(expected.results), set(actual.results)):
      # TODO check column order?
      output['expected'] = stringify(expected.results)
      output['actual'] = stringify(actual.results)
      return test['points']

    # Otherwise, their CREATE VIEW statement is corret.
    output['success'] = True
    return 0


  def output_test(self, o, test, specs):
    # TODO
    pass
