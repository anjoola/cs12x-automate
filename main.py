import argparse
from CONFIG import *
import dbtools
from grade import Grade
import iotools
import mysql.connector
import os
from models import *
from stylechecker import StyleError
import stylechecker
import sys

# The database connection. Parameters are specified in the CONFIG.py file.
DB = mysql.connector.connect(user=USER, password=PASS, host=HOST, \
  database=DATABASE, port=PORT)

# The assignment to grade.
assignment = None

# The specifications for the assignment.
specs = None

# The graded output.
o = None

# Grading tool.
g = None

def grade(filename, student, graded_student):
  """
  Function: grade
  ---------------
  Grades a student's submission for a particular file in the assignment.

  specs: The specifications for the assignment.
  filename: The name of the file to grade.
  student: The student to grade.
  graded_student: The graded output for that student.

  returns: The total points the student got for this file.
  """
  graded_file = {"filename": filename, "problems": [], "errors": []}
  graded_student["files"].append(graded_file)
  got_points = 0

  try:
    f = open(assignment + "/" + student + "-" + assignment + \
      "/" + filename, "r")
    # Run their files through the style-checker to make sure it is valid and
    # take points off for violations.
    graded_student["style-deductions"] = stylechecker.check(f, specs)
    responses = iotools.parse_file(f)
    f.close()

    # Grade each problem in the assignment.
    problems = specs[filename]
    for problem in problems:
      graded_problem = {"num": problem["number"], "tests": [], "errors": []}
      graded_file["problems"].append(graded_problem)
      got_points += g.grade(problem, responses[problem["number"]], \
        graded_problem, DB.cursor(), responses)
      print ".",

  # If the file has a style error (and cannot be parsed), they get 0 points.
  except StyleError:
    graded_File["errors"].append("File does not follow the style guide.")

  # If the file does not exist, then they get 0 points.
  except IOError:
    graded_file["errors"].append("File does not exist.")

  #except Exception as e:
  #  print "RUN-TIME EXCEPTION: ", e

  graded_file["got_points"] = got_points
  return got_points


if __name__ == "__main__":
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

  print "\n\n========================START GRADING========================" ,

  o = GradedOutput(specs)
  g = Grade(specs)

  # Source files needed prior to grading.
  if "dependencies" in specs and len(specs["dependencies"]) > 0:
    dbtools.source_files(assignment, specs["dependencies"], DB.cursor())
  if "import" in specs and len(specs["import"]) > 0:
    dbtools.import_files(assignment, specs["import"])

  # Grade each student, and grade each file for each student.
  for student in students:
    got_points = 0
    graded_student = {"name": student, "files": [], "got_points": 0}
    o.fields["students"].append(graded_student)

    # Output stuff to the command-line so we know the progress.
    print "\n\n" + student + ":"
    for f in files:
      print "- " + f + ":" ,
      got_points += grade(f, student, graded_student)
      print "\n"

    graded_student["got_points"] = got_points
    # Apply style deductions.
    graded_student = stylechecker.deduct(graded_student)

  # Output the graded output.
  f = iotools.output(o.jsonify(), specs)
  print "\n\n==== RESULTS: " + f.name

  print "\n\n=========================END GRADING=========================\n\n"

  # Close connection with the database.
  DB.cursor().close()
  DB.close()
