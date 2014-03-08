import argparse
import os
import sys

import mysql.connector

from CONFIG import ASSIGNMENT_DIR, MAX_TIMEOUT
import dbtools
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

  # Get the specs, files, and students.
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
  o = GradedOutput(specs) # TODO fix this should have a better name
  # Start up the connection with the database.
  db = dbtools.DBTools()
  db.get_db_connection(MAX_TIMEOUT)

  # Source files needed prior to grading and run setup queries.
  if specs.get("dependencies"):
    db.source_files(assignment, specs["dependencies"])
  if specs.get("import"):
    dbtools.import_files(assignment, specs["import"])
  if specs.get("setup"):
    for q in specs["setup"]: db.run_query(q)

  # Create the grading tool and output.
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

  # Graded output.
  output = {"name": student, "files": {}, "got_points": 0}
  o.fields["students"].append(output)

  # Parse student's response.
  response = {}
  for filename in files:
    # Add this file to the graded output.
    graded_file = {"filename": filename, "problems": [], "errors": []}
    output["files"][filename] = graded_file

    try:
      f = open(ASSIGNMENT_DIR + assignment + "/students/" + student + "-" + \
               assignment + "/" + filename, "r")
      # Run their files through the style-checker to make sure it is valid and
      # take points off for violations.
      # TODO output["style-deductions"] = stylechecker.check(f, specs)
      response[filename] = iotools.parse_file(f)
      f.close()

    # If the file has a style error (and cannot be parsed), they get 0 points.
    except stylechecker.StyleError:
      graded_file["errors"].append("File does not follow the style guide.") # TODO better errrr

    # If the file does not exist, then they get 0 points.
    except IOError:
      graded_file["errors"].append("File does not exist.")
      raise

  # Grade this student.
  try:
    output["got_points"] = grader.grade(response, output)
    # Apply style deductions. todo pass by reference?
    #graded_student = stylechecker.deduct(graded_student)

    # Output the results for this student.
    formatter.format_student(output, specs)

  # The student might not exist.
  except IOError as e: # TODO error in the wrong place???
    print "TODO" + str(e)
    log("Student " + student + " does not exist!")


def teardown():
  """
  Function: teardown
  ------------------
  Outputs the results, runs the teardown queries and closes the database
  connection.
  """
  global grader

  # Output the results to file.
  f = iotools.output(o.jsonify(), specs)
  log("\n\n==== RESULTS: " + f.name)

  # Run teardown queries.
  if specs.get("teardown"):
    for query in specs["teardown"]: db.run_query(query)
  grader.cleanup()

  # Close connection with the database
  db.close_db_connection()


if __name__ == "__main__":
  getargs()
  setup()
  log("\n\n========================START GRADING========================\n")
  for student in students:
    grade_student(student)
  log("\n\n=========================END GRADING=========================\n")
  teardown()