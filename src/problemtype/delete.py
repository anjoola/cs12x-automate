from types import *

class Delete(ProblemType):
  """
  Class: Delete
  -------------
  Tests a delete statement to see if the student's query deletes the same rows
  as the solution query. Does this using transactions to ensure the database
  is not modified incorrectly.

  Compares the remaining rows in the tables in order to check if deletion was
  done correctly.
  """

  def grade_test(self, test, output):
    # Get the state of the table before the delete.
    table_sql = ('SELECT * FROM %s' + test['table'])
    before = self.db.execute_sql(table_sql)

    # Create a savepoint and run the student's delete statement. Make sure that
    # it IS a delete statement and is only a single statement (by checking that
    # after removing the trailing semicolon, there are no more).
    if not (self.response.sql.lower().find("delete") != -1 and \
            self.response.sql.strip().rstrip(";").find(";") == -1):
      # TODO output something if it not a delete statement
      return test["points"]

    self.db.savepoint('spt_delete')
    try:
      self.db.execute_sql(self.response.sql)
      actual = self.db.execute_sql(table_sql)

    except Exception as e:
      raise
    finally:
      self.db.rollback('spt_delete')
      # Make sure the rollback occurred properly.
      assert(len(before.results) == len(self.db.execute_sql(table_sql).results))

    # Run the solution delete statement.
    try:
      self.db.execute_sql(test["query"])
      expected = self.db.execute_sql(table_sql)

    except Exception as e:
      raise e
    finally:
      if test.get("rollback"):
        self.db.rollback('spt_delete')
        # Make sure the rollback occurred properly.
        assert(len(before.results) == len(self.db.execute_sql(table_sql).results))
      self.db.release('spt_delete')

    # Compare the remaining expected rows versus the actual. If the results are
    # not equal in the size, then it is automatically wrong. If the results are
    # not the same, then they are also wrong.
    if len(expected.results) != len(actual.results) or not \
       self.equals(set(expected.results), set(actual.results)):
      output["expected"] = list(set(before.results) - set(expected.results))
      output["actual"] = list(set(before.results) - set(actual.results))
      return test["points"]

    # Otherwise, their delete statement is correct.
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
