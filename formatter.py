"""
Module: output.py
-----------------
Formats the output.
"""

from cStringIO import StringIO
import json

def format(output):
  """
  Funtion: format_md
  ------------------
  Formats the JSON output into markdown.

  output: The JSON string to output.
  """
  output = json.loads(output)
  o = StringIO()

  def format_lines(sep, lines):
    """
    Function: format_lines
    ----------------------
    Format lines in a nice way. Gets rid of extra spacing.
  
    lines: The lines to print and format.
    """
    return "\n" + sep + " " + ("\n" + sep + " ").join( \
      filter(None, [line.strip() for line in lines.split("\n")])) + "\n"


  def write(string):
    """
    Function: write
    ---------------
    Writes the markdown out to file. Markdown needs a lot of new lines!
    """
    o.write(string + "\n\n")


  # Loop through each student to print the results.
  for student in output["students"]:
    write("# -------------------------------------------")
    write("# [" + student["name"] + "]")

    # Loop through the student's files.
    for f in student["files"]:
      write("#### " + ("-" * 95))
      write("### " + f["filename"])

      # Any errors with the file.
      # Print out all errors that have occurred.
      if "errors" in f and len(f["errors"]) > 0:
        write("#### File Errors")
        for error in f["errors"]:
          write("* " + error)

      for problem in f["problems"]:
        write("---")
        errors = problem["errors"]
        num_points = str(problem["num_points"])
        write("#### Problem " + problem["num"] + " (" + num_points + " points)")

        # TODO always show these? only show if requested?
        if "comments" in problem and len(problem["comments"]) > 0:
          write("**Comments**\n")
          write(problem["comments"])
        if "submitted-results" in problem and \
          len(problem["submitted-results"]) > 0:
          write("**Submitted Results**\n")
          write(format_lines("   ", problem["submitted-results"]))
        write("**SQL**")
        write(format_lines("   ", problem["sql"]))

        # Go through the tests and print the failures.
        for test in problem["tests"]:
          if not test["success"] and "expected" in test:
            write("**`TEST FAILED`** (Lost " + str(test["points"]) + " points)")
            write(format_lines("   ", test["query"]))
            write("_Expected Results_")
            write(format_lines("   ", test["expected"]))
            write("_Actual Results_")
            write(format_lines("   ", test["actual"]))

        # Any errors with the problem.
        if len(errors) > 0:
          for error in errors:
            write("**Errors**")
            write("* "+ error)

        # Points received on this problem.
        got_points = str(problem["got_points"])
        if int(got_points) > 0:
          write("> ##### Points: " + got_points + " / " + num_points)
        else:
          write("> `Points: " + got_points + " / " + num_points + "`")


      write("\n### Total Points: " + str(f["got_points"]))

  return o.getvalue()
