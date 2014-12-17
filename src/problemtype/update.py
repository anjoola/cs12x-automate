from errors import DatabaseError, QueryError
from types import ProblemType, SuccessType

class Update(ProblemType):
  """
  Class: Update
  -------------
  Tests an update statement. Checks to see the changed rows after running the
  student's query and compares to the changed rows by the solution query.
  Does this using transactions to ensure the database is not modified
  incorrectly.
  """

  def grade_test(self, test, output):
    # Get the state of the table before the update.
    table_sql = "SELECT " + \
                (", ".join(test["columns"]) if test.get("columns") else "*") + \
                " FROM " + test["table"]
    before = self.db.execute_sql(table_sql)

    # Start a transaction in order to rollback if this is a self-contained
    # UPDATE test.
    self.db.start_transaction()

    # Create a savepoint and run the student's update statement.
    exception = None
    self.db.savepoint('spt_update')
    try:
      self.db.execute_sql_list(self.sql_list)
      actual = self.db.execute_sql(table_sql)
    except DatabaseError as e:
      exception = e
    finally:
      # Rollback to the savepoint and make sure it occurred properly.
      self.db.rollback('spt_update')
      assert before.output == self.db.execute_sql(table_sql).output

    # Run the solution update statement.
    self.db.execute_sql(test["query"])
    expected = self.db.execute_sql(table_sql)

    # A self-contained UPDATE. Make sure the rollback occurred properly.
    if test.get("rollback"):
      self.db.rollback()
      assert before.output == self.db.execute_sql(table_sql).output

    # Otherwise, release the savepoint.
    else:
      self.db.release('spt_update')
      self.db.commit()

    # Raise the exception if it occurred.
    if exception:
      raise exception

    # Compare the expected rows changed versus the actual.
    if not self.equals(expected, actual):
      output["expected"] = expected.subtract(before).output
      output["actual"] = actual.subtract(before).output
      return test["points"]

    # Otherwise, their update statement is correct.
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
