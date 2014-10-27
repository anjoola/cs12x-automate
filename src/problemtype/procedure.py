from errors import QueryError
from types import ProblemType, SuccessType

class Procedure(ProblemType):
  """
  Class: Procedure
  ----------------------
  Tests a stored procedure by calling the procedure and checking the contents
  of the table before and after.
  """

  def grade_test(self, test, output):
    # Get the table before and after the stored procedure is called.
    table_sql = "SELECT * FROM " + test["table"]
    before = self.db.execute_sql(table_sql)

    # Setup queries.
    if test.get("setup"):
      self.db.execute_sql(test["setup"])
    if test.get("run-query"):
      try:
        valid_sql = sqltools.parse_func_and_proc(self.response.sql,
                                                 is_procedure=True)
      # If there is something wrong with their CREATE PROCEDURE statement.
      except:
        output["deductions"].append(QueryError.MALFORMD_CREATE_STATEMENT)
        return test["points"]
      self.db.execute_sql(self.response.sql)
    after = self.db.execute_sql(table_sql,
                                setup=test["query"], 
                                teardown=test.get("teardown"))

    output["before"] = before.output
    output["after"] = after.output
    output["success"] = SuccessType.UNDETERMINED
    return 0


  def output_test(self, o, test, specs):
    # Don't output results if there is nothing to output.
    if "before" not in test or "after" not in test:
      return

    o.write("<b>Changes to " + specs["table"] + "</b><br>\n")
    o.write("<pre class='results'>")

    (bdiff, adiff) = self.get_diffs(test["before"].split("\n"),
                                    test["after"].split("\n"))
    (bindex, aindex) = (0, 0)

    # Heading for before and after.
    before_first = "Before" if len(bdiff) == 0 else bdiff[0][1]
    o.write("<b>Before</b>" +
            " " * (len(before_first) - len("Before") + 6) + "<b>After</b>\n")
    space = " " * (max(len(before_first), len("Before")) + 6)

    while bindex < len(bdiff):
      (diff_type, evalue) = bdiff[bindex]
      # Something that was removed compared to before.
      if diff_type == "remove":
        o.write("<font color='red'>" + self.e(evalue) + "</font>\n")
        bindex += 1
        continue

      (diff_type, avalue) = adiff[aindex]
      # Unchanged row.
      if diff_type == "":
        o.write("<font color='gray'>" + self.e(evalue + "      " + avalue) +
                "</font>\n")
        aindex += 1
        bindex += 1
      # Something that was added compared to before.
      elif diff_type == "add":
        o.write(space + "<font color='green'>" + self.e(avalue) + "</font>\n")
        aindex += 1

    # Any remaining added rows.
    while aindex < len(adiff):
      (_, avalue) = adiff[aindex]
      o.write(space + "<font color='green'>" + self.e(avalue) + "</font>\n")
      aindex += 1

    o.write("</pre>")
