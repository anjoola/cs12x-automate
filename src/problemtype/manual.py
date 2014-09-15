from errors import DatabaseError
from types import ProblemType, SuccessType

class Manual(ProblemType):
  """
  Class: Manual
  -------------
  No automated grading is done. The TA must manually grade this problem. Simply
  indicate that manual grading is required. Runs the query if needed.
  """

  def grade_test(self, test, output):
    output["success"] = SuccessType.UNDETERMINED

    if test.get("run-query"):
      try:
        self.db.execute_sql(self.response.sql)
      except DatabaseError:
        raise

    return 0


  def output_test(self, o, test, specs):
    o.write("This problem should be <b>manually</b> graded.")
