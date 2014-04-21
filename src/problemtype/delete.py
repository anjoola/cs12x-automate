from problemtype import *

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
    table_sql = "SELECT * FROM " + test["table"]
    before = self.db.run_query(table_sql)

    # Start a transaction and run the student's delete statement. Make sure that
    # it IS a delete statement and is only a single statement (by checking that
    # after removing the trailing semicolon, there are no more).
    if not (self.response.sql.lower().find("delete") != -1 and \
            self.response.sql.strip().rstrip(";").find(";") == -1):
      # TODO output something
      return test["points"]

    self.db.start_transaction()
    try:
      self.db.run_query(self.response.sql)
      actual = self.db.run_query(table_sql)

    except Exception as e:
      raise
    finally:
      self.db.rollback()
      # Make sure the rollback occurred properly.
      assert(len(before.results) == len(self.db.run_query(table_sql).results))

    # Start a transaction and run the solution delete statement.
    self.db.start_transaction()
    try:
      self.db.run_query(test["query"])
      expected = self.db.run_query(table_sql)

    except Exception as e:
      raise e
    finally:
      if test.get("rollback"):
        self.db.rollback()
        # Make sure the rollback occurred properly.
        assert(len(before.results) == len(self.db.run_query(table_sql).results))
      else:
        self.db.commit()

    # Compare the remaining expected rows versus the actual. If the results are
    # not equal in the size, then it is automatically wrong. If the results are
    # not the same, then they are also wrong.
    if len(expected.results) != len(actual.results) or not \
       self.equals(set(expected.results), set(actual.results)):
      output["expected"] = list(set(before.results) - set(expected.results))
      output["actual"] = list(set(before.results) - set(expected.results))
      return test["points"]

    # Otherwise, their delete statement is correct.
    output["success"] = True
    return 0


  def output_test(self, o, test, specs):
    # TODO
    pass
