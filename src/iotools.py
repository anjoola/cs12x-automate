"""
Module: iotools
---------------
Functions involving input and output into the system, as well as file-related
functions.
"""
import json
import os
import sys
import time
from datetime import datetime
from os.path import getmtime

import prettytable

import dbtools
import formatter
import sqltools
from CONFIG import *
from models import Response

# --------------------------- Debugging Utilities --------------------------- #

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

# ---------------------------------- Other ---------------------------------- #

def get_students(assignment, after=None):
  """
  Function: get_students
  ----------------------
  Gets all the students for a given assignment.

  assignment: The assignment.
  after: The date after which to find submissions. Will find all students
         who've submitted after this date.
  returns: A list of students who've submitted for that assignment.
  """
  directory = ASSIGNMENT_DIR + assignment + "/" + STUDENT_DIR
  files = [f for f in os.walk(directory).next()[1]
           if f.endswith("-" + assignment)]

  # If looking for files after a particular date.
  if after is not None:
    try:
      after = time.mktime(time.strptime(after, "%Y-%m-%d"))
      files = [f for f in files if getmtime(directory + f) >= after]

    # If the string they entered for the date is incorrect, just skip the date
    # filtering.
    except ValueError:
      err("'after' parameter not formatted correctly (must be YYYY-MM-DD)")
      pass

  return [f.replace("-" + assignment, "") for f in files]


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
  path = ASSIGNMENT_DIR + specs["assignment"] + "/" + RESULT_DIR
  if not os.path.exists(path):
    os.mkdir(path, 0644)

  if not os.path.exists(path + FILE_DIR):
    os.mkdir(path + FILE_DIR, 0644)

  f = None
  # For the raw, JSON output.
  if raw:
    f = open(path + datetime.now().strftime("%Y-%m-%d+%H;%M;%S") + ".json", "w")
    f.write(str(json))

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
    line = line + "\n"
    responses[curr].comments += line

  inline_comment = ""
  # Preprocess the file for DELIMITER statements.
  f = sqltools.preprocess_sql(f)
  for line in f.split("\n"):
    # Remove tabs.
    line = line.replace("\t", "    ")

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
      inline_comment = ""

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
    err("Could not find spec file: " + path, True)
  except ValueError as e:
    err("Could not parse spec file!\n" + str(e), True)


def prettyprint(results, col_names):
  """
  Function: prettyprint
  ---------------------
  Gets the pretty-printed version of the results.

  results: The results to pretty-print.
  col_names: The column names for the results.
  returns: A string contained the pretty-printed results.
  """
  # If the results are too long, don't print it.
  if len(results) > MAX_NUM_RESULTS:
    return "Too many results (%d) to print!" % len(results)

  output = prettytable.PrettyTable(col_names)
  output.align = "l"
  for row in results:
    output.add_row(row)
  return output.get_string()
