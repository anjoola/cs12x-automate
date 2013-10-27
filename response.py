class Response:
  """
  Class: Response
  ---------------
  Represents a response to a problem on the homework, including the query and
  the comments for the query.
  """
  def __init__(self):
    self.comments = ""
    self.query = ""

  def __repr__(self):
    return self.__str__()

  def __str__(self):
    return "(" + self.comments + ", " + self.query + ")"
