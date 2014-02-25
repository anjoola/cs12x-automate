class Response:
  """
  Class: Response
  ---------------
  Represents a student's response to a particular homework problem.
  """
  def __init__(self):
    # Their comments (if required).
    self.comments = ""

    # The SQL for that problem.
    self.sql = ""

    # The results of the query (if required).
    self.results = ""

  def __repr__(self):
    return self.__str__()

  def __str__(self):
    return "(" + self.comments + ", " + self.sql + ", " + self.results + ")"


class Result:
  """
  Class: Result
  -------------
  Represents the result of a query.
  """
  def __init__(self):
    # The schema of the result.
    self.schema = []

    # The column names of the result.
    self.col_names = []

    # The actual results.
    self.results = None

    # Pretty-formatted output to print.
    self.output = ""

  def __repr__(self):
    return self.__str__()

  def __str__(self):
    return "(" + str(self.schema) + ", " + str(self.results) + ", " + \
      self.output + ")"
