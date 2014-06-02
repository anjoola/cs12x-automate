"""
Module: dbtools
---------------
Contains helper methods involving the database, its state, and queries.
"""
import codecs
from cStringIO import StringIO
import re
import subprocess

import mysql.connector
import prettytable
import sqlparse

from CONFIG import *
from iotools import err, log
from models import DatabaseState, Result

class DBTools:
  """
  Class: DBTools
  --------------
  Handles requests to a particular database (as specified in the CONFIG file).
  """

  # Used to find delimiters in the file.
  DELIMITER_RE = re.compile(r"^\s*delimiter\s+([^\s]+)\s*$", re.I)

  def __init__(self):
    # The database connection parameters are specified in the CONFIG.py file.
    self.db = None

    # The database cursor.
    self.cursor = None

    # The current connection timeout limit.
    self.timeout = CONNECTION_TIMEOUT

    # The savepoints.
    self.savepoints = []

  # --------------------------- Database Utilities --------------------------- #

  def close_db_connection(self):
    """
    Function: close_db_connection
    -----------------------------
    Close the database connection (only if it is already open) and any running
    queries.
    """
    if self.db:
      # Consume remaining output.
      for _ in self.cursor: pass
      self.cursor.close()

      # Kill any remaining queries and close the database connection.
      self.kill_query()
      self.db.close()


  def commit(self):
    """
    Function: commit
    ----------------
    Commits the current transaction. Destroys any savepoints.
    """
    self.db.commit()
    self.savepoints = []


  def get_cursor(self):
    """
    Function: get_cursor
    --------------------
    Gets the cursor. Assumes the database has already been connected.
    """
    return self.cursor


  def get_db_connection(self, timeout=None):
    """
    Function: get_db_connection
    ---------------------------
    Get a new database connection with a specified timeout (defaults to
    CONNECTION_TIMEOUT specified in the CONFIG file). Closes the old connection
    if there was one.

    timeout: The connection timeout.
    returns: A database connection object.
    """
    if self.db and self.db.is_connected():
      # If timeout isn't specified, check if we're already at the default.
      if timeout is None and self.timeout == CONNECTION_TIMEOUT:
        return self.db
      # If the timeout is the same as before, then don't change anything.
      if timeout is not None and timeout == self.timeout:
        return self.db

    log("New timeout: " + str(timeout))
    # Close any old connections and make another one with the new setting.
    self.close_db_connection()
    self.timeout = timeout or CONNECTION_TIMEOUT
    self.db = mysql.connector.connect(user=USER, password=PASS, host=HOST, \
                                      database=DATABASE, port=PORT, \
                                      connection_timeout=self.timeout, \
                                      autocommit=True)
    self.cursor = self.db.cursor()
    return self.db


  def get_state(self):
    """
    Function: get_state
    -------------------
    Gets the current state of the database, which includes the tables, views,
    foreign keys, functions, and procedures.

    returns: A DatabaseState object which contains the current state.
    """
    state = DatabaseState()

    # Get tables and their foreign keys.
    state.tables = self.run_query(
      "SELECT table_name FROM information_schema.tables "
      "WHERE table_type='BASE TABLE'"
    ).results
    state.foreign_keys = self.run_query(
      "SELECT DISTINCT table_name, constraint_name FROM "
      "information_schema.table_constraints WHERE constraint_type='FOREIGN KEY'"
    ).results

    # Get views, functions, and procedures.
    state.views = self.run_query(
      "SELECT table_name FROM information_schema.tables "
      "WHERE table_type='VIEW'"
    ).results
    state.functions = self.run_query(
      "SELECT routine_name FROM information_schema.routines "
      "WHERE routine_type='FUNCTION'"
    ).results
    state.procedures = self.run_query(
      "SELECT routine_name FROM information_schema.routines "
      "WHERE routine_type='PROCEDURE'"
    ).results

    return state


  def kill_query(self):
    """
    Function: kill_query
    --------------------
    Kills the running query.
    """
    """
    if self.db and self.db.is_connected():
      try:
        # Gets the current thread ID of the database connection and attempts
        # to kill it.
        thread_id = self.db.connection_id
        self.db.cmd_process_kill(thread_id)

      except mysql.connector.errors.DatabaseError as e:
        # If this error is actually because the connection was successfully
        # terminated.
        if e.errno == 1927:
          pass
        # Otherwise, this is an actual error.
        else:
          err("Error while killing query: " + str(e))
          raise
    """ # TODO
    pass


  def release(self, savepoint):
    """
    Function: release
    -----------------
    Releases the named savepoint.

    savepoint: The savepoint to release.
    """
    if savepoint not in self.savepoints:
      return

    self.savepoints.remove(savepoint)
    self.run_query('RELEASE SAVEPOINT %s' % savepoint)


  def reset_state(self, old, new):
    """
    Functions: reset_state
    ----------------------
    Resets the state of the database from 'new' back to 'old'. This involves
    removing all functions, views, functions, and procedures that have been
    newly created.

    old: The old state of the database to be reverted back to.
    new: The new (current) state of the database.
    """
    new.subtract(old)

    # Drop all functions and procedures first.
    for proc in new.procedures:
      self.run_query('DROP PROCEDURE IF EXISTS %s' % proc)
    for func in new.functions:
      self.run_query('DROP FUNCTION IF EXISTS %s' % func)

    # Drop views.
    for view in new.views:
      self.run_query('DROP VIEW IF EXISTS %s' % view)

    # Drop tables. First must drop foreign keys on the tables in order to be
    # able to drop the tables without any errors.
    for (table, fk) in new.foreign_keys:
      self.run_query('ALTER TABLE %s DROP FOREIGN KEY %s' % (table, fk))
    for table in new.tables:
      self.run_query('DROP TABLE %s' % table)

    # Remove all savepoints.
    self.savepoints = []


  def rollback(self, savepoint=None):
    """
    Function: rollback
    ------------------
    Rolls back a database transaction, if currently in one. If a savepoint is
    named, rolls back to the named savepoint, otherwise, does a normal rollback
    which will remove all savepoints.

    savepoint: The savepoint to rollback to, if specified.
    """
    if self.db.in_transaction:
      # Roll back to the named savepoint. All savepoints created after this
      # savepoint are deleted.
      if savepoint and savepoint in self.savepoints:
        self.run_query('ROLLBACK TO %s' % savepoint)
        self.savepoints = self.savepoints[0:self.savepoints.index(savepoint)+1]
      else:
        self.db.rollback()
        self.savepoints = []


  def savepoint(self, savepoint):
    """
    Function: savepoint
    -------------------
    Creates a savepoint with the specified name.

    savepoint: The name of the savepoint.
    """
    self.run_query('SAVEPOINT %s' % savepoint) # TODO error in this query, what to do?
    # If this savepoint name already exists, add and remove it.
    if savepoint in self.savepoints:
      self.savepoints.remove(savepoint)
    self.savepoints.append(savepoint)


  def start_transaction(self):
    """
    Function: start_transaction
    ---------------------------
    Starts a database transaction, if not already in one.
    """
    if not self.db.in_transaction:
      self.db.start_transaction()

  # ----------------------------- Query Utilities ---------------------------- #

  def get_column_names(self):
    """
    Function: get_column_names
    --------------------------
    Gets the column names of the results.
    """
    if self.cursor.description is None:
      return []
    return [col[0] for col in self.cursor.description]


  def get_schema(self):
    """
    Function: get_schema
    --------------------
    Gets the schema of the result. Returns a list of tuples, where each tuple is
    of the form (column_name, type, None, None, None, None, null_ok, flags).
    """
    return self.cursor.description


  def prettyprint(self, results):
    """
    Function: prettyprint
    ---------------------
    Gets the pretty-printed version of the results.

    results: The results to pretty-print.
    returns: A string contained the pretty-printed results.
    """
    # If the results are too long, don't print it.
    if len(results) > MAX_NUM_RESULTS:
      return "Too many results (" + str(len(results)) + ") to print!"

    output = prettytable.PrettyTable(self.get_column_names())
    output.align = "l"
    for row in results:
      output.add_row(row)
    return output.get_string()


  def results(self):
    """
    Function: results
    -----------------
    Get the results of a query.
    """
    result = Result()

    # Get the query results and schema.
    rows = [row for row in self.cursor]
    if len(rows) > 0:
      result.results = rows
      result.schema = self.get_schema()
      result.col_names = self.get_column_names()

      # Pretty-print output.
      result.output = self.prettyprint(result.results)

      # If there are too many results.
      if len(result.results) > MAX_NUM_RESULTS:
        result.results = ["Too many results (" + str(len(rows)) + ") to print!"]

    return result


  def run_multi(self, queries):
    """
    Function: run_multi
    -------------------
    Runs multiple SQL statements at once.
    """
    # Consume old results if needed.
    [row for row in self.cursor]

    # Separate the CALL procedure statements.
    sql_list = queries.split("CALL")
    if len(sql_list) > 0:
      sql_list = \
          sqlparse.split(sql_list[0]) + ["CALL " + x for x in sql_list[1:]]
    else:
      sql_list = sqlparse.split(queries) # TODO test to see if this actually splits things?

    result = Result()
    for sql in sql_list:
      sql = sql.rstrip().rstrip(";")
      if len(sql) == 0:
        continue

      # If it is a CALL procedure statement, execute it differently.
      if sql.strip().startswith("CALL"):
        proc = str(sql[sql.find("CALL") + 5:sql.find("(")]).strip()
        args = sql[sql.find("(") + 1:sql.find(")")].split(",")
        args = tuple([str(arg.strip().rstrip("'").lstrip("'")) for arg in args])
        self.cursor.callproc(proc, args)
      else:
        try:
          self.cursor.execute(sql) # TODO should multi=True? 
          # TODO should breakdown the sql query so only one statement is executed
          # at at time...
        except mysql.connector.errors.InterfaceError: # TODO handle this...
          self.cursor.execute(sql, multi=True)
        result.append(self.results())

    # If no longer in a transaction, remove all savepoints.
    if not self.db.in_transaction:
      self.savepoints = []

    return result


  def run_query(self, query, setup=None, teardown=None):
    """
    Function: run_query
    -------------------
    Runs one or more queries as well as the setup and teardown necessary for
    that query (if provided).

    query: The query to run.
    setup: The setup query to run before executing the actual query.
    teardown: The teardown query to run after executing the actual query.

    returns: A Result object containing the result, the schema of the results
             and pretty-printed output.
    """
    # Run the query setup.
    result = Result()
    if setup is not None:
      self.run_multi(setup)

    try:
      result = self.run_multi(query)
    except mysql.connector.errors.ProgrammingError:
      raise

    # Always run the query teardown.
    finally:
      if teardown is not None:
        self.run_multi(teardown)
    return result
    # TODO get stuff from the cache? instead of in other things

  # ----------------------------- File Utilities ----------------------------- #

  def source_file(self, assignment, f):
    """
    Function: source_files
    ----------------------
    Sources a file into the database. Since the "source" command is for the
    MySQL command-line interface, we have to parse the source file and run
    each command one at a time.

    assignment: The assignment name, which is prepended to all the files.
    f: The source file to source.
    """
    f = codecs.open(ASSIGNMENT_DIR + assignment + "/" + f, "r", "utf-8")
    sql_list = sqlparse.split(preprocess_sql(f))
    for sql in sql_list:
      # Skip this line if there is nothing in it.
      if len(sql.strip()) == 0:
        continue
      # Otherwise execute each line. Output must be consumed for the query
      # to actually be executed.
      for _ in self.cursor.execute(sql.rstrip(), multi=True): pass
    f.close()


def import_file(assignment, f):
  """
  Function: import_files
  ----------------------
  Imports raw data files into the database. This uses the "mysqlimport"
  command on the terminal. We will have to invoke the command via Python.

  assignment: The assignment name, which is prepended to all the files.
  f: The file to import.
  """
  log("\nImporting file " + f + "...\n")
  filename = ASSIGNMENT_DIR + assignment + "/" + f
  subprocess.call("mysqlimport -h " + HOST + " -P " + PORT + " -u " + USER + \
                  " -p" + PASS + " --delete --local " + DATABASE + " " + \
                  filename)


def preprocess_sql(sql_file):
  """
  Function: preprocess_sql
  ------------------------
  Preprocess the SQL in order to handle the DELIMITER statements.

  sql_file: The SQL file to preprocess.
  returns: The newly-processed string containing SQL.
  """
  lines = StringIO()
  delimiter = ';'
  for line in sql_file:
    # See if there is a new delimiter.
    match = re.match(DBTools.DELIMITER_RE, line)
    if match:
      delimiter = match.group(1)
      continue

    # If we've reached the end of a statement.
    if line.strip().endswith(delimiter):
      line = line.replace(delimiter, ";")
    lines.write(line)

  return lines.getvalue()
