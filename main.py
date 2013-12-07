import argparse
from CONFIG import MAX_TIMEOUT
import dbtools
from dbtools import DBTools
import formatter
from grade import Grade
import iotools
import mysql.connector
import os
from models import *
from stylechecker import StyleError
import stylechecker
import sys

def grade():
  """
  Function: grade
  ---------------
  Grades all the students and files.
  """
  print "\n\n========================START GRADING========================" ,

  # The graded output.
  o = GradedOutput(specs)
  # Start up the connection with the database.
  db = DBTools()
  db.get_db_connection(MAX_TIMEOUT)

  # Source files needed prior to grading and run setup queries.
  if specs.get("dependencies"):
    db.source_files(assignment, specs["dependencies"])
  if specs.get("import"):
    dbtools.import_files(assignment, specs["import"])
  if specs.get("setup"):
    for q in specs["setup"]: db.run_query(q)

  # Grade each student, and grade each file for each student.
  for student in students:
    got_points = 0
    graded_student = {"name": student, "files": [], "got_points": 0}
    o.fields["students"].append(graded_student)

    graded_student["got_points"] = grade_student(db, student, graded_student)
    # Apply style deductions.
    graded_student = stylechecker.deduct(graded_student)

    # Output the results for this student.
    formatter.html_student(graded_student, specs)

  # Output the results to file.
  f = iotools.output(o.jsonify(), specs, output_type)
  print "\n\n==== RESULTS: " + f.name

  print "\n\n=========================END GRADING=========================\n\n"

  # Run teardown queries.
  if specs.get("teardown"):
    for q in specs["teardown"]: db.run_query(q)

  # Close connection with the database
  db.close_db_connection()


def grade_student(db, student, graded_student):
  """
  Function: grade_student
  -----------------------
  Grades a particular student.

  dh: The database.
  student: The student's name.
  graded_student: A dictionary containing the graded results for that student.

  returns: The number of points this student got.
  """
  # The grading tool.
  g = Grade(specs, db)
  # Dictionary containing files and a tuple containing the student's responses
  # for each file and the graded file.
  file_responses = {}

  # Parse all of the responses first before grading.
  print "\n\n" + student + ":"
  for filename in files:
    graded_file = {"filename": filename, "problems": [], "errors": []}
    graded_student["files"].append(graded_file)

    try:
      f = open(assignment + "/students/" + student + "-" + assignment + \
        "/" + filename, "r")
      # Run their files through the style-checker to make sure it is valid and
      # take points off for violations.
      graded_student["style-deductions"] = stylechecker.check(f, specs)
      responses = iotools.parse_file(f)
      f.close()

      # Add to the dictionary to process later.
      file_responses[filename] = (responses, graded_file)

    # If the file has a style error (and cannot be parsed), they get 0 points.
    except StyleError:
      graded_file["errors"].append("File does not follow the style guide.")

    # If the file does not exist, then they get 0 points.
    except IOError:
      graded_file["errors"].append("File does not exist.")

  # Grade the files (that exist) for this student.
  total_points = 0
  for f in files:
    # Skip this file if it doesn't exist.
    if f not in file_responses.keys():
      continue

    print "- " + f + ":" ,
    (responses, graded_file) = file_responses[f]
    got_points = 0

    # Grade each problem in the assignment.
    problems = specs[f]
    for problem in problems:
      graded_problem = {"num": problem["number"], "tests": [], "errors": [], \
        "got_points": 0}
      graded_file["problems"].append(graded_problem)
      try:
        got_points += g.grade(problem, responses[problem["number"]], \
          graded_problem, file_responses)
      # If they didn't do a problem.
      except KeyError:
        graded_problem["notexist"] = True
      print ".",

    graded_file["got_points"] = got_points
    total_points += 0
    print "\n"

  return total_points


if __name__ == "__main__":
  # Parse command-line arguments.
  parser = argparse.ArgumentParser(description="Get the arguments.")
  parser.add_argument("--assignment")
  parser.add_argument("--files", nargs="+")
  parser.add_argument("--students", nargs="+")
  parser.add_argument("--output")
  parser.add_argument("--after")
  args = parser.parse_args()
  (assignment, files, students, output_type, after) = \
    (args.assignment, args.files, args.students, args.output, args.after)

  # If the assignment argument isn't specified, print usage statement.
  if assignment is None:
    print "Usage: main.py --assignment <assignment folder> ", \
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

  grade()
