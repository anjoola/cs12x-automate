from problemtype import ProblemType

class Create(ProblemType):
  """
  Class: Create
  -------------
  Tests a create statement. TODO
  """

  def grade_test(self, test, output):
    output["success"] = "UNDETERMINED"
    # TODO create table statements are just printed.
    return 0


  def to_string(self, o, test, specs):
    pass
