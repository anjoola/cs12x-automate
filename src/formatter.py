"""
Module: formatter
-----------------
Formats the graded output into HTML.
"""

import cgi
from cStringIO import StringIO
import json
import os
import shutil

from CONFIG import ASSIGNMENT_DIR, RESULT_DIR, STYLE_DIR
from problemtype import *

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
    os.mkdir(path + RESULT_DIR + "files/")
    os.mkdir(path + RESULT_DIR + "style/")

    # Copy over stylesheets and Javascript files.
    for f in os.listdir(STYLE_DIR):
      shutil.copy(STYLE_DIR + f, path + RESULT_DIR + "style/" + f)


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

  # Print out the list of students to the list. Finds this by searching the
  # directory (since we may run the automation tool mutliple times on different
  # sets of students).
  o.write("<div id='left'>\n<div id='students'>Students</div><br>")
  found_students = []
  for f in os.listdir(ASSIGNMENT_DIR + specs["assignment"] + "/" + \
                      RESULT_DIR + "files/"):
    student = f.split("-")[0]
    if student not in found_students:
      found_students.append(student)

  # List students out in alphabetical order.
  for student in sorted(found_students):
    o.write("<a onclick='changeStudent(\"" + student + "\")'>" + student + \
            "</a><br>\n")
  o.write("</div>\n")

  # Graded output and actual files.
  first_student = output["students"][0]["name"]
  first_file = output["files"][0]
  o.write("<div id='container'>\n")
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

  o.write("</div>")
  return o.getvalue()

# TODO TODO add fancy javascript stuff

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

  # Create output per student, per file. Files are named student-file.html.
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
          o.write("<pre>" + problem["comments"] + "</pre>")
      o.write("<b>SQL</b>")
      o.write("<pre>" + problem["sql"] + "</pre>")

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
    o.write("<br><br></html>")

    filename = output["name"] + "-" + f["filename"] + ".html"
    out = open(ASSIGNMENT_DIR + specs["assignment"] + "/_results/files/" +
               filename, "w")
    out.write(o.getvalue())
    out.close()
