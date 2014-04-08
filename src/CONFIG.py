"""
File: CONFIG.py
---------------
Contains configuration parameters for the grading tool.
"""
import secret
from errors import *
from problemtype import *

# Verbose output. Set to True for all logging statements.
VERBOSE = True

# Error output. Set to True for only error messages (if VERBOSE is False)
ERROR = True

# ----------------------------- Database Details ----------------------------- #

# The following 5 fields must be modified in the secret.py file.
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
  "delete" : Delete,
  "function": Function,
  "insert" : Insert,
  "procedure": Procedure,
  "select" : Select,
  "trigger" : Trigger,
  "view" : View,
  "manual" : Manual
}

# Deductions for SQL problems. Values are tuples of the form (points, desc)
# where points is the number of points to take off for this problem, and
# desc is the description of the style error.
SQL_DEDUCTIONS = {
  "OrderBy":          (1, "Missing ORDER BY."),
  "ColumnOrder":      (1, "Wrong column order."),
  "MissingResults":   (1, "Did not include query results."),
  "RenameValues":     (1, "Did not rename computed values."),
  "WrongNumColumns":  (0, "More or fewer columns included."),
  "GroupingSelect":   (2, "SELECTed something that was not grouped on.")
}

# Deductions for overall style mistakes. The key is the style error, and the
# value is the number of points to deduct overall for each mistake. None of
# these style errors should occur if they run the style checker and fix the
# errors.
STYLE_DEDUCTIONS = {
  BadHeaderError          : 0,  # Problem header not formatted correctly.
  UsedTabsError           : 5,  # Tabs should not be used for indentation.
  LineTooLongError        : 5,  # Lines should not be longer than 80 characters.
  SpaceError              : 2,  # Operators should have spaces around them.
  CodeBeforeHeaderError   : 0,  # No code should appear before problem headers.
  DoubleQuoteError        : 5   # Double quotes cannot be used for strings.
}
