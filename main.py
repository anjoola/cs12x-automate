import argparse
import dbtools
import json
import mysql.connector
import os, sys

# Database to connect to for data.
DB = mysql.connector.connect(user="angela", password="cs121",
  host="sloppy.cs.caltech.edu", database="angela_db", port="4306")

class Problem:
  """
  Problem
  -------
  Represents a problem on the homework, including the response and the
  comments on the response if needed.
  """
  def __init__(self):
    self.comments = ""
    self.response = ""

  def __repr__(self):
    return self.__str__()

  def __str__(self):
    return "(" + self.comments + ", " + self.response + ")"


def grade(specs, filename):
  """
  grade
  -----
  Grades a file according to the specs. Will search the specs may contain
  details about multiple files, so gets the specs for the corresponding file.

  specs: The specs (an object).
  filename: The file name of the file to grade.
  """
  f = open(filename, "r")
  try:
    responses = parse_file(f)
  except Exception:
    print "SAD"
  finally:
    f.close()

  # TODO be able to grade multiple files
  problems = specs["queries.sql"]
  total_points = 0
  for problem in problems:
    # Problem definitions.
    problem_num = problem["number"]
    needs_comments = problem["comments"]
    num_points = int(problem["points"])

    print "-- Problem " + problem_num + " (" + str(num_points) + " points) "

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
          print responses[problem_num].comments
        result = dbtools.run_query(test, responses[problem_num].response, cursor)

        # Compare the student's code to the results.
        # TODO check sorting order, schema
        if str(sorted(expected)) != str(sorted(result)):
          # TODO: print out the wrong query
          num_points -= test_points

      # If the code doesn't work, they don't get any points.
      except Exception:
        # TODO print out the error
        # Print out the non-working code just in case it was a syntax error.
        print "Non-working code: \"" + responses[problem_num].response + "\""
        num_points -= test_points

    # Add to the total point count.
    total_points += (num_points if num_points > 0 else 0)

  print "Total points: " + str(total_points)
  cursor.close()


def parse_file(f):
  """
  parse_file
  ----------
  Parses the file into a dictionary of questions and the student's responses.

  f: The file object to parse.
  returns: A dictionary containing a mapping of the question number and the
           student's response.
  """

  # Dictionary containing a mapping from the problem number to the response.
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
      # Create an empty response to with no comments or responses.
      responses[current_problem] = Problem()

    # Lines with comments.
    elif line.startswith("--"):
      responses[current_problem].comments += line.replace("-- ", "").replace("--", "")

    # Lines with SQL queries.
    else:
      responses[current_problem].response += line

  return responses


if __name__ == "__main__":
  # Parse command-line arguments.
  parser = argparse.ArgumentParser(description="Get the arguments.")
  parser.add_argument("--specs")
  # The files to grade. Can be one or more files, or all files if * or nothing
  # is specified.
  parser.add_argument("--files", nargs="+")
  args = parser.parse_args()
  (specs, files) = (args.specs, args.files)

  # If no arguments specified.
  if specs is None:
    print "Usage: main.py --specs <spec folder> [--files <files to check>]"
    sys.exit()

  # Open the spec folder to find the spec file. This file is a JSON string.
  # Convert it into a JSON object.
  spec_file = open(specs + "/" + specs + "." + "spec", "r")
  specs = json.loads("".join(spec_file.readlines()))
  spec_file.close()

  print "\n\n========================START GRADING========================\n\n"

  # If * or nothing is specified for the files, grade all the files in the
  # assignment. This is in the specs file.
  if files is None or files[0] == "*":
    files = specs["files"]
    
    # TODO go through each subdirectory and get all files
    # TODO: deal with directories
    # TODO only find files corresponding to this spec
    # TODO: need to untar stuff
    files = [f for f in os.listdir(".")] # TODO f.startswith(... etc)

# TODO stopped here,
# want to grade per student, then for each student, per file
  # Grade each file.
  for f in files:
    grade(specs, f)

  # Close connection with the database.
  DB.close()
  print "\n\n=========================END GRADING=========================\n\n"
