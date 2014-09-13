"""
Module: formatter
-----------------
Formats the graded output into HTML.
"""

import cgi
import json
import os
import shutil
from cStringIO import StringIO

from CONFIG import (
  ASSIGNMENT_DIR,
  FILE_DIR,
  RESULT_DIR,
  STYLE_DIR,
  STYLE_DIR_BASE
)
from problemtype import PROBLEM_TYPES

def create_path(assignment):
  """
  Function: create_path
  ---------------------
  Create the path for the result files if it doesn't exist already, and add the
  necessary files for the automation output.

  assignment: The assignment that is currently being graded.
  """
  # Copy necessary stylesheets and create results folder if it doesn't exist.
  path = ASSIGNMENT_DIR + assignment + "/"
  if not os.path.exists(path + RESULT_DIR):
    os.mkdir(path + RESULT_DIR)
    os.mkdir(path + RESULT_DIR + FILE_DIR)
    os.mkdir(path + RESULT_DIR + STYLE_DIR_BASE)

    # Copy over stylesheets and Javascript files.
    for f in os.listdir(STYLE_DIR):
      shutil.copy(STYLE_DIR + f, path + RESULT_DIR + STYLE_DIR_BASE + f)


def e(text):
  """
  Function: e
  -----------
  Escapes text so it can be outputted as HTML.
  """
  return cgi.escape(text.encode('ascii', 'xmlcharrefreplace'))


def format(output, specs):
  """
  Function: format
  ----------------
  Formats the JSON output into HTML. This is the formatting for the main page.

  output: The graded JSON output.
  specs: The specs for the assignment.
  returns: A string containing the HTML.
  """
  # Create the necessary directories if needed.
  create_path(specs["assignment"])

  o = StringIO()
  o.write("<head><title>CS 121 Automation</title></head>")
  o.write("<link rel='stylesheet' type='text/css' href='style/css.css'>\n")
  o.write("<script type='text/javascript' src='style/javascript.js'></script>")
  o.write("\n<input type='hidden' id='assignment' value='" + \
          specs["assignment"] + "'>\n")

  o.write("<div id='container'>\n")

  # Print out the list of students to the list. Finds this by searching the
  # directory (since we may run the automation tool mutliple times on different
  # sets of students).
  o.write("<div id='list'><div id='list-inner'>\n" +
          "<div id='students'>Students</div><br>\n")
  found_students = []
  for f in os.listdir(ASSIGNMENT_DIR + specs["assignment"] + "/" + \
                      RESULT_DIR + "files/"):
    student = f.split("-")[0]
    if student not in found_students:
      found_students.append(student)

  # List students out in alphabetical order.
  for student in sorted(found_students):
    o.write("<a class='student-link' onclick='changeStudent(\"" + student + \
            "\")'>" + student + "</a><br>\n")
  o.write("</div></div>\n")

  # Header with student's name.
  o.write("<div id='contents'>\n")
  first_student = output["students"][0]["name"]
  first_file = output["files"][0]
  o.write("<div id='title'><div id='title-inner'>" + \
          "<div id='name'>" + first_student + "</div>\n")

  # Links for each file.
  for i in range(len(output["files"])):
    name = output["files"][i]
    if i == 0:
      o.write("<div class='label-active label' ")
    else:
      o.write("<div class='label' ")
    o.write("onclick='changeFile(this, \"" + name + "\")'>" + name + "</div>\n")
  o.write("</div></div>\n")

  o.write("<div id='iframes'>\n")

  # Graded files.
  o.write("<div class='iframe-container' id='graded'>\n")
  o.write("<div id='show-raw' onclick='showRaw()' style='display:none'>" + \
          "show raw file</div>")
  o.write("<div class='toast'>Graded File</div>")
  o.write("<iframe src='files/" + first_student + "-" + first_file + \
          ".html' id='iframe-graded'></iframe></div>\n\n")

  # Raw files.
  o.write("<div class='iframe-container' id='raw'>\n")
  o.write("<div id='hide-raw' onclick='hideRaw()'>hide raw file</div>")
  o.write("<div class='toast'>Raw File</div>")
  f = "../students/" + first_student + "-" + specs["assignment"] + "/" + \
      first_file
  o.write("<iframe src='" + f + "' id='iframe-raw'></iframe></div>\n")

  o.write("</div></div>\n")
  o.write("</div>\n")

  o.write("</div>")
  return o.getvalue()


def format_student(output, specs):
  """
  Function: format_student
  ------------------------
  Outputs the graded output for a particular student. Each student's output
  gets written to its own file.

  output: The student's JSON output.
  specs: The specs for the assignment.
  """

  # Create the necessary directories if needed.
  create_path(specs["assignment"])

  # Create output per student, per file. Files are named <student>-<file>.html.
  for f in output["files"].values():
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

      # Print out comments if the specs ask for it.
      if problem_specs.get("comments") and problem:
        o.write("<b>Comments</b>")
        if not problem.get("comments"):
          # TODO should check specs to see if comments were expected and output
          # that
          o.write("<br><i>No comments provided...</i><br>\n")
        else:
          o.write("<div class='comment'>" + problem["comments"] + "</div>")
      o.write("<b>SQL</b>")
      o.write("<div class='sql'>" + problem["sql"] + "</div>")

      # Test output.
      PROBLEM_TYPES[problem_specs["type"]]().do_output(o, problem["tests"], \
                                                       problem_specs["tests"])
      # Any errors that have occurred.
      errors = problem["errors"]
      if len(errors) > 0:
        o.write("\n<b>Errors</b>\n<br><ul>")
        for error in errors:
          o.write("<li>" + str(error) + "</li>\n")
        o.write("</ul>")

      o.write("</div>")

    o.write("<h2>Total: " + str(f["got_points"]) + " Points</h2>")
    o.write("</html>")

    filename = output["name"] + "-" + f["filename"] + ".html"
    out = open(ASSIGNMENT_DIR + specs["assignment"] + "/_results/files/" +
               filename, "w")
    out.write(o.getvalue())
    out.close()
