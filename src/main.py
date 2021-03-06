import argparse
import json
import os
import sys

import dbtools
import formatter
import iotools
import traceback

from CONFIG import (
  ASSIGNMENT_DIR,
  CONNECTION_TIMEOUT,
  MAX_TIMEOUT,
  STUDENT_DIR,
  VERBOSE
)
from errors import (
  add,
  DatabaseError,
  FileNotFoundError
)
from grader import Grader
from iotools import err, log
from models import GradedOutput
from stylechecker import StyleChecker

class AutomationTool:
  """
  Class: AutomationTool
  ---------------------
  The automation tool. Is able to parse the arguments and grade all the files.
  """
  # Whether or not to run the dependencies.
  dependency = False

  # Whether or not to purge the database before running the automation tool.
  purge = False

  # Whether or not to output results as raw JSON.
  raw = False

  def __init__(self):
    # The assignment to grade.
    self.assignment = None

    # The database to use, and later, the database connection.
    self.db = None

    # The files to grade.
    self.files = None

    # The grading tool.
    self.grader = None

    # The graded output.
    self.o = None

    # The specs file.
    self.specs = None

    # The students to grade.
    self.students = None

    # Which student to start with.
    self.start_with = None

    # The username for the database connection.
    self.user = None


  def get_args(self):
    """
    Function: get_args
    ------------------
    Gets the command-line arguments and prints a usage message if needed.
    Figures out the files and students to grade.
    """
    # Parse command-line arguments.
    parser = argparse.ArgumentParser()

    # The grading-specific arguments.
    parser.add_argument("--assignment", required=True,
                        help="Name of the assignment (cs121hw#)")
    parser.add_argument("--files", nargs="+", help="List of files to check")
    parser.add_argument("--students", nargs="+", help="Students to check")
    parser.add_argument("--startwith", nargs="+", help="Which student to start with")
    parser.add_argument("--exclude", nargs="+", help="Students to skip")
    parser.add_argument("--after", help="Of the form YYYY-MM-DD, will only "
                                        "grade students who've submitted after "
                                        "that date. Cannot be used with the "
                                        "--students flag")
    # Database-specific arguments.
    parser.add_argument("--user", help="Username for the database, defaults to "
                                       "a random one in the CONFIG")
    parser.add_argument("--db", help="Database to test on, defaults to "
                                     "<username>_db")
    parser.add_argument("--deps", action="store_const", const=True,
                        help="Whether or not to run the dependencies. Should "
                             "only be run once with this flag unless a purge "
                             "occurs, since there is no point running "
                             "dependencies more than once if they are already "
                             "in the database")
    parser.add_argument("--purge", action="store_const", const=True,
                        help="Whether or not to purge the database before"
                             " grading")
    parser.add_argument("--hide", action="store_const", const=True,
                        help="Whether or not to hide solutions from the output,"
                             " used to generate output for students")
    parser.add_argument("--raw", action="store_const", const=True,
                        help="Whether or not to output results as a raw JSON "
                             "file")
    args = parser.parse_args()
    (self.assignment, self.files, self.students, self.start_with, exclude, after,
     self.user, self.db, AutomationTool.purge, AutomationTool.dependency,
     AutomationTool.hide_solutions, AutomationTool.raw) = (
        args.assignment, args.files, args.students, args.startwith, args.exclude,
        args.after, args.user, args.db, args.purge, args.deps, args.hide, args.raw)

    # If the assignment argument isn't specified, print usage statement.
    if self.assignment is None:
      parser.print_help()
      sys.exit(1)

    # Get the specs, files, and students for this assignment.
    self.specs = iotools.parse_specs(self.assignment)

    # If nothing specified for the files, grade all the files. Make sure the
    # specified files are all valid.
    if self.files is None or self.files[0] == "*":
      self.files = self.specs["files"]
    for f in self.files:
      if f not in self.specs["files"]:
        err("File %s is not in the specs!" % f)
        self.files.remove(f)
    if len(self.files) == 0:
      err("No valid files specified for grading!", True)

    # If nothing specified for the students, grade all the students.
    if self.students is None or self.students[0] == "*":
      self.students = iotools.get_students(self.assignment, after)

    if self.start_with:
      self.start_with = self.start_with[0]
      try:
        start_index = self.students.index(self.start_with)
        self.students = self.students[start_index:]
      except ValueError:
        err("Couldn't find %s in students." % self.start_with, True)

    # Take out students to skip.
    if exclude:
      self.students = [s for s in self.students if s not in exclude]


  def grade_loop(self):
    """
    Function: grade_loop
    --------------------
    Run the grading loop. Goes through each student and grades them.
    """
    log("\n\n========================START GRADING========================\n")
    # Get the state of the database before grading.
    state = self.db.get_state()

    # Keep a list of students that we could not grade.
    failed_grading = []
    possibly_failed = False
    possibly_failed_grading = []

    # Grade each student.
    if len(self.students) == 0:
      err("No students to grade!")

    i_student = 0
    n_students = len(self.students)
    for student in self.students:
      i_student += 1
      try:
        self.grade_student(student, i_student, n_students)
        # If we've managed to grade this student, remove them from the students
        # that we could not grade.
        if student in failed_grading:
          failed_grading.remove(student)
      except Exception:
        # Don't try to regrade again if failed once already.
        if student not in failed_grading:
          failed_grading.append(student)
          self.students.append(student)
          print "\nFailed grading " + student + ", trying one more time.\n"
          traceback.print_exc()
        else:
          print "\nFailed grading " + student + " again. Giving up.\n"

      # Get the state of the database after the student is graded and reset it
      # to what it was before.
      try:
        new_state = self.db.get_state()
        self.db.reset_state(state, new_state)
      except:
        possibly_failed = True
        err("Could not get the database state. Future gradings are possibly " +
          "affected.")
      if possibly_failed and student not in possibly_failed_grading:
        possibly_failed_grading.append(student)

    log("\n\n=========================END GRADING=========================\n")

    if len(failed_grading) > 0:
      print "\nFAILED GRADING:",
      print ", ".join(failed_grading)
    if len(possibly_failed_grading) > 0:
      print "\nPOSSIBLY FAILED (could not get the database state):",
      print ", ".join(possibly_failed_grading)


  def grade_student(self, student, i_student, n_students):
    """
    Function: grade_student
    -----------------------
    Grades a particular student. Outputs the results to a file.

    student: The student's name.
    """
    log("\n\n%s (%d/%d):" % (student, i_student, n_students))

    # Check to see that this student exists. If not, skip this student.
    path = ASSIGNMENT_DIR + self.assignment + "/" + STUDENT_DIR + student + \
           "-" + self.assignment + "/"
    if not os.path.exists(path):
      err("Student " + student + " does not exist or did not submit!")
      return

    # Graded output for this particular student. Add it to the overall output.
    output = {"name": student, "files": {}, "got_points": 0}
    self.o.fields["students"].append(output)

    # Parse student's response.
    response = {}
    for filename in self.files:
      # Add this file to the graded output.
      graded_file = {
        "filename": filename,
        "problems": [],
        "errors": [],
        "got_points": 0
      }
      output["files"][filename] = graded_file
      fname = path + filename

      try:
        f = open(fname, "r")
        # Run their files through the stylechecker to make sure it is valid. Add
        # the errors to the list of style errors for this file and overall for
        # this student.
        graded_file["errors"] += StyleChecker.check(f)

        # Reset back to the beginning of the file.
        f.seek(0)
        response[filename] = iotools.parse_file(f)
        f.close()

      # If the file does not exist, then they get 0 points.
      except IOError:
        add(graded_file["errors"], FileNotFoundError(fname))

    # Grade this student, make style deductions, and output the results.
    output["got_points"] = self.grader.grade(response, output)
    formatter.format_student(student, output, self.specs, self.hide_solutions)


  def setup(self):
    """
    Function: setup
    ---------------
    Sets up the grading environment and tools. This includes establishing the
    database connection, reading the specs file, sourcing all dependencies,
    and running setup queries.
    """
    # The graded output.
    self.o = GradedOutput(self.specs)
    # Start up the connection with the database.
    self.db = dbtools.DBTools(self.user, self.db)
    try:
      self.db.get_db_connection(MAX_TIMEOUT)
    except DatabaseError:
      err("Could not get a database connection! Please check your internet " +
          "connection and database connection information!",
          True)

    # Purge the database if necessary.
    if AutomationTool.purge: self.db.purge_db()

    # Source and import files needed prior to grading and run setup queries.
    if self.specs.get("setup"):
      for item in self.specs.get("setup"):
        if item["type"] == "dependency" and AutomationTool.dependency:
          if VERBOSE:
            print("Sourcing dependency file %s" % item["file"])

          self.db.source_file(self.assignment, item["file"])
        elif item["type"] == "import" and AutomationTool.dependency:
          if VERBOSE:
            print("Importing file %s" % item["file"])

          self.db.import_file(self.assignment, item["file"])
        elif item["type"] == "queries": 
          if VERBOSE:
            print("Running initial queries:\n * %s" % '\n * '.join(item["queries"]))

          for q in item["queries"]: self.db.execute_sql(q)

    # Initialize the grading tool.
    self.db.get_db_connection(CONNECTION_TIMEOUT)
    self.grader = Grader(self.assignment, self.specs, self.db)


  def teardown(self):
    """
    Function: teardown
    ------------------
    Outputs the results, runs the teardown queries and closes the database
    connection.
    """
    # Output the results to file, but only if there are students to output.
    json_output = json.loads(self.o.jsonify())
    if json_output["students"]:
      f = iotools.output(json_output, self.specs, self.raw)
      log("\n\n==== RESULTS: " + f.name)

    # Run teardown queries.
    if self.specs.get("teardown"):
      for query in self.specs["teardown"]:
        self.db.execute_sql(query)

    # Close connection with the database
    self.db.close_db_connection()


if __name__ == "__main__":
  a = AutomationTool()
  try:
    a.get_args()
    a.setup()
    a.grade_loop()
    a.teardown()
  except Exception:
    err("\n\nThere is an error with the tool!\n")
    traceback.print_exc()
