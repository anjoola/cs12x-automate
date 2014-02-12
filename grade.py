import mysql.connector

from CONFIG import MAX_TIMEOUT, SQL_DEDUCTIONS
from cache import Cache
import dbtools
import iotools
from response import Response

class Grade:
  """
  Class: Grade
  ------------
  Handles the grading of different types of problems. Runs the different types
  of tests on that problem.
  """

  def __init__(self, specs, db):
    # The specifications for this assignment.
    self.specs = specs

    # The database tool object used to interact with the database.
    self.db = db

    # Cache to store results of query runs to avoid having to run the same
    # query multiple times.
    self.cache = Cache()


  def run_dependencies(self, problem, response):
    """
    Function: run_dependencies
    --------------------------
    Run dependent queries (which are student responses from other questions).
    
    problem: The problem to run dependencies for.
    response: The student's responses.
    """
    try:
      if problem.get("dependencies"):
        for dep in problem["dependencies"]:
          [f, problem_num] = dep.split("|")
          self.db.run_query(response[f][0][problem_num].sql)
      # Run setup queries.
      if problem.get("setup"):
        for q in problem["setup"]: self.db.run_query(q)

    except mysql.connector.errors.ProgrammingError as e:
      # TODO graded["errors"].append("Dependent query had an exception. Most " + \
      #  "likely all tests after this one will fail | MYSQL ERROR " + \
      #  str(e))
      raise


  def grade(self, response, output):
    """
    Function: grade
    ---------------
    Grades a student's responses.

    response: The student's response.
    output: The graded output.

    returns: The number of points received for this problem.
    """
    # Grade the files (that exist) for this student.
    total_points = 0
    for f in files:
      # Skip this file if it doesn't exist.
      if f not in response.keys():
        continue

      #print "- " + f + ":" ,
      (responses, graded_file) = (response[f], output["files"][f])
      got_points = 0

      # Grade each problem in the assignment.
      problems = self.specs[f]
      for problem in problems:
        self.run_dependencies(problem, response)

        graded_problem = {"num": problem["number"], "tests": [], "errors": [], \
          "got_points": 0}
        graded_file["problems"].append(graded_problem)

        try: # TODO call specific class depending on the problem type to grade
          got_points += TYPES[problem["type"]](self.db, problem, \
            responses[problem["number"]], output, cache).grade()

        # If they didn't do a problem.
        except KeyError:
          graded_problem["notexist"] = True
        #print ".",

      graded_file["got_points"] = got_points
      total_points += got_points
      #print "\n"

    return total_points

    


  def select(self, test, response, graded):
    """
    Function: select
    ----------------
    Runs a test SELECT statement and compares it to the student's SELECT
    statement. Possibly checks for the following things:
      - Order of rows
      - Order of columns
      - Whether or not derived relations are renamed

    test: The test to run.
    response: The student's response.
    graded: The graded test output.

    returns: The number of points to deduct.
    """
    


  def create(self, test, response, graded):
    """
    Function: create
    ----------------
    Tests a create statement. TODO

    test: The test to run.
    response: The student's response.
    graded: The graded test output.

    returns: The number of points to deduct.
    """
    # TODO check for drop tables?
    # TODO check for comments?

    graded["success"] = "UNDETERMINED"
    # TODO create table statements are just printed.
    return 0


  def insert(self, test, response, graded):
    """
    Function: insert
    ----------------
    Tests an insert statement and sees if the student's query produces the
    same diff as the solution query.

    test: The test to run.
    response: The student's response.
    graded: The graded test output.

    returns: The number of points to deduct.
    """
    table_sql = "SELECT * FROM " + test["table"]

    # Compare the expected rows inserted versus the actual.
    self.cache.get(self.db.run_query, test["query"], \
      setup=test.get("setup"), teardown=test.get("teardown"))
    expected = self.db.run_query(table_sql)

    self.db.run_query("DELETE FROM " + test["table"])
    self.db.run_query(response.sql, setup=test.get("setup"), \
      teardown=test.get("teardown"))
    actual = self.db.run_query(table_sql)

    # If the results are not equal in size, then they are wrong.
    if len(expected.results) != len(actual.results):
      return test["points"]

    # If the results are equal, then then the test passed.
    if equals(set(expected.results), set(actual.results)):
      graded["success"] = True
      return 0

    else:
      return test["points"]


  def sp(self, test, response, graded):
    """
    Function: sp
    ------------
    Tests a stored procedure by calling the procedure and checking the contents
    of the table before and after.

    test: The test to run.
    response: The student's response.
    graded: The graded test output.

    returns: The number of points to deduct.
    """
    # Get the table before and after the stored procedure is called.
    table_sql = "SELECT * FROM " + test["table"]
    before = self.db.run_query(table_sql)

    # Setup queries.
    if test.get("run-query"): self.db.run_query(response.sql)
    if test.get("setup"): self.db.run_query(test["setup"])

    after = self.db.run_query(table_sql, setup=test["query"], 
      teardown=test.get("teardown"))

    subs = list(set(before.results) - set(after.results))
    graded["subs"] = ("" if len(subs) == 0 else self.db.prettyprint(subs))
    adds = list(set(after.results) - set(before.results))
    graded["adds"] = ("" if len(adds) == 0 else self.db.prettyprint(adds))

    graded["success"] = "UNDETERMINED"
    # TODO how to handle deductions?
    return 0


  def function(self, test, response, graded):
    """
    Function: function
    ------------------  
    Tests a function by calling it and comparing it with the expected output.

    test: The test to run.
    response: The student's response.
    graded: The graded test output.

    returns: The number of points to deduct.
    """
    if test.get("run-query"):
      self.db.run_query(response.sql)
    result = self.db.run_query(test["query"], teardown=test.get("teardown"))

    if result.results and result.results[0]:
      result = str(result.results[0][0])
    else: result = ""

    graded["actual"] = result
    graded["expected"] = test["expected"]

    # Should be all or nothing.
    if test["expected"] != result:
      graded["success"] = False
      return test["points"]
    else:
      graded["success"] = True
      return 0


# ----------------------------- Utility Functions ---------------------------- #

def equals(lst1, lst2):
  """
  Function: equals
  ----------------
  Compares two lists of tuples to see if their contents are equal.
  """
  return [tuple(unicode(x).lower() for x in y) for y in lst1] == \
    [tuple(unicode(x).lower() for x in y) for y in lst2]
