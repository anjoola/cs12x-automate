from datetime import datetime
import json
from time import strftime

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



class GradedOutput:
  """
  Class: GradedOutput
  -------------------
  Contains the graded output. Has functions to convert such output into JSON.
  Contains the following fields:
    {
      "start": "",
      "end": "",
      "students": [...]
    }
  Each student is of the form:
    {
      "student": "",
    }
    TODO
  """
  def __init__(self):
    # Dictionary of fields.
    self.fields = {}

    # Set the start time for grading.
    self.fields["start"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # List of students graded.
    self.fields["students"] = []


  def jsonify(self):
    """
    Function: jsonify
    -----------------
    Convert the output into a JSON object.
    """
    # Set the end time for grading.
    self.fields["end"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    return json.dumps(self.fields, indent=2)

