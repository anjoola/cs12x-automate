import mysql.connector

from CONFIG import MAX_TIMEOUT, SQL_DEDUCTIONS, PROBLEM_TYPES
from cache import Cache
from problemtype import *
from problemtype import ProblemType
import dbtools
import iotools
from response import Response

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
          self.db.run_query(response[f][problem_num].sql)
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
    for f in self.specs["files"]:
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
          got_points += PROBLEM_TYPES[problem["type"]](self.db, problem, \
            responses[problem["number"]], graded_problem, self.cache).grade()

        # If they didn't do a problem.
        except KeyError as e:
          print str(e)
          graded_problem["notexist"] = True # TODO other errors like problem type
        #print ".",

      graded_file["got_points"] = got_points
      total_points += got_points
      #print "\n"

    return total_points


  def cleanup(self):
    """
    Function: cleanup
    -----------------
    TODO
    """
    self.cache.clear()
