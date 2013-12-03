"""
Module: iotools
---------------
Functions involving input and output into the system, as well as file-related
functions.
"""

from datetime import datetime
import dbtools
import formatter
import json
import os
from os.path import getmtime
from models import Response
from time import strftime

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
  files = [f for f in os.walk(assignment + "/").next()[1] \
    if f.endswith("-" + assignment)]

  # If looking for files after a particular person.
  if after is not None:
    # Sort the files such that the newest are first, then take a slice of
    # that list so only the newest files are there.
    files = sorted(files, key=lambda f: getmtime(assignment + "/" + f), \
      reverse=True)
    files = files[0:files.index(after + "-" + assignment)+1]

  return [f.replace("-" + assignment, "") for f in files]


def output(json, specs):
  """
  Function: output
  ----------------
  Outputs the graded output to a file.

  json: The graded output.
  specs: The assignment specs.
  returns: The file where the output was written to.
  """
  path = specs["assignment"] + "/_results/"
  if not os.path.exists(path):
    os.mkdir(path, 0644)
    # TODO .html or .md
  f = open(path + "index.html", "w")
  #f = open(path + datetime.now().strftime("%Y-%m-%d+%H;%M;%S") + ".html", "w")

  # Format the output nicely before writing it.
  f.write(formatter.html(json, specs)) # TODO let user be able to specify md or html
  f.close()
  return f


def parse_file(f):
  """
  Function: parse_file
  --------------------
  Parses the file into a dict of the question number and the student's response
  to that question. Parses their comments, query, and query results.

  f: The file object to parse.
  returns: The dict of the question number and student's response.
  """

  # Dictionary containing a mapping from the problem number to the response.
  responses = {}
  # The current problem number being parsed.
  curr = ""
  # True if in the middle of parsing a block comment.
  started_block_comment = False
  # True if in the middle of parsing results.
  started_results = False
  # True if in the middle of parsing SQL.
  started_sql = False

  def add_line(line):
    """
    Function: add_line
    ------------------
    Adds a line to the results or comments depending on where we are at parsing.
    """
    # If these are comments at the top of the file, ignore them.
    if curr == "":
      return
    #if len(line.strip()) > 0:
    line = line + "\n"
    if started_results:
      responses[curr].results += line
    else:
      responses[curr].comments += line

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

    # Query results.
    elif line.strip().startswith("-- [Results]"):
      started_results = True

    # Indicator denoting the start of an response.
    elif line.strip().startswith("-- [Problem ") and line.strip().endswith("]"):
      started_results = False
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
  f = open(assignment + "/" + assignment + "." + "spec", "r")
  specs = json.loads("".join(f.readlines()))
  f.close()
  return specs
