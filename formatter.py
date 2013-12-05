"""
Module: formatter.py
--------------------
Formats the output.
"""

import cgi
from cStringIO import StringIO
from CONFIG import TYPE_OUTPUTS
import json
from testoutput import TestOutput
import os

def e(text):
  """
  Function: esc
  -------------
  Escapes text so it can be outputted as HTML.
  """
  return cgi.escape(text.encode('ascii', 'xmlcharrefreplace'))


def html(output, specs):
  """
  Function: html
  --------------
  Formats the JSON output into HTML.

  output: The graded JSON output.
  specs: The specs for the assignment.
  returns: A string containing the HTML.
  """
  output = json.loads(output)
  o = StringIO()
  o.write("<link rel='stylesheet' type='text/css' href='style/css.css'>\n")
  o.write("<script type='text/javascript' src='style/javascript.js'></script>")
  o.write("\n<input type='hidden' id='assignment' value='" + \
    specs["assignment"] + "'>")

  # Print out the list of students to the list. Finds this by searching the
  # directory (since we may run the automation tool mutliple times on different
  # sets of students).
  o.write("<div id='left'>\n<div id='students'>Students</div><br>")
  found_students = []
  for f in os.listdir(specs["assignment"] + "/_results/files/"):
    student = f.split("-")[0]
    if student not in found_students:
      found_students.append(student)
      o.write("<a onclick='changeStudent(\"" + student + "\")'>" + student + \
        "</a><br>")
  o.write("</div>")

  # Graded output and actual files.
  first_student = output["students"][0]["name"]
  first_file = output["files"][0]
  o.write("<div draggable='true' class='resizable' id='middle'>\n" + \
    "<div class='title' id='name'>" + first_student + "</div>\n")

  # Graded files.
  o.write("<div class='links'>\n")
  for i in range(len(output["files"])):
    name = output["files"][i]
    if i == 0:
      o.write("<div class='label-active label' ")
    else:
      o.write("<div class='label' ")
    o.write("onclick='changeGradedFile(this, \"" + name + "\")'>" + name + \
      "</div>\n")
  o.write("</div>\n<iframe src='files/" + first_student + "-" + first_file + \
    ".html' name='middle' id='iframe-middle'></iframe></div>\n\n")

  # Raw files.
  o.write("<div id='right' draggable='true' class='resizable'>\n")
  o.write("<div class='title'>Raw Files</div>\n")
  o.write("<div class='links'>\n")
  for i in range(len(output["files"])):
    name = output["files"][i]
    if i == 0:
      o.write("<div class='label-active label' ")
    else:
      o.write("<div class='label' ")
    o.write("onclick='changeRawFile(this, \"" + name + "\")'>" + name + \
      "</div>\n")
  # Get the first file for the first student.
  f = "../students/" + first_student + "-" + specs["assignment"] + "/" + \
    first_file
  o.write("</div>\n<iframe src='" + f + "' name='right' " + \
    "id='iframe-right'></iframe></div>")

  return o.getvalue()


