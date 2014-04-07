def add(lst, error):
  lst.append(error.__repr__())


def adds(lst, errors):
  for error in errors:
    lst.append(error.__repr__())


class DatabaseError(Exception):
  """
  Class: DatabaseError
  --------------------
  Represents an error that occurs with the database connection
  """

  def __init__(self, value):
    self.value = value

  def __repr__(self):
    return "Database Error: " + self.value


class DependencyError(Exception):
  """
  Class: DependencyError
  ----------------------
  Occurs when there is a problem with a dependent query.
  """

  def __init__(self, value):
    self.value = value

  def __repr__(self):
    return "DependencyError: One or more dependent problems (" + \
           (", ".join(self.value)) + ") had errors. Most likely all tests " + \
           "after this one will fail."


class FileNotFoundError(Exception):
  """
  Class: FileNotFoundError
  ------------------------
  Occurs when a file cannot be found for grading.
  """

  def __init__(self, value):
    self.value = value

  def __repr__(self):
    return "FileNotFoundError: File " + value + " could not be found."


class MySQLError(Exception):
  """
  Class: MySQLError
  -----------------
  Represents a MySQL error.
  """

  def __init__(self, value):
    self.value = value

  def __repr__(self):
    return "MySQL Error " + str(self.value)


class ParsingError(Exception):
  """
  Class: ParsingError
  -------------------
  Represents an error that occurs when parsing a student's file.
  """
  def __init__(self, value):
    self.value = value

  def __repr__(self):
    return "Parsing Error: " + self.value


class MissingKeywordError(Exception):
  """
  Class: MissingKeywordError
  --------------------------
  Occurs when a student is missing one or more keywords from their response.
  The value of the error is a list of keywords that were missing.
  """
  def __init__(self, value):
    self.value = value

  def __repr__(self):
    return "Missing Keyword" + ("s" if len(self.value) > 1 else "") + ": " + \
           ", ".join(self.value)
