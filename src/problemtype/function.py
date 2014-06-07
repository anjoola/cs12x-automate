from CONFIG import PRECISION
from types import ProblemType

class Function(ProblemType):
  """
  Class: Function
  ---------------
  Tests a function by calling it and comparing it with the expected output.
  """

  # Possible result types.
  RESULT_TYPES = ["boolean", "int", "float", "string"]

  def compare(self, expected, actual, result_type):
    """
    Function: compare
    -----------------
    Compares the expected results versus the actual result. Takes into account
    the result type. For example, if the result type is a float, then will
    accept integers and floats within a certain epsilon from the answer.

    expected: The expected result.
    actual: The actual result.
    result_type: The type of the result.
    """
    if result_type not in Function.RESULT_TYPES:
      err("Result type %s is not valid. Using string as default." % result_type)
      result_type = "string"

    if result_type == "boolean":
      actual = "true" if actual == "1" else "false"
    elif result_type == "int":
      expected = int(expected)
      actual = int(actual) if len(actual) > 0 else 0
    elif result_type == "float":
      factor = 10.0 ** PRECISION
      expected = int(float(expected) * factor) / factor
      actual = int((float(actual) if len(actual) > 0 else 0.0) * factor) / factor

    return expected == actual


  def grade_test(self, test, output):
    if test.get("run-query"):
      self.db.execute_sql(self.response.sql)

    result = self.db.execute_sql(test["query"], teardown=test.get("teardown"))

    if result.results and result.results[0]:
      result = str(result.results[0][0])
    else: result = ""

    output["actual"] = result if len(result) > 0 else "NULL"
    output["expected"] = test["expected"]

    # Should be all or nothing.
    if not self.compare(test["expected"], result, test["type"]):
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
