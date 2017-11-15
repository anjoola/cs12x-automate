from errors import DatabaseError
from types import ProblemType, SuccessType
from sqltools import parse_create

class Create(ProblemType):
  """
  Class: Create
  -------------
  Tests one or more create table statements.

   - If "run-query" is true then the statements are run to check for correct
     syntax.
   - If "source-file" is set to a filename then the specified SQL file is sourced
     after the commands are run, to verify that data can be loaded properly.
  to make sure they have the correct syntax.
  """

  def grade_test(self, test, output):
    if test.get("run-query"):
      try:
        self.db.execute_sql(parse_create(self.response.sql))
      except DatabaseError:
        output["success"] = SuccessType.FAILURE
        raise

      f = test.get("source-file")
      if f is not None:
        try:
          print("sourcing %s" % f),
          self.db.source_file(self.assignment, f)
        except DatabaseError:
          output["success"] = SuccessType.FAILURE
          raise

    output["success"] = SuccessType.UNDETERMINED
    return 0


  def output_test(self, o, test, specs):
    o.write("This problem should be <b>manually</b> graded.")
    if test["success"] == SuccessType.FAILURE:
      o.write("<br><i>SQL was invalid in some way. Check the errors below " +
              "more information.</i>")
    else:
      o.write(" There were no syntax errors.")
      if specs.get("run-query") and specs.get("source-file") is not None:
        o.write(" Successfully imported %s." % specs["source-file"])

