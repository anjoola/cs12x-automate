from problemtype import ProblemType

class Trigger(ProblemType):
  """
  Class: Trigger
  --------------
  Tests a trigger statement.
  
  
  TODO
  """

  def grade_test(self, test, output):
    output["success"] = "UNDETERMINED"
    # TODO create table statements are just printed.
    return 0


  def output_test(self, o, test, specs):
    pass
