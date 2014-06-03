"""
Module: iotools
---------------
Functions involving input and output into the system, as well as file-related
functions.
"""
import json, os, sys, time
from datetime import datetime
from os.path import getmtime

import dbtools, formatter
from CONFIG import ASSIGNMENT_DIR, ERROR, VERBOSE
from models import Response

def get_students(assignment, after=None):
  """
  Function: get_students
  ----------------------
  Gets all the students for a given assignment.

  assignment: The assignment.
  after: The student to start grading from. Finds all students who've
         submitted at a time after this student (includes this student).
  returns: A list of students who've submitted for that assignment.
  """
  directory = ASSIGNMENT_DIR + assignment + "/students/"
  files = [f for f in os.walk(directory).next()[1]
           if f.endswith("-" + assignment)]

  # If looking for files after a particular person.
  if after is not None:
    try:
      # Only get files modified after the provided time.
      after = time.mktime(time.strptime(after, "%Y-%m-%d"))
      files = [f for f in files if getmtime(directory + f) >= after]

    # If the string they entered for the date is incorrect, just skip the date
    # filtering.
    except ValueError:
      err("'after' parameter not formatted correctly (must be YYYY-MM-DD)")
      pass

  return [f.replace("-" + assignment, "") for f in files]


def err(msg, fatal=False):
  """
  Function: err
  -------------
  Outputs to the console if the ERROR flag is on. If the VERBOSE flag is on,
  will also output, no matter what the ERROR flag is set to.

  string: The error message to print.
  fatal: If True, will immediately terminate the program.
  """
  if VERBOSE or ERROR:
    print "(ERROR)", msg
  if fatal:
    sys.exit(1)


def log(string):
  """
  Function: log
  -------------
  Outputs to the console if the VERBOSE flag is on.
  """
  if VERBOSE:
    print string, 


def output(json, specs, raw=False):
  """
  Function: output
  ----------------
  Outputs the graded output to a file.

  json: The graded output.
  specs: The assignment specs.
  raw: Whether or not to output as a raw JSON string. True if so, False
       otherwise.
  returns: The file where the output was written to.
  """
  path = ASSIGNMENT_DIR + specs["assignment"] + "/_results/"
  if not os.path.exists(path):
    os.mkdir(path, 0644)

  if not os.path.exists(path+ "files/"):
    os.mkdir(path + "files/", 0644)

  f = None
  # For the raw, JSON output.
  if raw:
    f = open(path + datetime.now().strftime("%Y-%m-%d+%H;%M;%S") + ".json", "w")
    f.write(json)

  # A nicely formatted HTML file.
  else:
    f = open(path + "index.html", "w")
    f.write(formatter.format(json, specs))

  f.close()
  return f


def parse_file(f):
  """
  Function: parse_file
  --------------------
  Parses a student's file into a dictionary with the key as the problem number
  and the student's response as the value. Also parses the student's comments
  and query.

  f: The file object to parse.
  returns: The dict of the question number and student's response.
  """

  # Dictionary containing a mapping from the problem number to the response.
  responses = {}
  # The current problem number being parsed.
  curr = ""
  # True if in the middle of parsing a block comment.
  started_block_comment = False
  # True if in the middle of parsing SQL.
  started_sql = False

  def add_line(line):
    """
    Function: add_line
    ------------------
    Adds a line to the comments.
    """
    # If these are comments at the top of the file, ignore them.
    if curr == "":
      return
    #if len(line.strip()) > 0: TODO
    line = line + "\n"
    responses[curr].comments += line

  inline_comment = ""
  # Preprocess the file for DELIMITER statements.
  f = dbtools.preprocess_sql(f)
  for line in f.split("\n"):
    # If in the middle of a block comment.
    if started_block_comment:
      # See if they are now ending the block comment.
      if line.strip().endswith("*/"):
        started_block_comment = False
        line = line.replace(" */", "").replace("*/", "").strip()
      # Strip out leading *'s if they have any.
      if line.strip().startswith("*"):
        line = (line[line.find("*") + 1:]).strip()
      add_line(line)

    # If this is a blank line, just skip it.
    elif len(line.strip()) == 0:
      continue

    # Indicator denoting the start of an response.
    elif line.strip().startswith("-- [Problem ") and line.strip().endswith("]"):
      started_sql = False
      curr = line.replace("-- [Problem ", "").replace("]", "")
      curr = curr.strip()
      # This is a new problem, so create an empty response to with no comments.
      responses[curr] = Response()

    # Lines with comments of the form "--". Only add this to the comments if it
    # is before the SQL starts appearing.
    elif not started_sql and line.strip().startswith("--"):
      add_line(line.replace("-- ", "").replace("--", ""))

    # Block comments of the form /* */.
    elif line.strip().startswith("/*"):
      started_block_comment = True
      line = line.replace("/* ", "").replace("/*", "").strip()
       # See if they are now ending the block comment.
      if line.strip().endswith("*/"):
        started_block_comment = False
        line = line.replace(" */", "").replace("*/", "").strip()
      add_line(line)

    # Inline comment.
    elif started_sql and line.strip().startswith("--"):
      inline_comment += line + "\n"

    elif started_sql:
      responses[curr].sql += inline_comment
      inline_comment = ""
      responses[curr].sql += line + "\n"

    # Continuation of a response from a previous line, or the start of a SQL
    # statement. This could also contain comments.
    elif curr != "":
      started_sql = True
      responses[curr].sql += line + "\n"

  return responses


def parse_specs(assignment):
  """
  Function: parse_specs
  ---------------------
  Parse the specs for a given assignment.

  assignment: The assignment.
  returns: A JSON object containing the specs for that assignment.
  """
  path = ASSIGNMENT_DIR + assignment + "/" + assignment + "." + "spec"
  try:
    f = open(path, "r")
    specs = json.loads("".join(f.readlines()))
    f.close()
    return specs

  # If there are any errors finding or loading the spec file, exit.
  # Automation cannot continue until the proper spec file is found.
  except IOError:
    err("Could not find spec file: " + path)
  except ValueError as e:
    err("Could not parse spec file!\n" + str(e))
  sys.exit(1)
