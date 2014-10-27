"""
Module: errors
--------------
Contains all of the possible errors that can occur during the execution of the
automation tool.
"""
from math import ceil

import mysql.connector.errors

def add(lst, error):
  """
  Function: add
  -------------
  Adds the string representation of 'error' to the list of errors 'lst'.

  lst: The list of errors.
  error: The error object.
  """
  lst.append(repr(error))



class Error(Exception):
  """
  Class: Error
  ------------
  Generic error class for the automation tool.
  """
  pass



class FileNotFoundError(Error):
  """
  Class: FileNotFoundError
  ------------------------
  Occurs when a file cannot be found for grading.
  """
  def __init__(self, filename):
    self.filename = filename

  def __repr__(self):
    return "FileNotFoundError: File %s could not be found." % self.filename

# ------------------------------ Grading Errors ----------------------------- #

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
    "There is code before a problem header! There will probably be major " +
    "point deductions for all problems in this file."
  )
  DOUBLE_QUOTES = (
    "DoubleQuoteError", 3, 5,
    "Double-quotes instead of single-quotes were used for strings."
  )
  LINE_TOO_LONG = (
    "LineTooLongError", 0.1, 5,
    "There are too many lines longer than 80 characters."
  )
  SPACING = (
    "SpacingError", 2, 5,
    "Did not use spaces after commas."
  )
  USED_TABS = (
    "UsedTabsError", 0.2, 5,
    "Tabs instead of spaces were used."
  )
  WRONG_ENCODING = (
    "WrongEncodingError", 0, 0,
    "File has the wrong encoding. Grading has proceeded but might get " +
    "strange errors."
  )

  @staticmethod
  def to_string(error, num_occurrences, num_lines):
    """
    Function: to_string
    -------------------
    Gets the description of an error as a string.

    error: The error to get the description of.
    num_occurrences: The number of times this error has appeared.
    returns: The description as a string if a deduction is necessary, otherwise
             returns None.
    """
    # Get the number of lines the error has to occur in order for a deduction
    # to happen.
    times = int(error[1] * num_lines) if error[1] < 1 else error[1]
    if num_occurrences >= times:
      return "%s [-%d suggested]: %s" % (error[0], error[2], error[3])
    else:
      return "<i>%s [-0]: %s</i> [Did not occur often]" % (error[0], error[3])



class QueryError(Error):
  """
  Class: QueryError
  -----------------
  A query-related error that occurs if something is wrong with the student's
  query. Each error is a tuple of the form
  (error name, point deduction, proportion, long description), where
  the 'proportion' is the proportion of the problem's points to take off.

  For example, if 'proportion' is set to 0.5 and the problem is worth 10 points,
  then 5 points are deducted. If 'proportion' is set to 1, then the number of
  points deducted is equal to 'point deduction'.
  """
  BAD_QUERY = (
    "BadQueryError", 0, 0,
    "Query might be bad because it is empty, contains unexpected SQL or " +
    "extra stuff before or after. <b>This might need to be manually graded</b>."
  )
  COLUMN_ORDER = (
    "ColumnOrderError", 1, 0.3,
    "Columns are in the wrong order."
  )
  INCORRECT_VIEW_NAME = (
    "IncorrectViewNameError", 0, 0,
    "View was not named correctly."
  )
  MALFORMED_CREATE_STATEMENT = (
    "MalformedCreateStatementError", 0, 0,
    "CREATE statement not formatted correctly."
  )
  NOT_UPDATABLE = (
    "ViewNotUpdatableError", 2, 0.5,
    "View is not updatable but should be."
  )
  ORDER_BY = (
    "OrderByError", 1, 0.3,
    "Missing or incorrect ORDER BY statement."
  )
  RENAME_VALUE = (
    "RenameValueError", 1, 0.3,
    "Did not rename computed values."
  )
  WRONG_NUM_COLUMNS = (
    "WrongNumColumnsError", 0, 0,
    "More or fewer columns included."
  )

  @staticmethod
  def deduction(error, points):
    """
    Function: deduction
    -------------------
    Gets the number of points to deduct for a specific query error.

    error: The query error.
    points: The number of points a problem is worth.

    returns: The number of points to deduct.
    """
    # Figure out how many points to deduct. If it is an integer number of
    # points, don't deduct more points than the problem is worth.
    deduct = ceil(error[2] * points) if error[2] < 1 else max(points, error[1])
    return int(deduct)


  @staticmethod
  def to_string(error, points):
    """
    Function: to_string
    -------------------
    Gets the description of an error as a string.

    error: The error to get the description of.
    points: The number of points a problem is worth.

    returns: The description as a string.
    """
    deduct = QueryError.deduction(error, points)
    return "%s [-%d]: %s" % (error[0], deduct, error[3])

# ----------------------------- Database Errors ----------------------------- #

class DatabaseError(Error):
  """
  Class: DatabaseError
  --------------------
  Represents any error that occurs with the database, either user or client
  errors as listed in:
  - http://dev.mysql.com/doc/refman/5.7/en/error-messages-server.html
  - http://dev.mysql.com/doc/refman/5.7/en/error-messages-client.html
  """
  def __init__(self, error):
    # The MySQL error number.
    self.errno = error.errno

    # The message to print.
    self.msg = error.msg


  def __repr__(self):
    return "DatabaseError (%d): %s" % (self.errno, self.msg)


  def __str__(self):
    return repr(self)



class DependencyError(DatabaseError):
  """
  Class: DependencyError
  ----------------------
  Occurs when there is a problem with a dependent query.
  """
  def __init__(self, dep_file, num, error):
    # The dependent file.
    self.f = dep_file

    # The problem number in the file.
    self.num = num

    # The database error that occurred.
    self.errno = error.errno

    # The message for the database error.
    self.msg = error.msg


  def __repr__(self):
    return ("DependencyError (%d): Dependent query from problem %s in file " +
            "%s got error \"%s\".") % (self.errno, self.num, self.f, self.msg)



class MissingKeywordError(Error):
  """
  Class: MissingKeywordError
  --------------------------
  Occurs when a student is missing one or more keywords from their response.
  The value of the error is a list of keywords that were missing.
  """
  def __init__(self, keywords):
    # The list of keywords that are missing.
    self.keywords = keywords


  def __repr__(self):
    return "MissingKeywordError: Keyword" + \
           ("s" if len(self.keywords) > 1 else "") + " " + \
           ", ".join(self.keywords) + " missing from query."



class TimeoutError(DatabaseError):
  """
  Class: TimeoutError
  -------------------
  Occurs when a query times out.
  """
  def __init__(self):
    pass


  def __repr__(self):
    return "TimeoutError: Query timed out."
