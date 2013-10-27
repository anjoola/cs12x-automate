"""
Module: iotools
---------------
TODO
"""

import json
import os
from response import Response

def format_lines(lines):
  """
  Function: format_lines
  ----------------------
  Print out lines in a nice formatted way. Gets rid of extra spacing.

  lines: The lines to print and format.
  """
  print "\n+ " + ("\n+ ").join( \
    filter(None, [line.strip() for line in lines.split("\n")])) + "\n"


def get_students(assignment):
  # TODO grade students who'ev submitted after a given time
  """
  Function: get_students
  ----------------------
  Gets all the students for a given assignment.

  assignment: The assignment.
  returns: A list of students who've submitted for that assignment.
  """
  return [f for f in os.walk(assignment + "/").next()[1] \
    if f.endswith("-" + assignment)]


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


def parse_file(f):
  """
  Function: parse_file
  --------------------
  Parses the file into a dict of the question number and the student's response
  to that question.

  f: The file object to parse.
  returns: The dict of the question number and student's response.
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
      responses[current_problem] = Response()

    # Lines with comments.
    elif line.startswith("--"):
      responses[current_problem].comments += \
        line.replace("-- ", "").replace("--", "")

    # Continuation of a response from a previous line.
    else:
      responses[current_problem].query += line

  return responses
