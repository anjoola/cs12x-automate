from problemtype import *

class Insert(ProblemType):
  """
  Class: Insert
  -------------
  Tests an insert statement and sees if the student's query produces the
  same diff as the solution query. Does this using transactions to ensure the
  database is not modified incorrectly.
  """
  def grade_test(self, test, output):
    # Get the state of the table before the insert.
    table_sql = "SELECT * FROM " + test["table"]
    before = self.db.run_query(table_sql)

    # Start a transaction and run the student's insert query. Assert that it
    # IS an insert statement and is only a single statement (by checking that
    # after removing the trailing semicolon, there are no more).
    assert(self.response.sql.lower().find("insert") and \
           self.response.sql.strip().rstrip(";").find(";") == 0)
    self.db.start_transaction()
    self.db.run_query(self.response.sql, setup=test.get("setup"), \
                      teardown=test.get("teardown"))
    actual = self.db.run_query(table_sql)
    self.db.rollback()

    # Make sure the rollback occurred properly.
    assert(len(before.results) == len(self.db.run_query(table_sql).results))

    # Start a transaction and run the solution insert statement.
    self.db.start_transaction()
    self.cache.get(self.db.run_query, test["query"], \
                   setup=test.get("setup"), teardown=test.get("teardown"))
    expected = self.db.run_query(table_sql)

    # Compare the results of the test insert versus the actual. If the results
    # are not equal in size, then it is automatically wrong. If the results are
    # not the same, then they are also wrong.
    if len(expected.results) != len(actual.results) or not \
       self.equals(set(expected.results), set(actual.results)):
      output["expected"] = list(set(before.results) - set(expected.results))
      output["actual"] = list(set(before.results) - set(expected.results))
      return test["points"]

    # Otherwise, their insert statement is correct.
    output["success"] = True
    return 0


  def output_test(self, o, test, specs):
    # TODO
    pass
