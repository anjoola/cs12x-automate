"""
File: CONFIG.py
---------------
Contains configuration parameters for the grading tool.
"""
import secret
from problemtype import *

# Verbose output.
VERBOSE = True

# ----------------------------- Database Details ----------------------------- #

# Database username.
USER = secret.USER

# Database password.
PASS = secret.PASS

# Database host.
HOST = secret.HOST

# Database port.
PORT = secret.PORT

# Database name.
DATABASE = secret.DATABASE

# Default database connection timeout (in seconds).
CONNECTION_TIMEOUT = 10

# Maximum timeout for any query.
MAX_TIMEOUT = 600

# ------------------------------ Grading Config ------------------------------ #

# Directory where all the assignment specs and student files are stored.
ASSIGNMENT_DIR = "../assignments/"

# Maximum number of results to print out.
MAX_NUM_RESULTS = 100

# The types of problems there are and the classes to handle each type.
PROBLEM_TYPES = {
  "create" : Create,
  "select" : Select,
  "insert" : Insert,
  "trigger" : Trigger,
  "function": Function,
  "procedure": Procedure
}



#### TODO clean up below
# Deductions for overall style problems. Values are tuples of the form
# (points, message) where points is the number of points taken off overall, and
# desc is the description of the style error.
STYLE_DEDUCTIONS = {
  "80char": (5, "Too many lines over 80 characters!"),
  "doublequotes": (3, "Double-quoting instead of single-quoting strings!"),
  "semicolon": (3, "Missing semicolons at the end of the commands!")
}

# Deductions for SQL problems. Values are tuples of the form (points, desc)
# where points is the number of points to take off for this problem, and
# desc is the description of the style error.
SQL_DEDUCTIONS = {
  "orderby": (1, "Missing ORDER BY."),
  "columnorder": (1, "Wrong column order."),
  "missingresults": (1, "Forgot to include results."),
  "renamecolumns": (1, "Did not rename computed values."),
  "missingcols": (1, "More or fewer columns than the question asked for."),
  "groupingselect": (2, "Can only SELECT on things that are being grouped by.")
}

