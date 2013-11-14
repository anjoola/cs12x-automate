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

  def __init__(self, specs, o):
    # The specifications for this assignment.
    self.specs = specs
    # THe file to output to.
    self.o = o


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


  def write(self, string):
    write(self.o, string)

  def grade(self, problem, response, cursor):
    """
    Function: grade
    ---------------
    Runs all of the tests for a particular problem and computes the number
    of points received.

    problem: The problem specification.
    response: The student's response.
    cursor: The database cursor.

    returns: The number of points received for this problem.
    """
    # Problem definitions.
    num = problem["number"]
    needs_comments = problem["comments"]
    num_points = int(problem["points"])
    self.write("#### Problem " + num + " (" + str(num_points) + " points)")

    # Print out the comments for this problem if they are required.
    if needs_comments == "true":
      self.write("**Comments**\n")
      self.write(response.comments)

    # The number of points this student has received so far on this problem.
    got_points = num_points

    # Run each test for the problem.
    for test in problem["tests"]:
      test_points = int(test["points"])

      try:
        # Figure out what kind of test it is and call the appropriate function.
        f = self.get_function(test)
        got_points -= (0 if f(test, response, cursor) else test_points)

      # If there was a MySQL error, print out the error that occurred and the
      # code that caused the error.
      except mysql.connector.errors.ProgrammingError as e:
        self.write("**Incorrect Code**")
        self.write(iotools.format_lines("   ", response.query))
        self.write("_MySQL Error:_ " + str(e))
        got_points -= test_points

      except Exception as e:
        print "TODO", str(e)
        # TODO handle

    # Get the total number of points received.
    got_points = (got_points if got_points > 0 else 0)
    self.write("> ##### Points: " + str(got_points) + " / " + str(num_points))
    return got_points


  def select(self, test, response, cursor):
    """
    Function: select
    ----------------
    TODO

    test: The test to run.
    response: The student's response.
    cursor: The database cursor.

    returns: True if the test passed, False otherwise.
    """
    expected = dbtools.run_query(test, test["query"], cursor)
    actual = dbtools.run_query(test, response.query, cursor)

    # Compare the student's code to the results.
    # TODO check sorting order, schema
    # TODO what if don't need to check order of results or columns?
    # TODO comparing results doesn't quite work?
    if expected.results != actual.results:
      self.write("**Test** (" + str(test_points) + " points)")
      self.write(iotools.format_lines("   ", test["query"]))
      self.write("_Expected Results_")
      self.write(iotools.format_lines("   ", expected.output))
      self.write("_Actual Results_")
      self.write(iotools.format_lines("   ", actual.output))
      return False
    return True


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


