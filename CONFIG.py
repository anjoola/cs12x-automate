"""
File: CONFIG.py
---------------
Contains configuration parameters for the grading tool.
"""

# Database username.
USER = "angela"

# Database password.
PASS = "cs121"

# Database host.
HOST = "sloppy.cs.caltech.edu"

# Database port.
PORT = "4306"

# Database name.
DATABASE = "angela_db"

# Deductions for overall style problems. Values are tuples of the form
# (points, message) where points is the number of points taken off overall, and
# desc is the description of the style error.
STYLE_DEDUCTIONS = {
  "80char": (5, "Too many lines over 80 characters!"),
  "doublequotes": (3, "Double-quoting instead of single-quoting strings!"),
  "semicolon": (3, "Missing semicolons at the end of the commands!")
}

# Deductions for SQL problems. Values are tuples of the form (points, desc)
# where points it he number of points to take off for this problem, and
# desc is the description of the style error.
SQL_DEDUCTIONS = {
  "orderby": (1, "Missing ORDER BY."),
  "columnorder": (1, "Wrong column order."),
  "missingresults": (1, "Forgot to include results."),
  "renamecolumns": (1, "Did not rename computed values."),
  "missingcols": (1, "More or fewer columns than the question asked for."),
  "groupingselect": (2, "Can only SELECT on things that are being grouped by.")
}

# Type of tests to output for. This should not be modified unless the code
# is also modified.
TYPE_OUTPUTS = ["select", "stored-procedure"]
