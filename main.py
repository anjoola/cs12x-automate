import argparse
from datetime import datetime
from grade import Grade
import iotools
from iotools import write
import mysql.connector
import os
from response import Response, Result
import sys
from time import strftime

# Database to connect to for data.
DB = mysql.connector.connect(user="angela", password="cs121",
  host="sloppy.cs.caltech.edu", database="angela_db", port="4306")

# The assignment to grade.
assignment = None

# The specifications for the assignment.
specs = None

# The results file.
o = None

# Grading tool.
g = None

def grade(filename, student):
  """
  Function: grade
  ---------------
  Grades a student's submission for a particular file in the assignment.

  specs: The specifications for the assignment.
  filename: The name of the file to grade.
  student: The student to grade.
  """
  responses = {}
  total_points = 0
  try:
    f = open(assignment + "/" + student + "-" + assignment + "/" + filename, "r")
    # TODO run their file through the stylechecker?
    responses = iotools.parse_file(f)
    f.close()

    # Grade each problem in the assignment.
    problems = specs[filename]
    for problem in problems:
      total_points += g.grade(problem, responses[problem["number"]], DB.cursor())
      print ".",

  # If the file does not exist, then they get 0 points.
  except IOError:
    write(o, "File does not exist.")

  #except Exception as e:
  #  print "TODO", e

  write(o, "\n### Total Points: " + str(total_points))
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

  # Make the results file.
  path = assignment + "/_results/"
  if not os.path.exists(path):
    os.mkdir(path, 0644)
  o = open(path + datetime.now().strftime("%Y-%m-%d+%H;%M;%S") + ".md", "w")
  g = Grade(specs, o)

  # Source dependencies needed prior to grading.
  if "dependencies" in specs and len(specs["dependencies"]) > 0:
    dbtools.source_files(specs["dependencies"], DB.cursor())

  # Grade each student, and grade each file.
  for student in students:
    # Output stuff to the command-line so we know the progress.
    write(o, "# -------------------------------------------")
    write(o, "# [" + student + "]")
    print "\n\n" + student + ":"
    for f in files:
      write(o, "#### " + ("-" * 95))
      print "- " + f + ":" ,
      write(o, "### " + f)
      grade(f, student)
  o.close()

  print "\n\n==== RESULTS: " + o.name

  print "\n\n=========================END GRADING=========================\n\n"

  # Close connection with the database.
  DB.close()
