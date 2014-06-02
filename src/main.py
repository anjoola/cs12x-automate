import argparse
import os
import sys

import mysql.connector

from CONFIG import ASSIGNMENT_DIR, MAX_TIMEOUT
import dbtools
from errors import *
import formatter
from grader import Grader
import iotools
from iotools import log
from models import *
import stylechecker

(assignment, files, students, db, specs, o, grader) = tuple([None] * 7)

def getargs():
  """
  Function: get_args
  ------------------
  Gets the command-line arguments and prints a usage message if needed. Figures
  out the files and students to grade.
  """
  global assignment, files, students, specs
  # Parse command-line arguments.
  parser = argparse.ArgumentParser(description="Get the arguments.")
  parser.add_argument("--assignment")
  parser.add_argument("--files", nargs="+")
  parser.add_argument("--students", nargs="+")
  parser.add_argument("--after")
  args = parser.parse_args()
  (assignment, files, students, after) = \
    (args.assignment, args.files, args.students, args.after)

  # If the assignment argument isn't specified, print usage statement.
  if assignment is None:
    print "Usage: main.py --assignment <assignment name> ", \
      "[--files <files to check>] [--students <specific students to check>] ", \
      "\n[--after <grade submissions that are turned in on or after this ", \
      "student turned it in>]"
    sys.exit()

  # Get the specs, files, and students for this assignment.
  specs = iotools.parse_specs(assignment)
  # If nothing specified for the files, grade all the files.
  if files is None or files[0] == "*":
    files = specs["files"]
  # If nothing specified for the students, grade all the students.
  if students is None or students[0] == "*":
    students = iotools.get_students(assignment, after)


def setup():
  """
  Function: setup
  ---------------
  Sets up the grading environment and tools. This includes establishing the
  database connection, reading the specs file, sourcing all dependencies,
  and running setup queries.
  """
  global db, specs, o, grader

  # The graded output.
  o = GradedOutput(specs)
  # Start up the connection with the database.
  db = dbtools.DBTools()
  db.get_db_connection(MAX_TIMEOUT)

  # Source and import files needed prior to grading and run setup queries.
  if specs.get("setup"):
    for item in specs.get("setup"):
      if item["type"] == "dependency":
        db.source_file(assignment, item["file"])
      elif item["type"] == "import":
        dbtools.import_file(assignment, item["file"])
      elif item["type"] == "queries":
        for q in item["queries"]: db.run_query(q)

  # Initialize the grading tool.
  grader = Grader(specs, db)


def grade_student(student):
  """
  Function: grade_student
  -----------------------
  Grades a particular student. Outputs the results to a file.

  student: The student name.
  """
  global assignment, files, o, grader
  log("\n\n" + student + ":")

  # Check to see that this student exists. If not, skip this student.
  path = ASSIGNMENT_DIR + assignment + "/students/" + student + "-" + \
         assignment + "/"
  if not os.path.exists(path):
    log("Student " + student + " does not exist or did not submit!")
    return

  # Graded output for this particular student. Add it to the overall output.
  output = {"name": student, "files": {}, "got_points": 0}
  o.fields["students"].append(output)

  # Parse student's response.
  response = {}
  style_errors = set()
  for filename in files:
    # Add this file to the graded output.
    graded_file = {"filename": filename, "problems": [], "errors": [], \
                   "got_points": 0}
    output["files"][filename] = graded_file
    fname = path + filename

    try:
      f = open(fname, "r")
      # Run their files through the stylechecker to make sure it is valid. Add
      # the errors to the list of style errors for this file and overall for
      # this student.
      errors = stylechecker.check(f)
      for e in errors:
        add(graded_file["errors"], e())
        style_errors.add(e)

      f.seek(0)
      response[filename] = iotools.parse_file(f)
      f.close()

    # If the file does not exist, then they get 0 points.
    except IOError:
      add(graded_file["errors"], FileNotFoundError(fname))

  # Grade this student, make style deductions, and output the results.
  output["got_points"] = grader.grade(response, output)
  output["got_points"] -= stylechecker.deduct(style_errors)
  formatter.format_student(output, specs)


def teardown():
  """
  Function: teardown
  ------------------
  Outputs the results, runs the teardown queries and closes the database
  connection.
  """
  global grader

  # Output the results to file, but only if there are students to output.
  json_output = json.loads(o.jsonify())
  if json_output["students"]:
    f = iotools.output(json_output, specs)
    log("\n\n==== RESULTS: " + f.name)

  # Run teardown queries.
  if specs.get("teardown"):
    for query in specs["teardown"]: db.run_query(query)
  grader.cleanup()

  # Close connection with the database
  db.close_db_connection()


if __name__ == "__main__":
  # Parse arguments and run setup.
  getargs()
  setup()

  log("\n\n========================START GRADING========================\n")
  # Get the state of the database before grading.
  state = db.get_state()

  # Grade each student.
  for student in students:
    grade_student(student)

    # Get the state of the database after the student is graded and reset it
    # to what it was before.
    new_state = db.get_state()
    db.reset_state(state, new_state)

  log("\n\n=========================END GRADING=========================\n")
  teardown()
