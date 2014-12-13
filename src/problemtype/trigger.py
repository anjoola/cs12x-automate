from errors import DatabaseError
from types import ProblemType, SuccessType

class Trigger(ProblemType):
  """
  Class: Trigger
  --------------
  Tests a trigger statement. Activates the trigger and checks to make sure that
  the trigger updated values in a particular table.
  """

  def grade_test(self, test, output):
    exception = None
    try:
      # Run setup and teardown queries if necessary.
      if test.get("setup"):
        self.db.execute_sql(test["setup"])
      if test.get("run-query"):
        self.db.execute_sql(self.response.sql)

      # Start a transaction and run the test query to trigger the trigger.
      self.db.start_transaction()
      self.db.execute_sql(test["query"])

      # Compare actual and expected results.
      actual = self.db.execute_sql(test["actual"])
      expected = self.db.execute_sql(test["expected"])
    except DatabaseError as e:
      exception = e
    finally:
      if test.get("teardown"):
        self.db.execute_sql(test["teardown"])
      self.db.rollback()

    # Raise any exceptions now if there was a problem with the student's query.
    if exception:
      raise exception

    # Compare the expected versus the actual results. If the results are not the
    # same, then they are wrong.
    if not self.equals(expected, actual):
      output["expected"] = expected.output
      output["actual"] = actual.output
      return test["points"]

    # Otherwise, their trigger worked.
    output["success"] = SuccessType.SUCCESS
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
