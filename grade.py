from CONFIG import MAX_TIMEOUT, SQL_DEDUCTIONS
from cache import Cache
import dbtools
import iotools
import mysql.connector
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


  def get_function(self, test):
    """
    Function: get_function
    ----------------------
    Finds the right function to call on for the specified test.

    test: The test to find the right function for.
    returns: A function object.
    """
    test_type = test["type"]
    if test_type == "select":
      return self.select
    elif test_type == "create":
      return self.create
    elif test_type == "stored-procedure":
      return self.sp
    elif test_type == "function":
      return self.function
    elif test_type == "insert":
      return self.insert
    # TODO add other functions?


  def grade(self, problem, response, graded, file_responses):
    """
    Function: grade
    ---------------
    Runs all of the tests for a particular problem and computes the number
    of points received.

    problem: The problem specification.
    response: The student's response.
    graded: The graded problem output.
    file_responses: The entire list of responses (used for certain tests like
                    stored procedure tests).

    returns: The number of points received for this problem.
    """
    # Problem definitions.
    num = problem["number"]
    num_points = problem["points"]

    # Print out some things before running tests.
    self.pretest(problem, response, graded)

    # The number of points this student has received so far on this problem.
    got_points = num_points

    try:
      # Run dependent queries (which is the student's response from another
      # question).
      if problem.get("dependencies"):
        for dep in problem["dependencies"]:
          [f, problem_num] = dep.split("|")
          self.db.run_query(file_responses[f][0][problem_num].sql)
      # Run setup queries.
      if problem.get("setup"):
        for q in problem["setup"]: self.db.run_query(q)

    except mysql.connector.errors.ProgrammingError as e:
      graded["errors"].append("Dependent query had an exception. Most " + \
        "likely all tests after this one will fail | MYSQL ERROR " + \
        str(e))
      return 0

    # Run each test for the problem.
    for test in problem["tests"]:
      lost_points = 0
      graded_test = {"errors": [], "deductions": [], "success": False}
      graded["tests"].append(graded_test)

      try:
        # Change the connection timeout.
        self.db.get_db_connection(test.get("timeout"))

        # Figure out what kind of test it is and call the appropriate function.
        f = self.get_function(test)
        lost_points += f(test, response, graded_test)

        # Apply any other deductions.
        if graded_test.get("deductions"):
          for deduction in graded_test["deductions"]:
            (lost, desc) = SQL_DEDUCTIONS[deduction]
            graded["errors"].append(desc)
            lost_points += lost

      # TODO database disconnected or their query timedout
      except mysql.connector.errors.InterfaceError as e:
        print "error: ", e
        graded["errors"].append("MYSQL ERROR " + str(e) + " (most likely " + \
          "the query is invalid and failed or query timed out)")
        lost_points += test["points"]
        self.db.get_db_connection(MAX_TIMEOUT)
        if test.get("teardown"): self.db.run_query(test["teardown"])

      # If there was a MySQL error, print out the error that occurred and the
      # code that caused the error.
      except mysql.connector.errors.Error as e:
        graded["errors"].append("MYSQL ERROR " + str(e))
        lost_points += test["points"]
        self.db.get_db_connection(MAX_TIMEOUT)
        if test.get("teardown"): self.db.run_query(test["teardown"])

      got_points -= lost_points
      graded_test["got_points"] = test["points"] - lost_points
      #except Exception as e:
      #  print "TODO", str(e)
        # TODO handle

    # Run problem teardown queries.
    if problem.get("teardown"):
      self.db.get_db_connection(MAX_TIMEOUT)
      for q in problem["teardown"]: self.db.run_query(q)

    # Get the total number of points received.
    got_points = (got_points if got_points > 0 else 0)
    graded["got_points"] = got_points
    return got_points


  def pretest(self, problem, response, graded):
    """
    Function: pretest
    -----------------
    Check for certain things before running the tests and print them out.
    This includes:
      - Comments
      - Attaching results of query
      - Checking their SQL for certain keywords
      - Printing out their actual SQL

    problem: The problem specification.
    response: The student's response.
    graded: The graded problem output.
    """
    # Comments, query results, and SQL.
    graded["comments"] = response.comments
    graded["submitted-results"] = response.results
    graded["sql"] = response.sql

    # Check for keywords.
    if problem.get("keywords"):
      missing = False
      missing_keywords = []
      for keyword in problem["keywords"]:
        if keyword not in response.sql:
          missing = True
          missing_keywords.append(keyword)
      if missing:
        graded["errors"].append("MISSING KEYWORDS " + ", ".join(missing_keywords))
    # TODO take points off for missing keywords?


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
    success = True
    deductions = 0
    test_points = test["points"]

    # TODO make sure they aren't doing SQL injection
    expected = self.cache.get(self.db.run_query, test["query"], \
      setup=test.get("setup"), teardown=test.get("teardown"))
    try:
      actual = self.db.run_query(response.sql, setup=test.get("setup"), \
        teardown=test.get("teardown"))
    except mysql.connector.errors.ProgrammingError as e:
      raise
    """
    # TODO
    # Run the teardown no matter what.
    finally:
      self.db.run_query(test.get("teardown"))
    """
    # If we don't need to check that the results are ordered, then sort the
    # results for easier checking.
    if not test.get("ordered"):
      expected.results = set(expected.results)
      actual.results = set(actual.results)

    # If we don't need to check that the columns are ordered in the same way,
    # then sort each tuple for easier checking.
    if not test.get("column-order"):
      expected.results = [set(x) for x in expected.results]
      actual.results = [set(x) for x in actual.results]

    # Compare the student's code to the results.
    if not equals(expected.results, actual.results):
      graded["expected"] = expected.output
      graded["actual"] = actual.output
      deductions = test_points

      # Check to see if they forgot to ORDER BY.
      if test.get("ordered"):
        eresults = set(expected.results)
        aresults = set(actual.results)
        if aresults == eresults:
          deductions = 0
          graded["deductions"].append("orderby")

      # See if they chose the wrong column order.
      if test.get("column-order"):
        eresults = [set(x) for x in expected.results]
        aresults = [set(x) for x in actual.results]
        if equals(eresults, aresults):
          deductions = 0
          graded["deductions"].append("columnorder")

      success = False

    # Check to see if they named aggregates.
    # TODO check for other things? must contain a certain word in col name?
    if test.get("rename"):
      for col in actual.col_names:
        if col.find("(") + col.find(")") != -2:
          graded["deductions"].append("renamecolumns")
          success = False
          break

    # TODO more or fewer columns?
    graded["success"] = success
    return deductions


  def create(self, test, response, graded):
    """
    Function: create
    ----------------
    TODO

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

    # If the results are equal, then then the test passed.
    if equals(set(expected.results), set(actual.results)):
      graded["success"] = True
      return 0

    else:
      print "\n\n\n\n\nNOT EQUAL"
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
    result = str(result.results[0][0])

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
