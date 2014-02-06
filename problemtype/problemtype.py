from errors import *

class ProblemType(object):
  """
  Class: ProblemType
  ------------------
  A generic problem type. To be implemented for specific types of problems.
  """

  def __init__(self, specs, response, output):
    # The specifications for this problem.
    self.specs = specs

    # The student's response for this problem.
    self.response = response

    # The graded problem output.
    self.output = output


  def preprocess(self):
    """
    Function: preprocess
    --------------------
    Check for certain things before running the tests and add them to the
    graded problem output. This includes:
      - Comments
      - Attaching results of query
      - Checking their SQL for certain keywords
      - Printing out their actual SQL
    """
    # Comments, query results, and SQL.
    self.output["comments"] = self.response.comments
    self.output["submitted-results"] = self.response.results
    self.output["sql"] = self.response.sql

    # Check if they included certain keywords.
    if self.specs.get("keywords"):
      missing = False
      missing_keywords = []
      for keyword in self.specs["keywords"]:
        if keyword not in self.response.sql:
          missing = True
          missing_keywords.append(keyword)
      if missing:
        self.output["errors"].append(MissingKeywordError(missing_keywords))
        # TODO need to convert this to a string later? using repr


  def grade(self):
    """
    Function: grade
    ---------------
    Runs all the tests for a particular problem and computes the number of
    points received for this response.

    returns: The number of points received for this response.
    """

    # Problem definitions and preprocessing.
    number = problem["number"]
    num_points = problem["points"]
    self.preprocess()










    # The number of points this student has received so far on this problem.
    got_points = num_points
    
  
    return 0


class Function(ProblemType):
  def grade(self):
    super(Function, self).grade()