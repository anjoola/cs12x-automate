"""
Module: models
--------------
Contains all models that are passed around and used in the automation tool.
"""

import json
from copy import deepcopy
from datetime import datetime
from time import strftime

import iotools

class DatabaseState:
  """
  Class: DatabaseState
  --------------------
  Represents the state of the database, which includes the tables, foreign keys,
  views, functions, procedures, and triggers.
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

    # A list of triggers.
    self.triggers = []


  def __repr__(self):
    return "Tables: " + str(self.tables) + "\n" + \
           "Foreign Keys: " + str(self.foreign_keys) + "\n" + \
           "Views: " + str(self.views) + "\n" + \
           "Functions: " + str(self.functions) + "\n" + \
           "Procedures: " + str(self.procedures) + "\n" + \
           "Triggers: " + str(self.triggers)


  def subtract(self, other):
    """
    Function: subtract
    --------------
    Removes the elements that are the same between this DatabaseState and
    another one.

    other: The other database state.
    """

    def diff(a, b):
      # Returns the diff between a and b, if a is non-empty.
      try:
        return [x for x in a if x not in b]
      except TypeError:
        return []

    self.tables = diff(self.tables, other.tables)
    self.foreign_keys = diff(self.foreign_keys, other.foreign_keys)
    self.views = diff(self.views, other.views)
    self.functions = diff(self.functions, other.functions)
    self.procedures = diff(self.procedures, other.procedures)
    self.triggers = diff(self.triggers, other.triggers)



class GradedOutput:
  """
  Class: GradedOutput
  -------------------
  Contains the graded output. Has functions to convert such output into JSON.
  Format of the output can be found in the wiki.
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
    assert(self.col_names == other.col_names or len(other.col_names) == 0)
    new_result = deepcopy(self)
    new_result.results += other.results
    new_result.output = iotools.prettyprint(new_result.results,
                                            new_result.col_names)
    return new_result


  def subtract(self, other):
    """
    Function: subtract
    ------------------
    Subtracts two results from each other. The schema and column name must be
    the same. Keeps rows from the current Result.

    returns: The newly-modified Result object.
    """
    if len(self.col_names) == 0:
      return self
    assert(self.col_names == other.col_names or len(other.col_names) == 0)

    new_result = deepcopy(self)
    results = filter(lambda row: row not in other.results, new_result.results)
    if len(results) != 0:
      new_result.results = results
      new_result.output = iotools.prettyprint(new_result.results,
                                              new_result.col_names)
    # If the result of the subtraction is nothing, then indicate it.
    else:
      new_result.results = []
      new_result.output = ""
    return new_result
