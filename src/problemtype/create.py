from errors import DatabaseError
from types import ProblemType, SuccessType

class Create(ProblemType):
  """
  Class: Create
  -------------
  Tests a create table statement. Simply executes the CREATE TABLE statements
  to make sure they have the correct syntax.
  """

  def grade_test(self, test, output):
    if test.get("run-query"):
      try:
        self.db.execute_sql_list(self.sql_list)
      except DatabaseError:
        output["success"] = SuccessType.FAILURE
        raise

    output["success"] = SuccessType.UNDETERMINED
    return 0


  def output_test(self, o, test, specs):
    o.write("This problem should be <b>manually</b> graded.")
    if test["success"] == SuccessType.FAILURE:
      o.write("<br><i>SQL was invalid in some way. Check the errors below " +
              "more information.</i>")
    else:
      o.write(" There were no syntax errors.")
