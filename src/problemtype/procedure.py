from errors import DatabaseError
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
    if test.get("run-query"): self.db.execute_sql(self.response.sql)
    if test.get("setup"): self.db.execute_sql(test["setup"])

    after = self.db.execute_sql(table_sql, setup=test["query"], 
      teardown=test.get("teardown"))

    subs = list(set(before.results) - set(after.results))
    output["subs"] = ("" if len(subs) == 0 else self.db.prettyprint(subs))
    adds = list(set(after.results) - set(before.results))
    output["adds"] = ("" if len(adds) == 0 else self.db.prettyprint(adds))

    output["success"] = SuccessType.UNDETERMINED
    # TODO how to handle deductions?
    return 0


  def output_test(self, o, test, specs):
    # If there are no changes in the table, don't print anything out.
    if not test.get("adds") and not test.get("subs"):
      return

    # Get table differences before and after the call on the stored procedure.
    o.write("<b>Changes to " + specs["table"] + "</b><br>\n")
    o.write("<pre class='results'>")
    (subs, adds) = self.get_diffs(test["subs"].split("\n"), \
      test["adds"].split("\n"))

    (sindex, aindex) = (0, 0)
    while sindex < len(subs):
      (diff_type, svalue) = subs[sindex]
      # A value that was removed.
      if diff_type == "remove":
        o.write("<font color='red'>- " + self.e(svalue) + "</font>\n")
        sindex += 1

      if aindex >= len(adds):
        break
      (diff_type, avalue) = adds[aindex]
      # Matching values. Only print it out once.
      if diff_type == "":
        o.write("  " + self.e(svalue) + "\n")
        aindex += 1
        sindex += 1
      # A value that was added.
      elif diff_type == "add":
        o.write("<font color='green'>+ " + self.e(avalue) + "</font>\n")
        aindex += 1

    # Any remaning subtractions.
    while sindex < len(subs):
      (_, svalue) = subs[sindex]
      o.write("<font color='red'>+ " + self.e(svalue) + "</font>\n")
      sindex += 1

    # Any remaining additions.
    while aindex < len(adds):
      (_, avalue) = adds[aindex]
      o.write("<font color='green'>+ " + self.e(avalue) + "</font>\n")
      aindex += 1

    o.write("</pre>")
