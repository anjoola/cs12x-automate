import argparse
import dbtools, iotools
import mysql.connector
from response import Response
import sys

# Database to connect to for data.
DB = mysql.connector.connect(user="angela", password="cs121",
  host="sloppy.cs.caltech.edu", database="angela_db", port="4306")

# The assignment to grade.
assignment = None

# The specifications for the assignment.
specs = None

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
    f = open(assignment + "/" + student + "/" + filename, "r")
    # TODO run their file through the stylechecker?
    responses = iotools.parse_file(f)
    f.close()
  except IOError:
    print "TODO"
  except Exception:
    print "TODO"

  problems = specs[filename]
  total_points = 0
  for problem in problems:
    # Problem definitions.
    problem_num = problem["number"]
    needs_comments = problem["comments"]
    num_points = int(problem["points"])

    print "==== Problem " + problem_num + " (" + str(num_points) + " points)\n"

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
          print "-- COMMENTS" ,
          iotools.format_lines(responses[problem_num].comments)
        result = dbtools.run_query(test, responses[problem_num].query, cursor)

        # Compare the student's code to the results.
        # TODO check sorting order, schema
        if str(sorted(expected)) != str(sorted(result)):
          # TODO: print out the wrong query
          num_points -= test_points

      # If the code doesn't work, they don't get any points.
      except Exception:
        # TODO print out the error
        # Print out the non-working code just in case it was a syntax error.
        print "-- INCORRECT CODE" ,
        iotools.format_lines(responses[problem_num].query)
        num_points -= test_points

      print ""

    # Add to the total point count.
    total_points += (num_points if num_points > 0 else 0)

  print "TOTAL POINTS: " + str(total_points)
  cursor.close()


def parse_file(f):
  """
  Function: parse_file
  --------------------
  Parses the file into a dict of the question number and the student's response
  to that question.

  f: The file object to parse.
  returns: The dictionary.
  """

  # Dictionary containing a mapping from the question number to the response.
  responses = {}
  # The current problem number being parsed.
  current_problem = ""

  for line in f:
    # If this is a blank line, just skip it.
    if len(line.strip()) == 0:
      continue

    # Find the indicator denoting the start of an response.
    elif line.strip().startswith("-- [Problem ") and line.strip().endswith("]"):
      current_problem = line.replace("-- [Problem ", "").replace("]", "")
      current_problem = current_problem.strip()
      # This is a new problem, so create an empty response to with no comments.
      responses[current_problem] = Problem()

    # Lines with comments.
    elif line.startswith("--"):
      responses[current_problem].comments += \
        line.replace("-- ", "").replace("--", "")

    # Continuation of a response from a previous line.
    else:
      responses[current_problem].response += line

  return responses


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

  print "\n\n========================START GRADING========================\n\n"

  # Grade each student, and grade each file.
  for student in students:
    for f in files:
      grade(f, student)

  print "\n\n=========================END GRADING=========================\n\n"

  # Close connection with the database.
  DB.close()
