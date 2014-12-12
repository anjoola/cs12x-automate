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
  MATH_JAX,
  RESULT_DIR,
  STUDENT_DIR,
  STUDENT_OUTPUT_DIR,
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
    os.mkdir(path + RESULT_DIR + STUDENT_OUTPUT_DIR)
    os.mkdir(path + RESULT_DIR + STYLE_DIR_BASE)

    # Copy over stylesheets and Javascript files.
    for f in os.listdir(STYLE_DIR):
      shutil.copy(STYLE_DIR + f, path + RESULT_DIR + STYLE_DIR_BASE + f)


def escape(text):
  """
  Function: escape
  ----------------
  Escapes text so it can be outputted as HTML.
  """
  return cgi.escape(text.encode('ascii', 'xmlcharrefreplace'))


def generate_student_list(specs):
  """
  Function: generate_student_list
  -------------------------------
  Generates the list of students that have already been graded.
  """
  students = []
  for f in os.listdir(ASSIGNMENT_DIR + specs["assignment"] + "/" +
                      RESULT_DIR + FILE_DIR):
    student = f.split("-")[0]
    if student not in students:
      students.append(student)
  return students


def format(output, specs, studentlst=None):
  """
  Function: format
  ----------------
  Formats the JSON output into HTML. This is the formatting for the main page.

  output: The graded JSON output.
  specs: The specs for the assignment.
  student_list: The list of students that have already been graded. If set to
                None, then generates this list by a directory search.
  returns: A string containing the HTML.
  """
  # Create the necessary directories if needed.
  create_path(specs["assignment"])

  o = StringIO()
  o.write("<head><title>CS 121 Automation</title></head>\n")
  o.write("<link rel='stylesheet' type='text/css' href='" + STYLE_DIR_BASE +
          "css.css'>\n")
  o.write("<link rel='stylesheet' type='text/css' href='" + STYLE_DIR_BASE +
          "hide-raw.css' media='screen and (max-width: 900px)'>\n")
  o.write("<script type='text/javascript' src='" + STYLE_DIR_BASE +
          "javascript.js'></script>\n")
  o.write("\n<input type='hidden' id='assignment' value='" +
          specs["assignment"] + "'>\n")

  o.write("<div id='container'>\n")

  # Print out the list of students to the list. Finds this by searching the
  # directory (since we may run the automation tool multiple times on different
  # sets of students).
  o.write("<div id='list'><div id='list-inner'>\n" +
          "<div id='students'>Students</div><br>\n")
  students = generate_student_list(specs) if studentlst is None else studentlst

  # List students out in alphabetical order.
  for student in sorted(students):
    o.write("<a class='student-link' onclick='changeStudent(\"" + student +
            "\")' id=\"" + student + "\">" + student + "</a><br>\n")
  o.write("</div></div>\n")

  # Header with student's name.
  o.write("<div id='contents'>\n")
  first_student = output["students"][0]["name"]
  first_file = output["files"][0]
  o.write("<div id='title'><div id='title-inner'>" +
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
  o.write("<div id='show-raw' onclick='showRaw()' style='display:none'>" +
          "show raw file</div>")
  o.write("<div class='toast'>Graded File</div>")
  o.write("<iframe src='files/" + first_student + "-" + first_file +
          ".html' id='iframe-graded'></iframe></div>\n\n")

  # Raw files.
  o.write("<div class='iframe-container' id='raw'>\n")
  o.write("<div id='hide-raw' onclick='hideRaw()'>hide raw file</div>")
  o.write("<div class='toast'>Raw File</div>")
  o.write("<iframe src='files/" + first_student + "-" + first_file +
          ".raw.html' id='iframe-raw'></iframe></div>\n")

  o.write("</div></div>\n")
  o.write("</div>\n")

  o.write("</div>")
  return o.getvalue()


def format_raw_file(fname, student, assignment):
  """
  Function: format_raw_file
  -------------------------
  Creates an HTML version of a SQL file so web browsers won't try to download
  the file.

  fname: The raw filename.
  specs: The specs for the assignment.
  """
  try:
    out = open(ASSIGNMENT_DIR + assignment + "/" + RESULT_DIR + FILE_DIR +
               student + "-" + fname + ".raw.html", 'w')
    infile = open(ASSIGNMENT_DIR + assignment + "/" + STUDENT_DIR +
                  student + "-" + assignment + "/" + fname, 'r')
    contents = infile.read()
    out.write("<pre style='font-family: Consolas, monospace; " +
              "font-size: 12px;'>" + contents + "</pre>")
    out.close()
  except IOError:
    return


def format_student(student, output, specs, hide_solutions):
  """
  Function: format_student
  ------------------------
  Outputs the graded output for a particular student. Each student's output
  gets written to its own file.

  student: The student's name.
  output: The student's JSON output.
  specs: The specs for the assignment.
  hide_solutions: Whether or not to hide solution output.
  """

  # Create the necessary directories if needed.
  create_path(specs["assignment"])

  # Put styling inline if hiding solutions.
  if hide_solutions:
    o = StringIO()
    o.write("<style type='text/css'>\n")
    css = open(STYLE_DIR + "css.css", 'r')
    o.write(css.read())
    o.write("</style>")

  # Create output per student, per file. Files are named <student>-<file>.html.
  for (fname, f) in output["files"].iteritems():
    # Generate HTML versions of raw files (so it can be displayed on IE and
    # other browsers).
    format_raw_file(fname, student, specs["assignment"])

    if not hide_solutions:
      o = StringIO()
      o.write("<link rel='stylesheet' type='text/css' href='" +
              STYLE_DIR + "css.css'>\n")
      o.write("<script type='text/javascript' src='" + STYLE_DIR +
              "javascript.js'></script>\n")
      o.write("<script type='text/javascript' src='" + MATH_JAX +
              "'></script>\n")
    o.write("<html class='student-page'>\n")

    if hide_solutions:
      o.write("<div class='filename'>" + fname + "</div>")

    # Print out all errors that have occurred with the file.
    if f.get("errors"):
      o.write("<div class='file-errors'><h3>File Errors</h3><ul>")

      for error in f["errors"]:
        o.write("<li>" + error + "</li>")
      o.write("</ul></div>")

    # Loop through all the problems.
    for (i, problem) in enumerate(f["problems"]):
      o.write("<div class='problem'>\n")
      problem_specs = specs[f["filename"]][i]
      if hide_solutions:
        o.write("<h3>Problem " + problem["num"] + "</h3>\n")
        o.write("<div id=\"" + problem["num"] + "\">")
      else:
        # Figure out the color of the header.
        warn_color = ""
        if any([t["success"] == "UNDETERMINED" for t in problem["tests"]]):
          warn_color = " class='warning' "
        elif problem["got_points"] != problem_specs["points"]:
          warn_color = " class='error' "

        # Figure out the number of points received; ? if it needs to be
        # manually graded.
        points = problem["got_points"]
        points = "?" if warn_color == " class='warning' " else str(points)

        o.write("<a onclick='toggle(\"" + problem["num"] + "\")'><h3 " +
                warn_color + ">Problem " + problem["num"] + " (" +
                points + "/" + str(problem_specs["points"]) +
                " Points)</h3></a>\n")
        o.write("<div id=\"" + problem["num"] + "\" style='display:none'>")

      # If the student did not submit an answer for this problem.
      if problem.get("notexist"):
        o.write("<i>Did not submit a response for this question!</i>")
        o.write("</div></div>")
        continue

      # Problem statement.
      if problem_specs.get("question"):
        o.write("<b>Problem Statement</b>\n")
        o.write("<div class='question'>" + problem_specs.get("question") +
                "</div>\n")
      # Print out comments if the specs ask for it.
      if problem.get("comments") or problem_specs.get("comments"):
        o.write("<b>Comments</b>")
        if not problem.get("comments"):
          o.write("<br><i>Comments expected but none provided...</i><br><br>\n")
        else:
          o.write("<div class='comment'>" + escape(problem["comments"]) + "</div>")
      if hide_solutions:
        o.write("<b>Response</b>")
      else:
        o.write("<b>Student's Response</b>")
      o.write("<div class='sql' contenteditable='true' " +
              "onclick='document.execCommand(\"selectAll\", false, null)'>" +
              escape(problem["sql"]) + "</div>")

      # Do test output.
      PROBLEM_TYPES[problem_specs["type"]]().do_output(o,
                                                       problem["tests"],
                                                       problem_specs["tests"],
                                                       hide_solutions)

      # Any errors that have occurred. Hide them if hiding solutions since
      # some errors may display solution queries.
      if not hide_solutions:
        errors = problem["errors"]
        if len(errors) > 0:
          o.write("\n<b>Errors</b>\n<br><ul>")
          for error in errors:
            o.write("<li>" + str(error) + "</li>\n")
          o.write("</ul>")

      o.write("</div>\n</div>")

    if not hide_solutions:
      o.write("</html>")
      filename = output["name"] + "-" + f["filename"] + ".html"
      out = open(ASSIGNMENT_DIR + specs["assignment"] + "/" + RESULT_DIR +
                 FILE_DIR + filename, "w")
      out.write(o.getvalue())
      out.close()

  if hide_solutions:
    o.write("</html>")

    filename = output["name"] + ".html"
    out = open(ASSIGNMENT_DIR + specs["assignment"] + "/" + RESULT_DIR +
               STUDENT_OUTPUT_DIR + filename, "w")
    out.write(o.getvalue())
    out.close()
