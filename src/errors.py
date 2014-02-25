class DatabaseError(Exception):
  """
  Class: DatabaseError
  --------------------
  Represents an error that occurs with the database connection
  """

  def __init__(self, value):
    self.value = value

  def __str__(self):
    return "Database Error: " + self.value


class ParsingError(Exception):
  """
  Class: ParsingError
  -------------------
  Represents an error that occurs when parsing a student's file.
  """
  def __init__(self, value):
    self.value = value

  def __str__(self):
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

  def __str__(self):
    return "Parsing Error: " + ", ".join(self.value)





