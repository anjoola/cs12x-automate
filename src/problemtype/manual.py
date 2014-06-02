from types import ProblemType

class Manual(ProblemType):
  """
  Class: Manual
  -------------
  No automated grading is done. The TA must manually grade this problem. Simply
  indicate that manual grading is required.
  """

  def grade_test(self, test, output):
    output["success"] = "UNDETERMINED"
    return 0


  def output_test(self, o, test, specs):
    o.write("This problem should be <b>manually</b> graded.")
    pass
