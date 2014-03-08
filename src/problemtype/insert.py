from problemtype import *

class Insert(ProblemType):
  """
  Class: Insert
  -------------
  Tests an insert statement and sees if the student's query produces the
  same diff as the solution query.
  """

  def grade_test(self, test, output):
    table_sql = "SELECT * FROM " + test["table"]

    # Compare the expected rows inserted versus the actual.
    self.cache.get(self.db.run_query, test["query"], \
                   setup=test.get("setup"), teardown=test.get("teardown"))
    expected = self.db.run_query(table_sql)

    # Clean up the results of the test INSERT statement so the student's query
    # can be run.
    self.db.run_query("DELETE FROM " + test["table"])
    self.db.run_query(self.response.sql, setup=test.get("setup"), \
                      teardown=test.get("teardown"))
    actual = self.db.run_query(table_sql)

    # If the results are not equal in size, then they are wrong.
    if len(expected.results) != len(actual.results):
      return test["points"]

    # If the results are equal, then then the test passed.
    if self.equals(set(expected.results), set(actual.results)):
      output["success"] = True
      return 0

    else:
      return test["points"]


  def output_test(self, o, test, specs):
    pass
