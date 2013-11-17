import dbtools
import iotools
from iotools import write
import mysql.connector
from response import Response

class Grade:
  """
  Class: Grade
  ------------
  Handles the grading of different types of problems. Runs the different types
  of tests on that problem.
  """

  def __init__(self, specs):
    # The specifications for this assignment.
    self.specs = specs


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
    # TODO


  #def write(self, string):
    """
    Function: write
    ---------------
    Writes a string out to the output file.
    """
    #write(self.o, string)


  def grade(self, problem, response, graded, cursor):
    """
    Function: grade
    ---------------
    Runs all of the tests for a particular problem and computes the number
    of points received.

    problem: The problem specification.
    response: The student's response.
    graded: The graded problem output.
    cursor: The database cursor.

    returns: The number of points received for this problem.
    """
    # Problem definitions.
    num = problem["number"]
    num_points = problem["points"]
    #self.write("---")
    #self.write("#### Problem " + num + " (" + str(num_points) + " points)")
    graded["num_points"] = num_points

    # Print out some things before running tests.
    self.pretest(problem, response, graded)

    # The number of points this student has received so far on this problem.
    got_points = num_points

    # Run each test for the problem.
    for test in problem["tests"]:
      points = test["points"]
      graded_test = {"points": points, "errors": []}
      graded["tests"].append(graded_test)

      try:
        # Figure out what kind of test it is and call the appropriate function.
        f = self.get_function(test)
        got_points -= (0 if f(test, response, graded_test, cursor) else points)

      # If there was a MySQL error, print out the error that occurred and the
      # code that caused the error.
      except mysql.connector.errors.ProgrammingError as e:
        graded["errors"].append("MYSQL ERROR " + str(e))
        #self.write("**`MYSQL ERROR`** " + str(e))
        got_points -= points

      #except Exception as e:
      #  print "TODO", str(e)
        # TODO handle

    # Get the total number of points received.
    got_points = (got_points if got_points > 0 else 0)
    graded["got_points"] = got_points
    """
    if got_points > 0:
      self.write("> ##### Points: " + str(got_points) + " / " + str(num_points))
    else:
      self.write("> `Points: " + str(got_points) + " / " + str(num_points) + "`")
    """
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
    # Print out the comments for this problem if they are required.
    if "comments" in problem and problem["comments"]:
      graded["comments"] = response.comments
      #self.write("**Comments**\n")
      #self.write(response.comments)

    # Print out the query results if required.
    # TODO have this anyway? don't need an if condition.
    # Then when generating the output can check if show results is true
    if "show-results" in problem and problem["show-results"]:
      graded["submitted-results"] = response.results
      #self.write("**Submitted Results**\n")
      #self.write(iotools.format_lines("   ", response.results))

    # Print out the student's code for this problem.
    #if "comments" in problem or "show-results" in problem:
    #  self.write("**SQL**\n")
    #self.write(iotools.format_lines("   ", response.sql))
    graded["sql"] = response.sql

    # Check for keywords.
    if "keywords" in problem:
      missing = False
      missing_keywords = []
      for keyword in problem["keywords"]:
        if keyword not in response.sql:
          missing = True
          missing_keywords.append(keyword)
      if missing:
        graded["errors"].append("MISSING KEYWORDS " + ", ".join(missing_keywords))
        #self.write("**`MISSING KEYWORDS`** " + ", ".join(missing_keywords))

    # TODO take points off for missing keywords?


  def select(self, test, response, graded, cursor):
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
    cursor: The database cursor.

    returns: True if the test passed, False otherwise.
    """
    # TODO
    boolean = True
    
    
    expected = dbtools.run_query(test, test["query"], cursor)
    actual = dbtools.run_query(test, response.sql, cursor)

    # If we don't need to check that the results are ordered, then sort the
    # results for easier checking.
    if "ordered" not in test or not test["ordered"]:
      expected.results = sorted(expected.results)
      actual.results = sorted(actual.results)

    # If we don't need to check that the columns are ordered in the same way,
    # then sort each tuple for easier checking.
    if "column-order" not in test or not test["column-order"]:
      expected.results = [tuple(sorted(x)) for x in expected.results]
      actual.results = [tuple(sorted(x)) for x in actual.results]

    # Compare the student's code to the results.
    if expected.results != actual.results:
      graded["success"] = False
      #self.write("**`TEST FAILED`** (Lost " + str(test["points"]) + " points)")
      #self.write(iotools.format_lines("   ", test["query"]))
      graded["expected"] = expected.output
      #self.write("_Expected Results_")
      #self.write(iotools.format_lines("   ", expected.output))
      graded["actual"] = actual.output
      #self.write("_Actual Results_")
      #self.write(iotools.format_lines("   ", actual.output))

      # Check to see if they forgot to ORDER BY.
      if "ordered" in test and test["ordered"]:
        eresults = sorted(expected.results)
        aresults = sorted(actual.results)
        if aresults == eresults:
          graded["errors"].append("MISSING ORDER BY")
          #self.write("`MISSING ORDER BY`")
        # TODO poitns off? add points back and only take points off for order by?

      # See if they chose the wrong column order.
      if "column-order" in test and test["column-order"]:
        eresults = [tuple(sorted(x)) for x in expected.results]
        aresults = [tuple(sorted(x)) for x in actual.results]
        if eresults == aresults:
          graded["errors"].append("WRONG COLUMN ORDERING")
          #self.write("`WRONG COLUMN ORDERING`")
          # TODO add points back?

      boolean = False

    # Check to see if they named aggregates.
    # TODO check for other things? must contain a certain word in col name?
    if "rename" in test and test["rename"]:
      for col in actual.col_names:
        if col.find("(") + col.find(")") != -2:
          graded["errors"].append("DID NOT RENAME AGGREGATES")
          #self.write("`DID NOT RENAME AGGREGATES`")
          # TODO take points off
          boolean = False
          break

    # TODO don't return true or false, return how many points to take off
    return boolean


  def create(self):
    """
    Function: create
    ----------------
    TODO

    test: The test to run.
    response: The student's response.
    cursor: The database cursor.

    returns: True if the test passed, False otherwise.
    """
    pass


