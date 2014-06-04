"""
Module: models
--------------
Contains all models that are passed around and used in the automation tool.
"""

import json
from datetime import datetime
from time import strftime

import iotools

class DatabaseState:
  """
  Class: DatabaseState
  --------------------
  Represents the state of the database, which includes the functions,
  procedures, tables, foreign keys, and views.
  """
  def __init__(self):
    # A list of tables.
    self.tables = []

    # A list of foreign keys. In the form of (table, foreign key name).
    self.foreign_keys = []

    # A list of views.
    self.views = []

    # A list of functions.
    self.functions = []

    # A list of procedures.
    self.procedures = []


  def subtract(self, other):
    """
    Function: subtract
    --------------
    Removes the elements that are the same between this DatabaseState and
    another one.

    other: The other database state.
    """

    def diff(a, b):
      return [x for x in a if x not in b]

    self.tables = diff(self.tables, other.tables)
    self.foreign_keys = diff(self.foreign_keys, other.foreign_keys)
    self.views = diff(self.views, other.views)
    self.functions = diff(self.functions, other.functions)
    self.procedures = diff(self.procedures, other.procedures)



class GradedOutput:
  """
  Class: GradedOutput
  -------------------
  Contains the graded output. Has functions to convert such output into JSON.
  Contains the following fields: TODO this needs to change.....
    {
      "start": "",
      "end": "",
      "students": [...]
    }
  Each student is of the form:
    {
      "name": "",
      "files": [...]
    }
  Each file is of the form:
    {
      "filename": ""
      "got_points": 0,
      "errors": [""],
      "problems": [...]
    }
  Each problem is of the form:
    {
      "num": "",
      "num_points": 0,
      "errors": [],
      "got_points" 0,
      "sql": "",
      
      
    TODO should check this
  """
  def __init__(self, specs):
    # Dictionary of fields.
    self.fields = {}

    # Set the start time for grading.
    self.fields["start"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # List of students graded.
    self.fields["students"] = []

    # List of files to grade.
    self.fields["files"] = specs["files"]


  def jsonify(self):
    """
    Function: jsonify
    -----------------
    Convert the output into a JSON object.
    """
    # Set the end time for grading.
    self.fields["end"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    return json.dumps(self.fields, indent=2)



class Response:
  """
  Class: Response
  ---------------
  Represents a student's response to a particular homework problem. The
  response includes any comments before the SQL and the actual SQL response.
  """
  def __init__(self):
    # Their comments.
    self.comments = ""

    # The SQL for that problem.
    self.sql = ""


  def __repr__(self):
    return self.__str__()


  def __str__(self):
    return "(" + self.comments + ", " + self.sql + ")"



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
    self.results = []

    # Pretty-formatted output to print.
    self.output = ""


  def __repr__(self):
    return self.__str__()


  def __str__(self):
    return "(" + str(self.schema) + ", " + str(self.results) + ", " + \
      self.output + ")"


  def append(self, other):
    """
    Function: append
    ----------------
    Appends two results together. The schema and column names must be the same.

    returns: The newly-modified Result object.
    """
    assert(self.col_names == other.col_names)
    self.results += other.results
    self.output = iotools.prettyprint(self.results, self.col_names)
    return self


  def subtract(self, other):
    """
    Function: subtract
    ------------------
    Subtracts two results from each other. The schema and column name must be
    the same. Keeps rows from the current Result.

    returns: The newly-modified Result object.
    """
    assert(self.col_names == other.col_names)
    self.results = filter(lambda row: row not in other.results, self.results)
    self.output = iotools.prettyprint(self.results, self.col_names)
    return self
