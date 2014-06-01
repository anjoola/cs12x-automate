"""
Module: errors
--------------
Contains all of the possible errors.
"""

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

class BadHeaderError(Error):
  """
  Class: BadHeaderError
  ---------------------
  Indicates that a problem header was not formatted correctly.
  """
  def __repr__(self):
    return "BadHeaderError: Problem header was not formatted correctly."


class CodeBeforeHeaderError(Error):
  """
  Class: CodeBeforeHeaderError
  ----------------------------
  Occurs if there is code before a problem header.
  """
  def __repr__(self):
    return "CodeBeforeHeaderError: There is code before a problem header! " + \
           "There will probably be major point deductions for all problems" + \
           " in this file."


class ColumnOrderError(Error):
  """
  Class: ColumnOrderError
  -----------------------
  Occurs if the query produces results in the wrong column order.
  """
  def __repr__(self):
    return "ColumnOrderError: Columns are in the wrong order."


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


class DoubleQuoteError(Error):
  """
  Class: DoubleQuoteError
  -----------------------
  Occurs if a SQL string is enclosed by double-quotes instead of single-quotes.
  """
  def __repr__(self):
    return "DoubleQuoteError: Double-quotes were used for a string!"


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


class LineTooLongError(Error):
  """
  Class: LineTooLongError
  -----------------------
  Occurs if the file has lines that are longer than 80 characters.
  """
  def __repr__(self):
    return "LineTooLongError: There are lines of code longer than 80 " + \
           "characters."


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


class OrderByError(Error):
  """
  Class: OrderByError
  -------------------
  Occurs when the results are not in the right order.
  """
  def __repr__(self):
    return "OrderByError: Missing or incorrect ORDER BY statement."


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


class RenameValueError(Error):
  """
  Class: RenameValueError
  -----------------------
  The query did not rename computed values.
  """
  def __repr__(self):
    return "RenameValueError: Did not rename computed values."


class SpaceError(Error):
  """
  Class: SpaceError
  -----------------
  Occurs if there are no spaces before and after operators or after a comma.
  """
  def __repr__(self):
    return "SpaceError: No spaces after operators!"


class UsedTabsError(Error):
  """
  Class: UsedTabsError
  --------------------
  Occurs if a tabs are used in a file instead of spaces.
  """
  def __repr__(self):
    return "UsedTabsError: Tabs were used."


class WrongNumColumnError(Error):
  """
  Class: WrongNumColumnError
  --------------------------
  Occurs if the students provides more or fewer columns than required.
  """
  def __repr__(self):
    return "WrongNumColumnError: More or fewer columns included."
