"""
Module: output.py
-----------------
Formats the output.
"""

from cStringIO import StringIO
from CONFIG import TYPE_OUTPUTS
import difflib
import json
from testoutput import TestOutput

def get_diffs(lst1, lst2):
  """
  Function: get_diffs
  -------------------
  Gets the diffs of two lists.

  lst1: The first list.
  lst2: The second list.
  returns: A tuple containing two lists (one for lst1, one for lst2). The list
           contains tuples of the form (type, value) where type can either be
           "add", "remove", or "".
  """

  def is_line_junk(string):
    """
    Function: is_line_junk
    ----------------------
    Returns whether or not a line is junk and should be ignored when doing
    a diff.
    """
    return string == " " or string == "-" or string == "+"

  # Get the diffs.
  (one, two) = ([], [])
  diff = difflib.ndiff(lst1, lst2, is_line_junk)

  # True if last added to "one".
  last_added = True
  # True if we've just seen a close match and need to modify the NEXT
  # row coming in.
  close_match = False

  for item in diff:
    # If the previous thing was a close match.
    if close_match and item.startswith("+"):
      close_match = False
      two.append(("", item.replace("+ ", "")))
    # A subtraction; goes in the "one" list.
    elif item.startswith("-"):
      last_added = True
      one.append(("remove", item.replace("- ", "")))
    # An addition, goes in the "two" list.
    elif item.startswith("+"):
      last_added = False
      two.append(("add", item.replace("+ ", "")))
    # Similar lines, but not the same. Don't count them as the same line.
    elif item.find("?") != -1 and item.find("^") != -1:
      continue
    # Close match for the previous two elements. Don't mark them as being
    # added or removed.
    elif item.find("?") != -1:
      if not last_added:
        one[len(one)-1] = ("", one[len(one)-1][1])
        two[len(two)-1] = ("", two[len(two)-1][1])
      else:
        one[len(one)-1] = ("", one[len(one)-1][1])
        close_match = True

  return (one, two)


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
  o.write("<link rel='stylesheet' type='text/css' href='css.css'>\n")
  o.write("<script type='text/javascript' src='javascript.js'></script>\n")
  o.write("<input type='hidden' id='assignment' value='" + \
    specs["assignment"] + "'>")

  # Print out the list of students to the list.
  o.write("<div id='left'>\n<div id='students'>Students</div><br>")
  for student in output["students"]:
    name = student["name"]
    o.write("<a onclick='changeStudent(\"" + name + "\")'>" + name + "</a><br>")

    # Actually write out those student's files. TODO html needs to be able
    # to get this itself.
    html_student(student, specs)
  o.write("</div>")

  # Graded output and actual files.
  # TODO the files to output should only be files that exist for a student..
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
  o.write("</div>\n<iframe src='" + first_student + "-" + first_file + \
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
  f = "../" + first_student + "-" + specs["assignment"] + "/" + first_file
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
    o.write("<link rel='stylesheet' type='text/css' href='css.css'>\n")
    o.write("<script type='text/javascript' src='javascript.js'></script>\n")
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
      # Print out comments and submitted results if the specs ask for it.
      if problem_specs.get("comments"):
        o.write("<b>Comments</b>")
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
      
      # TODO other things
      o.write("</div>")

    o.write("<h2>Total: " + str(f["got_points"]) + " Points</h2>")
    o.write("<br><br></html>")

    filename = student["name"] + "-" + f["filename"] + ".html"
    output = open(specs["assignment"] + "/_results/" + filename, "w")
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
          if test["type"] in TYPE_OUTPUTS and not test["success"] and \
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