def html_student(student, specs):
  """
  Function: html_student
  ----------------------
  Outputs the graded output for a particular student. Each student's output
  gets written to its own file.

  student: The student's JSON output.
  specs: The specs for the assignment.
  """
  # Create output per student, per file. Files are named student-file.html.
  for f in student["files"]:
    o = StringIO()
    o.write("<link rel='stylesheet' type='text/css' href='../style/css.css'>\n")
    o.write("<script type='text/javascript' src='../style/javascript.js'>" + \
      "</script>\n")
    o.write("<html class='student-page'>")

    # Print out all errors that have occurred with the file.
    if f.get("errors"):
      o.write("<h2>File Errors</h2><ul>")
      for error in f["errors"]:
        o.write("<li>" + error + "</li>")
      o.write("</ul>")

    # Loop through all the problems.
    for (i, problem) in enumerate(f["problems"]):
      problem_specs = specs[f["filename"]][i]
      o.write("<a onclick='toggle(\"" + problem["num"] + "\")'><h3>Problem " + \
        problem["num"] + " (" + str(problem["got_points"]) + "/" + \
        str(problem_specs["points"]) + " Points)</h3></a>\n")

      o.write("<div id=\"" + problem["num"] + "\" style='display:none'>")
      # If the student did not submit an answer for this problem.
      if problem.get("notexist"):
        o.write("<i>Did not submit a response for this question!</i>")
        o.write("</div>")
        continue

      # Print out comments and submitted results if the specs ask for it.
      if problem_specs.get("comments") and problem:
        o.write("<b>Comments</b>")
        if not problem["comments"]:
          o.write("<br><i>No comments provided...</i><br>\n")
        else:
          o.write("<pre>" + problem["comments"] + "</pre>")
      if problem_specs.get("submitted-results"):
        o.write("<b>Submitted Results</b>")
        o.write("<pre>" + problem["submitted-results"] + "</pre>")
      o.write("<b>SQL</b>")
      o.write("<pre>" + problem["sql"] + "</pre>")

      # Test output.
      test_output = TestOutput(o)
      test_output.output(problem["tests"], problem_specs["tests"])

      # Any errors that have occurred.
      errors = problem["errors"]
      if len(errors) > 0:
        o.write("\n<b>Errors</b>\n<br><ul>")
        for error in errors:
          o.write("<li>" + error + "</li>\n")
        o.write("</ul>")

      o.write("</div>")

    o.write("<h2>Total: " + str(f["got_points"]) + " Points</h2>")
    o.write("<br><br></html>")

    filename = student["name"] + "-" + f["filename"] + ".html"
    output = open(specs["assignment"] + "/_results/files/" + filename, "w")
    output.write(o.getvalue())
    output.close()


def markdown(output, specs):
  """
  Function: markdown
  ------------------
  Formats the JSON output into markdown.

  output: The graded JSON output.
  specs: The specs for the assignment.
  returns: The string containing the markdown.
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

      # Print out all errors that have occurred with the file.
      if f.get("errors"):
        write("#### File Errors")
        for error in f["errors"]:
          write("* " + error)

      # Loop through all the problems.
      for (i, problem) in enumerate(f["problems"]):
        write("---")
        problem_specs = specs[f["filename"]][i]
        errors = problem["errors"]
        num_points = str(problem_specs["points"])
        write("#### Problem " + problem["num"] + " (" + num_points + " points)")

        # Print out the comments and submitted results if the specs ask for it.
        if problem_specs.get("comments"):
          write("**Comments**\n")
          write(problem["comments"])
        if problem_specs.get("submitted-results"):
          write("**Submitted Results**\n")
          write(format_lines("   ", problem["submitted-results"]))
        write("**SQL**")
        write(format_lines("   ", problem["sql"]))

        # Go through the tests and print the failures. Only print out the test
        # if it is one to output for (see TYPE_OUTPUTS in the CONFIG file).
        for (j, test) in enumerate(problem["tests"]):
          test_specs = problem_specs["tests"][j]
          if test.get("type") in TYPE_OUTPUTS and not test["success"] and \
            "expected" in test:
            write("**`TEST FAILED`** (Lost " + str(test_specs["points"]) + \
              " points)")
            write(format_lines("   ", test_specs["query"]))
            write("_Expected Results_")
            write(format_lines("   ", test["expected"]))
            write("_Actual Results_")
            write(format_lines("   ", test["actual"]))

        # Any errors with the problem.
        if len(errors) > 0:
          write("**Errors**")
          for error in errors:
            write("* "+ error)

        # Points received on this problem.
        got_points = str(problem["got_points"])
        if int(got_points) > 0:
          write("> ##### Points: " + got_points + " / " + num_points)
        else:
          write("> `Points: " + got_points + " / " + num_points + "`")

      write("\n### Total Points: " + str(f["got_points"]))

  return o.getvalue()
