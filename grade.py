from iotools import write

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
      return select
    elif test_type == "create":
      return create
    # TODO


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
    write(o, "#### Problem " + num + " (" + str(num_points) + " points)")

    # Print out the comments for this problem if they are required.
    if needs_comments == "true":
      write(o, "**Coments**\n")
      write(o, response.comments)

    # The number of points this student has received so far on this problem.
    got_points = num_points

    # Run each test for the problem.
    for test in problem["tests"]:
      test_points = int(test["points"])

      # Figure out what kind of test it is and call the appropriate function.
      f = self.get_function(test, response, cursor)
      got_points -= f(test)

    # Get the total number of points received.
    got_points = (got_points if got_points > 0 else 0)
    write(o, "> ##### Points: " + str(got_points) + " / " + str(num_points))
    return got_points


  def select(self, test, response, cursor):
    """
    Function: select
    ----------------
    TODO

    test: The test to run.
    response: The student's response.
    cursor: The database cursor.

    returns: The number of points lost for this test.
    """
    pass


  def create(self):
    """
    Function: create
    ----------------
    TODO

    test: The test to run.
    response: The student's response.
    cursor: The database cursor.

    returns: The number of points lost for this test.
    """
    pass


