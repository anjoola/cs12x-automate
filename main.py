import argparse
import dbtools
from grade import Grade
import iotools
from iotools import write
import mysql.connector
import os
from models import *
import sys

# Database to connect to for data.
DB = mysql.connector.connect(user="angela", password="cs121",
  host="sloppy.cs.caltech.edu", database="angela_db", port="4306")

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
  """
  graded_file = {"filename": filename, "problems": [], "errors": []}
  graded_student["files"].append(graded_file)
  #graded_file = GradedFile(filename)
  #graded_student.add(graded_file)

  responses = {}
  got_points = 0
  try:
    f = open(assignment + "/" + student + "-" + assignment + "/" + filename, "r")
    # TODO run their file through the stylechecker?
    responses = iotools.parse_file(f)
    f.close()

    # Grade each problem in the assignment.
    problems = specs[filename]
    for problem in problems:
      graded_problem = {"num": problem["number"], "tests": [], "errors": []}
      graded_file["problems"].append(graded_problem)
      #graded_problem = GradedProblem(problem["number"])
      #graded_file.add(graded_problem)
      got_points += g.grade(problem, responses[problem["number"]], \
        graded_problem, DB.cursor())
      print ".",

  # If the file does not exist, then they get 0 points.
  except IOError:
    graded_file["errors"].append("File does not exist.")
    #write(o, "File does not exist.")

  #except Exception as e:
  #  print "TODO", e

  
  #write(o, "\n### Total Points: " + str(got_points))
  graded_file["got_points"] = got_points
  DB.cursor().close()


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

  o = GradedOutput()
  g = Grade(specs)

  # Source dependencies needed prior to grading.
  if "dependencies" in specs and len(specs["dependencies"]) > 0:
    dbtools.source_files(specs["dependencies"], DB.cursor())

  # Grade each student, and grade each file for each student.
  for student in students:
    graded_student = {"student": student, "files": []}
    #graded_student = StudentGradedOutput(student)
    o.fields["students"].append(graded_student)
    # Output stuff to the command-line so we know the progress.
    #write(o, "# -------------------------------------------") # TODO
    #write(o, "# [" + student + "]")  # TODO
    print "\n\n" + student + ":"
    for f in files:
      #write(o, "#### " + ("-" * 95))  # TODO
      print "- " + f + ":" ,
      #write(o, "### " + f)  # TODO
      grade(f, student, graded_student)

  # TODO total up all of stduent's points
  # Output the graded output.
  f = iotools.output(o.jsonify(), assignment)
  print "\n\n==== RESULTS: " + f.name

  print "\n\n=========================END GRADING=========================\n\n"

  # Close connection with the database.
  DB.close()
