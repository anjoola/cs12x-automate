import mysql.connector

import dbtools, iotools
from CONFIG import MAX_TIMEOUT
from errors import (
  add,
  DatabaseError,
  DependencyError
)
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


  def run_dependencies(self, problem, response):
    """
    Function: run_dependencies
    --------------------------
    Run dependent queries (which are the student's responses for other
    questions).

    problem: The problem to run dependencies for.
    response: The student's responses.
    """
    if problem.get("dependencies"):
      for dep in problem["dependencies"]:
        # Get the file and problem number for the dependent query.
        [dep_file, problem_num] = dep.split("|")

        try:
          self.db.execute_sql(response[dep_file][problem_num].sql)
        except DatabaseError as e:
          raise DependencyError(dep_file, problem_num, e)

    # Run setup queries.
    if problem.get("setup"):
      for q in problem["setup"]: self.db.execute_sql(q)


  def run_teardown(self, problem):
    """
    Function: run_teardown
    ----------------------
    Run teardown queries.

    problem: The problem to run teardown queries for.
    """
    try:
      if problem.get("teardown"):
        for q in problem["teardown"]: self.db.execute_sql(q)

    except DatabaseError:
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

      log("\n  - " + f + ": ")
      (responses, graded_file) = (response[f], output["files"][f])
      got_points = 0

      # Grade each problem in the assignment.
      problems = self.specs[f]
      for problem in problems:
        # Add this graded problem to the list in the graded file.
        num = problem["number"]
        graded_problem = {"num": num, "tests": [], "errors": [], \
                          "got_points": 0}
        graded_file["problems"].append(graded_problem)

        try:
          # Call the grade function on the specific class corresponding to this
          # problem type.
          grade_fn = PROBLEM_TYPES[problem["type"]]
          grade_fn = grade_fn(self.db, problem, responses[num], graded_problem)
          grade_fn.preprocess()

          # Run dependent query.
          self.run_dependencies(problem, response)

          got_points += grade_fn.grade()

        except DependencyError as e:
          add(graded_problem["errors"], e)

        # If they didn't do a problem, indicate that it doesn't exist.
        except KeyError:
          graded_problem["notexist"] = True

        # Run teardown queries.
        self.run_teardown(problem)
        log(".")

      # Compute total points for this file.
      graded_file["got_points"] = got_points
      total_points += got_points

    return total_points
