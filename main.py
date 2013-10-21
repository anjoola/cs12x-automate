import argparse, sqlparse
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
      expected = run_query(test, test["query"], cursor)
      # Run the student's code.
      try:
        # If there are comments to grade for this problem, print them out.
        if needs_comments == "true":
          print responses[problem_num].comments
        result = run_query(test, responses[problem_num].response, cursor)

        # Compare the student's code to the results.
        # TODO check sorting order, schema
        if str(sorted(expected)) != str(sorted(result)):
          num_points -= test_points

      # If the code doesn't work, they don't get any points.
      except Exception:
        # Print out the non-working code just in case it was a syntax error.
        print "Non-working code: \"" + responses[problem_num].response + "\""
        num_points -= test_points

    # Add to the total point count.
    total_points += (num_points if num_points > 0 else 0)

  print "Total points: " + str(total_points)
  cursor.close()


def source_files(files, cursor):
  """
  source_files
  ------------
  Sources files into the database. Since the "source" command is for the
  MySQL command-line interface, we have to parse the source file and run
  each command one at a time.

  files: The source files to source.
  cursor: The database cursor.
  """

  if len(files) <= 0:
    return

  # Loop through each source file.
  for source in files:
    sql = open(source).read()
    sql_list = sqlparse.split(sql)
    for sql in sql_list:
      if len(sql.strip()) == 0:
        continue
      cursor.execute(sql)


def run_query(test, query, cursor):
  """
  run_query
  ---------
  test: The test to run. Contains information about the source files, the
        setup, and the teardown necessary for each test.
  query: The query to run.
  cursor: The database cursor.
  returns: The result of running the query.
  """
  result = []

  # Source files if needed.
  source_files(test["source"], cursor)

  # Query setup.
  cursor.execute(test["setup"])
  cursor.execute(query)

  result = [str(row) for row in cursor]
  cursor.execute(test["teardown"])
  return result


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
  # The files to grade. Can be one or more files, or all files.
  parser.add_argument("--files", nargs="+")
  args = parser.parse_args()
  (specs, files) = (args.specs, args.files)

  # If no arguments specified.
  if specs is None or files is None:
    print "Usage: main.py --specs [spec folder] --files [files to check]"
    sys.exit()

  print "\n\n========================START GRADING========================\n\n"
    
  # TODO: Handle homeworks with multiple file submissions

  # IF * is specified as files, then find all files of the same form.
  if files[0] == "*":
    # TODO: deal with directories
    # TODO only find files corresponding to this spec
    # TODO: need to untar stuff
    files = [f for f in os.listdir(".")] # TODO f.startswith(... etc)

  # Open the spec folder to find the spec file. This file is a JSON string.
  # Convert it into a JSON object.
  spec_file = open(specs + "/" + specs + "." + "spec", "r")
  specs = json.loads("".join(spec_file.readlines()))
  spec_file.close()

  # Grade each file.
  for f in files:
    grade(specs, f)

  # Close connection with the database.
  DB.close()
  print "\n\n=========================END GRADING=========================\n\n"
