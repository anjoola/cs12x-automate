from types import *

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
    table_sql = "SELECT * FROM " + test["table"]
    before = self.db.execute_sql(table_sql)

    # Create a savepoint and run the student's update statement. Make sure that
    # it IS an update statement and is only a single statement (by checking
    # that after removing the trailing semicolon, there are no more).
    if not (self.response.sql.lower().find("update") != -1 and \
            self.response.sql.strip().rstrip(";").find(";") == -1):
      # TODO output some error thing
      return test["points"]

    self.db.savepoint('spt_update')
    try:
      self.db.execute_sql(self.response.sql)
      actual = self.db.execute_sql(table_sql)

    except Exception as e: # TODO
      raise e
    finally:
      self.db.rollback('spt_update')
      # Make sure the rollback occurred properly.
      assert(len(before.results) == len(self.db.execute_sql(table_sql).results))
    
    # Run the solution update statement.
    try:
      self.db.execute_sql(test["query"])
      expected = self.db.execute_sql(table_sql)

    except Exception as e: # TODO
      raise e
    finally:
      if test.get("rollback"):
        self.db.rollback('spt_update')
        # Make sure the rollback occurred properly.
        assert(len(before.results) == len(self.db.execute_sql(table_sql).results))
      self.db.release('spt_update')

    # Compare the expected rows changed versus the actual. If the changes are
    # not equal in size, then it is automatically wrong. If the changes are not
    # the same, then they are also wrong.
    if len(expected.results) != len(actual.results) or not \
       self.equals(set(expected.results), set(actual.results)):
      output["expected"] = stringify(list(set(before.results) - \
                                     set(expected.results)))
      output["actual"] = stringify(list(set(before.results) - \
                                   set(actual.results)))
      return test["points"]

    # Otherwise, their update statement is correct.
    output["success"] = True
    return 0


  def output_test(self, o, test, specs):
     # Don't output anything if they are successful.
    if test["success"] or "expected" not in test:
      return

    # Expected and actual output.
    o.write("<pre class='results'>")
    self.generate_diffs(test["expected"], \
                        test["actual"], o)
    o.write("</pre>")
