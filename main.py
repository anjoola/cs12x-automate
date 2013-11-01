import argparse
import dbtools, iotools
from iotools import write
import mysql.connector
from response import Response, Result
import sys

# Database to connect to for data.
DB = mysql.connector.connect(user="angela", password="cs121",
  host="sloppy.cs.caltech.edu", database="angela_db", port="4306")

# The assignment to grade.
assignment = None

# The specifications for the assignment.
specs = None

# The results file.
o = None

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
  try:
    f = open(assignment + "/" + student + "-" + assignment + "/" + filename, "r")
    # TODO run their file through the stylechecker?
    responses = iotools.parse_file(f)
    f.close()
  except IOError:
    write(o, "File does not exist.")
  except Exception:
    print "TODO"

  problems = specs[filename]
  total_points = 0
  for problem in problems:
    # Problem definitions.
    num = problem["number"]
    needs_comments = problem["comments"]
    num_points = int(problem["points"])
    got_points = num_points
    write(o, "#### Problem " + num + " (" + str(num_points) + " points)")
    print "." ,

    # Run each test for the problem.
    for test in problem["tests"]:
      test_points = int(test["points"])
      cursor = DB.cursor()

      # Run the test code.
      expected = dbtools.run_query(test, test["query"], cursor)
      # Run the student's code.
      try:
        # If there are comments to grade for this problem, print them out.
        if needs_comments == "true":
          write(o, "**Comments**\n")
          write(o, responses[num].comments)
        actual = dbtools.run_query(test, responses[num].query, cursor)

        # Compare the student's code to the results.
        # TODO check sorting order, schema
        # TODO what if don't need to check order of results or columns?
        # TODO comparing results doesn't quite work?
        if expected.results != actual.results:
          write(o, "**Test** (" + str(test_points) + " points)")
          write(o, iotools.format_lines("   ", test["query"]))
          write(o, "_Expected Results_")
          write(o, iotools.format_lines("   ", expected.output))
          write(o, "_Actual Results_")
          write(o, iotools.format_lines("   ", actual.output))

          got_points -= test_points

      # If there was a MySQL error, print out the error that occurred and the
      # code that caused the error.
      except mysql.connector.errors.ProgrammingError as e:
        write(o, "**Incorrect Code**")
        write(o, iotools.format_lines("   ", responses[num].query))
        write(o, "_MySQL Error:_ " + str(e))
        got_points -= test_points

      except Exception as e:
        print "TODO" , str(e)
        # TODO handle

    # Add to the total point count.
    got_points = (got_points if got_points > 0 else 0)
    total_points += got_points
    write(o, "> ##### Points: " + str(got_points) + " / " + str(num_points))

  write(o, "\n### Total Points: " + str(total_points))
  cursor.close()


if __name__ == "__main__":
  # Parse command-line arguments.
  parser = argparse.ArgumentParser(description="Get the arguments.")
  parser.add_argument("--assignment")
  parser.add_argument("--files", nargs="+")
  parser.add_argument("--students", nargs="+")
  args = parser.parse_args()
  (assignment, files, students) = (args.assignment, args.files, args.students)

  # If the assignment argument isn't specified, print usage statement.
  if assignment is None:
    print "Usage: main.py --assignment <assignment folder> ", \
      "[--files <files to check>] [--students <students to check>]"
    sys.exit()

  # Get the specs, files, and students.
  specs = iotools.parse_specs(assignment)
  # If nothing specified for the files, grade all the files.
  if files is None or files[0] == "*":
    files = specs["files"]
  # If nothing specified for the students, grade all the students.
  if students is None or students[0] == "*":
    students = iotools.get_students(assignment)

  print "\n\n========================START GRADING========================" ,

  o = open(assignment + "/_results.md", "w") # TODO append current time
  # Grade each student, and grade each file.
  for student in students:
    write(o, "-----------------------")
    write(o, "# <" + student + ">")
    print "\n\n" + student + ":"
    for f in files:
      print "- " + f + ":" ,
      write(o, "### " + f)
      grade(f, student)
  o.close()

  print "\n\n=========================END GRADING=========================\n\n"

  # Close connection with the database.
  DB.close()
