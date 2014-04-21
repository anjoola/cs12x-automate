from problemtype import ProblemType

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
    before = self.db.run_query(table_sql)

    # Start a transaction and run the student's update statement. Make sure that
    # it IS an update statement and is only a single statement (by checking
    # that after removing the trailing semicolon, there are no more).
    if not (self.response.sql.lower().find("update") != -1 and \
            self.response.sql.strip().rstrip(";").find(";") == -1):
      # TODO output some error thing
      return test["points"]

    self.db.start_transaction()
    try:
      actual = self.db.run_query(self.response.sql)

    except Exception as e:
      raise e
    finally:
      self.db.rollback()
      # Make sure the rollback occurred properly.
      assert(len(before.results) == len(self.db.run_query(table_sql).results))
    
    # Start a transaction and run the solution update statement.
    self.db.start_transaction()
    try:
      self.db_run_query(test["query"])
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

    # Compare the expected rows changed versus the actual. If the changes are
    # not equal in size, then it is automatically wrong. If the changes are not
    # the same, then they are also wrong.
    if len(expected.results) != len(actual.results) or not \
       self.equals(set(expected.results), set(actual.results)):
      output["expected"] = list(set(before.results) - set(expected.results))
      output["actual"] = list(set(before.results) - set(actual.results))
      return test["points"]

    # Otherwise, their update statement is correct.
    output["success"] = True
    return 0


  def output_test(self, o, test, specs):
    # TODO
    pass
