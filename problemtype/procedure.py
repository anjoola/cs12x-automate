from problemtype import *

class Procedure(ProblemType):
  """
  Class: Procedure
  ----------------------
  Tests a stored procedure by calling the procedure and checking the contents
    of the table before and after.
  """

  def grade_test(self, test, output):
    # Get the table before and after the stored procedure is called.
    table_sql = "SELECT * FROM " + test["table"]
    before = self.db.run_query(table_sql)

    # Setup queries.
    if test.get("run-query"): self.db.run_query(self.response.sql)
    if test.get("setup"): self.db.run_query(test["setup"])

    after = self.db.run_query(table_sql, setup=test["query"], 
      teardown=test.get("teardown"))

    subs = list(set(before.results) - set(after.results))
    output["subs"] = ("" if len(subs) == 0 else self.db.prettyprint(subs))
    adds = list(set(after.results) - set(before.results))
    output["adds"] = ("" if len(adds) == 0 else self.db.prettyprint(adds))

    output["success"] = "UNDETERMINED"
    # TODO how to handle deductions?
    return 0
