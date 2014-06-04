"""
Module: errors
--------------
Contains all of the possible errors that can occur in the execution of the
automation tool.
"""
# TODO remove all of this
def add(lst, error):
  """
  Function: add
  -------------
  Adds the string representation of 'error' to the list of errors 'lst'.

  lst: The list of errors.
  error: The error object.
  """
  lst.append(repr(error))


def adds(lst, errors):
  """
  Function: adds
  --------------
  Adds the string representation of each error in 'errors' to the list of
  errors 'lst'.
  """
  for error in errors:
    lst.append(repr(error))


class Error(Exception):
  """
  Class: Error
  ------------
  Error class for the automation tool.
  """
  pass

# -------------------------- Error Implementations -------------------------- #

class StyleError(Error):
  """
  Class: StyleError
  -----------------
  A style-related error which occurs if an error occurs with the stylechecker
  or there is a problem parsing the student's file. Each error is a tuple of
  the form (error name, point deduction, frequency, long description), where
  a deduction occurs after an error occurs at a certain frequency.

  If 'frequency' is set to an integer, then a deduction will occur after that
  many instances of that error. If it is set to a decimal (between 0 and 1),
  then a deduction will occur after that proportion of lines have that error.
  """
  BAD_HEADER = (
    "BadHeaderError", 0, 1,
    "Problem header not formatted correctly."
  )

  CODE_BEFORE_PROBLEM_HEADER = (
    "CodeBeforeProblemHeaderError", 0, 1,
    "There is code before a problem header! There will probably be major " + \
    "point deductions for all problems in this file."
  )

  DOUBLE_QUOTES = (
    "DoubleQuoteError", 3, 3,
    "Double-quotes instead of single-quotes were used for strings."
  )

  LINE_TOO_LONG = (
    "LineTooLongError", 0.1, 5,
    "There are too many lines longer than 80 characters."
  )

  SPACING = (
    "SpacingError", 5, 2,
    "Did not use spaces after operators."
  )

  USED_TABS = (
    "UsedTabsError", 0.2, 5,
    "Tabs instead of spaces were used."
  )

  @staticmethod
  def deduction(error, num_occurrences, num_lines):
    """
    Function: deduction
    -------------------
    Gets the number of points to deduct for a specific style error.

    error: The style error.
    num_occurrences: The number of times the error has occurred.
    num_lines: The number of lines in the file to grade.

    returns: The number of points to deduct.
    """
    # Get the number of lines the error has to occur in order for a deduction
    # to happen.
    times = int(error[1] * num_lines) if error[1] < 1 else error[1]
    return error[2] if num_occurrences >= times else 0


  @staticmethod
  def to_string(error):
    """
    Function: to_string
    -------------------
    Gets the description of an error as a string.

    error: The error to get the description of.
    returns: The description as a string.
    """
    return "%s: %s" % (error[0], error[3])



"""
SQL_DEDUCTIONS = {
  "OrderByError"           : 1,  # Missing or incorrect ORDER BY.
  "ColumnOrderError"       : 1,  # Wrong column order.
  "RenameValueError"       : 1,  # Did not rename computed values.
  "WrongNumsColumnError"   : 0,  # More or fewer columns included.
  "GroupingSelectError"    : 2   # Selected on a column that was not grouped on.
}
"""

class QueryError(Error):
  """
  Class: QueryError
  -----------------
  A query-related error that occurs if something is wrong with the student's
  query.
  """
  COLUMN_ORDER = "ColumnOrderError: Columns are in the wrong order."

  ORDER_BY = "OrderByError: Missing or incorrect ORDER BY statement."

  RENAME_VALUE = "RenameValueError: Did not rename computed values."

  WRONG_NUM_COLUMNS = "WrongNumColumnsError: More or fewer columns included."




class DatabaseError(Error):
  """
  Class: DatabaseError
  --------------------
  Represents an error that occurs with the database connection
  """
  def __init__(self, value):
    self.value = value

  def __repr__(self):
    return "Database Error: " + self.value


class DependencyError(Error):
  """
  Class: DependencyError
  ----------------------
  Occurs when there is a problem with a dependent query.
  """
  def __init__(self, problems):
    self.problems = problems

  def __repr__(self):
    return "DependencyError: One or more dependent problems (" + \
           (", ".join(self.problems)) + ") had errors. Most likely all " + \
           "tests after this one will fail."


class FileNotFoundError(Error):
  """
  Class: FileNotFoundError
  ------------------------
  Occurs when a file cannot be found for grading.
  """
  def __init__(self, filename):
    self.filename = filename

  def __repr__(self):
    return "FileNotFoundError: File " + self.filename + " could not be found."


class GroupingSelectError(Error):
  """
  Class: GroupingSelectError
  --------------------------
  Occurs when a query selects on a column that was not grouped on.
  """
  def __repr__(self):
    return "GroupingSelectError: Selected on a column that was not grouped on."



class MissingKeywordError(Error):
  """
  Class: MissingKeywordError
  --------------------------
  Occurs when a student is missing one or more keywords from their response.
  The value of the error is a list of keywords that were missing.
  """
  def __init__(self, keywords):
    self.keywords = keywords

  def __repr__(self):
    return "MissingKeywordError: Keyword" + \
           ("s" if len(self.keywords) > 1 else "") + ": " + \
           ", ".join(self.keywords)


class MySQLError(Error):
  """
  Class: MySQLError
  -----------------
  Represents a MySQL error.
  """
  def __init__(self, value):
    self.value = value

  def __repr__(self):
    return "MySQL Error " + str(self.value)



class ParsingError(Error):
  """
  Class: ParsingError
  -------------------
  Represents an error that occurs when parsing a student's file.
  """
  def __init__(self, value):
    self.value = value

  def __repr__(self):
    return "ParsingError: " + self.value

