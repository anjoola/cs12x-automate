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
  "80char": (5, "Too many lines over 80 characters!"), \
  "doublequotes": (3, "Double-quoting instead of single-quoting strings!"), \
  "semicolon": (3, "Missing semicolons at the end of the commands!")
}