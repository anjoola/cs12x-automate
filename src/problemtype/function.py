from CONFIG import PRECISION
from errors import QueryError
from types import ProblemType, SuccessType

import sqltools

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
      try:
        valid_sql = sqltools.parse_func_and_proc(self.response.sql)
      # If there is something wrong with their CREATE FUNCTION statement.
      except:
        output["deductions"].append(QueryError.MALFORMED_CREATE_STATEMENT)
        return test["points"]
      self.db.execute_sql(valid_sql)
    result = self.db.execute_sql(test["query"], teardown=test.get("teardown"))

    if result.results and result.results[0]:
      result = str(result.results[0][0])
    else:
      result = ""

    output["actual"] = result if len(result) > 0 else "NULL"
    output["expected"] = test["expected"]

    # Should be all or nothing.
    if not self.compare(test["expected"], result, test["type"]):
      output["success"] = SuccessType.FAILURE
      return test["points"]
    else:
      output["success"] = SuccessType.SUCCESS
      return 0


  def output_test(self, o, test, specs):
    # If the test failed, print out the differences.
    if not test["success"] and test.get("expected"):
      expected = self.e(test["expected"])
      actual = self.e(test["actual"])
      diff = len(expected) - len("Expected")

      o.write("<pre class='results'>\n")
      o.write("<b>Expected</b>" +
              (" " * ((diff if diff > 0 else 0) + 6)) + "<b>Actual</b>")

      o.write("<br>" + expected +
              (" " * ((0 if diff > 0 else abs(diff)) + 6)) + actual + "\n")
      o.write("</pre>")
