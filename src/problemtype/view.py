from problemtype import *

class View(ProblemType):
  """
  Class: View
  -----------
  
  TODO: view should just select from the view and check to see if it's the same
  as the table the view is built off of
  
  need to parse their view name somehow
  replace "table" with their view name
  run "query" onl table and their view
  """

  def grade_test(self, test, output):
    # TODO

    
    
    
    
    
    
    
    
    
    table_sql = "SELECT * FROM " + test["table"]

    # Compare the expected rows inserted versus the actual.
    self.cache.get(self.db.run_query, test["query"], \
                   setup=test.get("setup"), teardown=test.get("teardown"))
    expected = self.db.run_query(table_sql)

    # Clean up the results of the test INSERT statement so the student's query
    # can be run.
    self.db.run_query("DELETE FROM " + test["table"])
    self.db.run_query(self.response.sql, setup=test.get("setup"), \
                      teardown=test.get("teardown"))
    actual = self.db.run_query(table_sql)

    # If the results are not equal in size, then they are wrong.
    if len(expected.results) != len(actual.results):
      return test["points"]

    # If the results are equal, then then the test passed.
    if self.equals(set(expected.results), set(actual.results)):
      output["success"] = True
      return 0

    else:
      return test["points"]


  def output_test(self, o, test, specs):
    # TODO
    pass
