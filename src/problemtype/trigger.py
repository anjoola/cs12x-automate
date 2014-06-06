from types import ProblemType

class Trigger(ProblemType):
  """
  Class: Trigger
  --------------
  Tests a trigger statement.
  
  
  TODO
  """

  def grade_test(self, test, output):
    if test.get("run-query"):
      self.db.execute_sql(self.response.sql)

    # Start a transaction and run the test query.
    self.db.start_transaction()
    self.db.execute_sql(test["query"])

    exception = None
    try:
      self.db.execute_sql(self.response.sql, setup=test.get("setup"), \
                          teardown=test.get("teardown"))
      actual = self.db.execute_sql(test["actual"])
    except Exception as e:
      exception = e
    finally:
      self.db.rollback()

    self.db.start_transaction()
    expected = self.db.execute_sql(test["expected"])
    self.db.rollback()

    if exception: raise exception

    if len(expected.results) != len(actual.results) or not \
       self.equals(set(expected.results), set(actual.results)):
      output["expected"] = expected.output
      output["actual"] = actual.output
      return test["points"]

    # Otherwise, their insert statement is correct.
    output["success"] = True
    return 0


  def output_test(self, o, test, specs):
    # Don't output anything if they are successful.
    if test["success"] or "expected" not in test:
      return

    # Expected and actual output.
    o.write("<pre class='results'>")
    self.generate_diffs(test["expected"].split("\n"), \
                        test["actual"].split("\n"), o)
    o.write("</pre>")
