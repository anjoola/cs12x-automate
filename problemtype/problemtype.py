from errors import *

TYPES = {
  "create" : Create,
  "select" : Select,
  "insert" : Insert,
  "trigger" : Trigger,
  "function": Function,
  "procedure": Procedure
}

class ProblemType(object):
  """
  Class: ProblemType
  ------------------
  A generic problem type. To be implemented for specific types of problems.
  """

  def __init__(self, db, specs, response, output, cache):
    # The database connection.
    self.db = db

    # The specifications for this problem.
    self.specs = specs

    # The student's response for this problem.
    self.response = response

    # The graded problem output.
    self.output = output

    # Cache to store results of query runs to avoid having to run the same
    # query multiple times.
    self.cache = cache

    # The problem number.
    self.num = self.specs["number"]

    # The number of points this problem is worth.
    self.points = self.specs["points"]

    # The number of points the student has gotten on this question. They start
    # out with the maximum number of points, and points get deducted as the
    # tests go on.
    self.got_points = self.points


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
      if missing: # TODO errors
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
    # Run each test for the problem.
    for test in self.specs["tests"]:
      lost_points = 0
      graded_test = {"errors": [], "deductions": [], "success": False}
      self.output["tests"].append(graded_test)

      try:
        lost_points += grade_test(test, graded_test)

        # Apply any other deductions.
        if graded_test.get("deductions"):
          for deduction in graded_test["deductions"]:
            (lost, desc) = SQL_DEDUCTIONS[deduction]
            self.output["errors"].append(desc) # TODO fix this
            lost_points += lost

      # If their query times out.
      except timeouts.TimeoutError:
        self.output["errors"].append("Query timed out.") # TODO errors
        lost_points += test["points"]
        if test.get("teardown"): self.db.run_query(test["teardown"])

      # If there was a MySQL error, print out the error that occurred and the
      # code that caused the error.
      except mysql.connector.errors.Error as e:
        self.output["errors"].append("MYSQL ERROR " + str(e)) # TODO errors
        lost_points += test["points"]
        if test.get("teardown"): self.db.run_query(test["teardown"])

      self.got_points -= lost_points
      graded_test["got_points"] = test["points"] - lost_points

    # Run problem teardown queries.
    if problem.get("teardown"):
      for q in problem["teardown"]: self.db.run_query(q)

    # Get the total number of points received.
    self.got_points = (self.got_points if self.got_points > 0 else 0)
    self.output["got_points"] = self.got_points
    return self.got_points


  def grade_test(self, test, output):
    """
    Function: grade_test
    --------------------
    Runs a test.

    test: The specs for the test to run.
    output: The graded output for this test.

    returns: The number of points to deduct.
    """
    raise NotImplementedError("Must be implemented!")
