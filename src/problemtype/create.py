from types import *

class Create(ProblemType):
  """
  Class: Create
  -------------
  Tests a create table statement. Checks for the following things:
  - TODO
  """

  def grade_test(self, test, output):
    # TODO parse the table name or specify in the specs?
    
    
    
    
    output["success"] = "UNDETERMINED"
    # TODO create table statements are just printed.
    
    output["a"] = "asf"
    return 0


  def output_test(self, o, test, specs):
    o.write(str(test["a"]))
    
