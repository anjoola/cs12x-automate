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
  
  """
  def __init__(self):
    # Dictionary of fields.
    self.fields = {}

    # Set the start time for grading.
    self.fields["start"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    
    self.fields["students"] = []



  def jsonify(self):
    """
    Function: jsonify
    -----------------
    Convert the output into a JSON object.
    """
    # Set the end time for grading.
    self.fields["end"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    #fields["students"] = []
    #for student in student:
    #  fields["students"].append(student.get_fields())

    return json.dumps(self.fields, indent=2)


############### TODO REMOVE
class GradedStudent:
  """
  Class: GradedStudent
  --------------------
  Graded output for a particular student. Contains the following fields:
  
  TODO
  """
  def __init__(self, name):
    # Dictionary of fields.
    self.fields = {}

    # List of graded files.
    self.files = []
    
  def add(self, f):
    """
    Function: add
    -------------
    TODO
    """
    self.files.append(f)
    
    
  def get_fields(self):
    pass
  
  
    
class GradedFile:
  """
  Class: GradedFile
  -----------------
  Graded output for a particular file. Contains the following fields:
  
  TODO
    {
      "filename": "",
      "total_points": 0,
      "problems": [GradedProblem]
    }
  """
  def __init__(self, filename):
    self.fields = {}
    self.fields["filename"] = filename
    self.fields["total_points"] = 0
    
    self.problems = []
    
    
  def add(self, problem):
    self.problems.append(problem)
    
    
  def get_fields(self):
    pass
  
  
class GradedProblem:
  """
  Class: GradedProblem
  --------------------
  Graded output for a particular problem. Contains the following fields:
  
   TODO
  """
  def __init__(self, num):
    # Dictionary of fields.
    self.fields = {}
    self.fields["num"] = num
    
############ TODO REMOVE 
    
    