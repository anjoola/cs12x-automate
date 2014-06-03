"""
Module: CONFIG
--------------
Contains configuration parameters for the grading tool.
"""
import secret
from errors import *

# Verbose output. Set to True for all logging statements.
VERBOSE = True

# Error output. Set to True for only error messages (if VERBOSE is False)
ERROR = True

# ----------------------------- Database Details ----------------------------- #

# The first 3 fields must be modified in the secret.py file.

# Database login information. Must be a dictionary with the username as the
# key and the password as the value.
LOGIN = secret.LOGIN

# Database host.
HOST = secret.HOST

# Database port.
PORT = secret.PORT

# Default database connection timeout (in seconds).
CONNECTION_TIMEOUT = 10

# Maximum timeout for any query.
MAX_TIMEOUT = 600

# ------------------------------ Grading Config ------------------------------ #

# Directory where all the assignment specs and student files are stored.
ASSIGNMENT_DIR = "../assignments/"

# Directory where results an assignment are stored.
RESULT_DIR = "_results/"

# Directory where the stylesheet and Javascripts are.
STYLE_DIR = "../style/"

# Maximum number of results to print out.
MAX_NUM_RESULTS = 100

# Deductions for SQL problems. Values are tuples of the form (points, desc)
# where points is the number of points to take off for this problem, and
# desc is the description of the style error.
SQL_DEDUCTIONS = {
  OrderByError            : 1,  # Missing or incorrect ORDER BY.
  ColumnOrderError        : 1,  # Wrong column order.
  RenameValueError        : 1,  # Did not rename computed values.
  WrongNumColumnError     : 0,  # More or fewer columns included.
  GroupingSelectError     : 2   # Selected on a column that was not grouped on.
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
