from types import *

class Function(ProblemType):
  """
  Class: Function
  ---------------
  Tests a function by calling it and comparing it with the expected output.
  """

  def grade_test(self, test, output):
    if test.get("run-query"):
      self.db.run_query(self.response.sql)
    result = self.db.run_query(test["query"], teardown=test.get("teardown"))

    if result.results and result.results[0]:
      result = str(result.results[0][0])
    else: result = ""

    output["actual"] = result
    output["expected"] = test["expected"]

    # Should be all or nothing.
    if test["expected"] != result:
      output["success"] = False
      return test["points"]
    else:
      output["success"] = True
      return 0


  def output_test(self, o, test, specs):
    # If the test failed, print out the differences.
    if not test["success"] and test.get("expected"):
      o.write("<b>Expected</b>\n")
      o.write("<pre>" + self.e(test["expected"]) + "</pre>\n")
      o.write("<b>Actual</b>\n")
      o.write("<pre>" + self.e(test["actual"]) + "</pre>\n")
