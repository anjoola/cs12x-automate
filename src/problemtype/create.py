from types import ProblemType

class Create(ProblemType):
  """
  Class: Create
  -------------
  Tests a create table statement. Simply executes the CREATE TABLE statements
  to make sure they have the correct syntax. Outputs the SQL in a nice format
  that is easy to read for the TAs.
  """

  def grade_test(self, test, output):
    output["success"] = "UNDETERMINED"
    return 0


  def output_test(self, o, test, specs):
    pass
    # TODO
