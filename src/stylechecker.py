import collections, os, re, sys

from errors import StyleError

MAX_LINE_LENGTH = 80

S                   = "[^\>\<\=\(\) \t\n\r\f\v]"

header              = re.compile("-- \[Problem (([0-9])+([a-zA-Z])*|[a-zA-Z])\]")
bad_header          = re.compile("-- \[Problem([^\]])*\]")
comment             = re.compile(r"\s*--.|/\*.|\*/.")
tabs                = re.compile(r"\t+")
comma_space         = re.compile(",[^ ][^\n]")
negative_num        = re.compile(r"\-([0-9]*\.?[0-9]+)")
count_star          = re.compile("\(\*\)|\(DISTINCT \*\)")
double_quote        = re.compile("\"([^\"])*\"")

class StyleChecker:
  """
  Class: StyleChecker
  -------------------
  Stylechecker for student submissions. Takes points off for violations. The
  regular expressions must be kept in sync with the ../check.py file.
  """
  # Whether or not a problem header has been encountered.
  has_header = False

  # If in a multi-line comment.
  multiline_comment = False

  # Dictionary where the key is the error name and the value is the number of
  # times that error occurred.
  errors = collections.defaultdict(int)

  @classmethod
  def check(cls, f):
    """
    Function: check
    --------------
    Checks for style violations.

    f: The file to check.
    returns: A list of style errors.
    """
    cls.errors = collections.defaultdict(int)
    lines = f.readlines()
    num_lines = len(lines)

    # Check every line.
    for i in range(num_lines):
      line = lines[i][:-1]
      cls.check_line(line, i + 1)

    error_list = []
    for e in cls.errors:
      string = StyleError.to_string(e, cls.errors[e], num_lines)
      error_list.append(string)
    return error_list


  @classmethod
  def check_line(cls, line, line_number):
    """
    Function: check_line
    --------------------
    Checks a line of a file for style violations.
  
    line: The line to check.
    line_number: The line number of the line to check.
    """
    is_bad_header = False

    if not len(line.strip()):
      return

    # Check for problem header formatting errors (cannot have code before a
    # problem header).
    if not cls.has_header and header.search(line):
      cls.has_header = True
    if not cls.has_header and line.strip().startswith("/*"):
      cls.multiline_comment = True
  
    # Check for style mistakes.
    if bad_header.search(line) and not header.search(line):
      cls.errors[StyleError.BAD_HEADER] += 1
      is_bad_header = True
    if tabs.search(line):
      cls.errors[StyleError.USED_TABS] += 1
    if len(line) > MAX_LINE_LENGTH:
      cls.errors[StyleError.LINE_TOO_LONG] += 1
    if not cls.multiline_comment and not comment.search(line):
      if comma_space.search(line):
        cls.errors[StyleError.SPACING] += 1
      if double_quote.search(line):
        cls.errors[StyleError.DOUBLE_QUOTES] += 1
  
    # Continue checking for problem header mistakes.
    if not (cls.has_header or cls.multiline_comment or is_bad_header or \
      comment.search(line.strip())):
      cls.errors[StyleError.CODE_BEFORE_PROBLEM_HEADER] += 1
    if line.strip().startswith("*/") or line.strip().endswith("*/"):
      cls.multiline_comment = False
