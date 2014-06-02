import mysql.connector

from cache import Cache
from CONFIG import MAX_TIMEOUT, SQL_DEDUCTIONS
import dbtools
from errors import *
import iotools
from iotools import log
from models import Response
from problemtype import *

class Grader:
  """
  Class: Grader
  -------------
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


  def cleanup(self):
    """
    Function: cleanup
    -----------------
    Cleanup stuff after grading.
    """
    self.cache.clear()


  def run_dependencies(self, problem, response):
    """
    Function: run_dependencies
    --------------------------
    Run dependent queries (which are the student's responses for other
    questions).

    problem: The problem to run dependencies for.
    response: The student's responses.
    """
    try:
      if problem.get("dependencies"):
        for dep in problem["dependencies"]:
          # Get the file and problem number for the dependent query.
          [dep_file, problem_num] = dep.split("|")
          self.db.run_query(response[dep_file][problem_num].sql)

      # Run setup queries.
      if problem.get("setup"):
        for q in problem["setup"]: self.db.run_query(q)

    # If there was an error with the dependent query.
    except mysql.connector.errors.ProgrammingError as e:
      # TODO graded["errors"] does not exist...
      add(graded["errors"], DependencyError(problem["dependencies"]))
      add(graded["errors"], MySQLError(e))
      raise


  def run_teardown(self, problem):
    """
    Function: run_teardown
    ----------------------
    Run teardown queries.

    problem: The problem to run teardown queries for.
    """
    try:
      if problem.get("teardown"):
        for q in problem["teardown"]: self.db.run_query(q)

    except mysql.connector.errors as e:
      print e # TODO
      pass


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
    for f in self.specs["files"]:
      # Skip this file if it doesn't exist.
      if f not in response.keys():
        continue

      log("- " + f + ": ")
      (responses, graded_file) = (response[f], output["files"][f])
      got_points = 0

      # Grade each problem in the assignment.
      problems = self.specs[f]
      for problem in problems:
        self.run_dependencies(problem, response)

        # Add this graded problem to the list in the graded file.
        num = problem["number"]
        graded_problem = {"num": num, "tests": [], "errors": [], \
                          "got_points": 0}
        graded_file["problems"].append(graded_problem)

        try:
          # Call the grade function on the specific class corresponding to this
          # problem type.
          grader = PROBLEM_TYPES[problem["type"]]
          got_points += grader(self.db, problem, responses[num], \
                               graded_problem, self.cache).grade()

        # If they didn't do a problem, indicate that it doesn't exist.
        except KeyError as e:
          graded_problem["notexist"] = True

        # Run teardown queries.
        self.run_teardown(problem)
        log(".")

      # Compute total points for this file.
      graded_file["got_points"] = got_points
      total_points += got_points
      log("\n")

    return total_points
