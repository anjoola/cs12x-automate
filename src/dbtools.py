"""
Module: dbtools
---------------
Contains helper methods involving the database, its state, and queries.
"""
import codecs
import os
import subprocess

import mysql.connector
import mysql.connector.errors

from cache import Cache
from CONFIG import *
from errors import DatabaseError, TimeoutError
from iotools import (
  err,
  log,
  prettyprint
)
from models import DatabaseState, Result
from sqltools import preprocess_sql, split
from terminator import Terminator

class DBTools:
  """
  Class: DBTools
  --------------
  Handles requests to a particular database (as specified in the CONFIG file).
  """

  def __init__(self, user, database):
    # The database connection parameters are specified in the CONFIG.py file.
    # Contains the reference to the database object.
    self.db = None

    # The database cursor.
    self.cursor = None

    # The current connection timeout limit.
    self.timeout = CONNECTION_TIMEOUT

    # The savepoints.
    self.savepoints = []

    # The user to connect with. If no user is specified, picks the first user
    # in the dictionary.
    self.user = user if user is not None else LOGIN.keys()[0]

    # The name of the database to connect to. If none is specified, use
    # <user>_db as the default database.
    self.database = database if database is not None else "%s_db" % user

    # Separate database connection used to terminate queries. If the terminator
    # cannot start, the grading cannot occur.
    try:
      self.terminator = Terminator(self.user, self.database)
    except mysql.connector.errors.Error:
      err("Could not start up terminator connection! Any unruly queries " +
          "must be manually killed!")

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
      #for _ in self.cursor: pass

      # Kill any remaining queries and close the database connection.
      try:
        self.kill_query()
        self.cursor.close()
        self.db.close()
      except mysql.connector.errors.Error as e:
        raise DatabaseError(e)


  def commit(self):
    """
    Function: commit
    ----------------
    Commits the current transaction. Destroys any savepoints.
    """
    try:
      self.db.commit()
    except mysql.connector.errors.Error as e:
      raise DatabaseError(e)
    self.savepoints = []


  def get_cursor(self):
    """
    Function: get_cursor
    --------------------
    Gets the cursor. Assumes the database has already been connected.
    """
    return self.cursor


  def get_db_connection(self, timeout=None, close=True):
    """
    Function: get_db_connection
    ---------------------------
    Get a new database connection with a specified timeout (defaults to
    CONNECTION_TIMEOUT specified in the CONFIG file). Closes the old connection
    if there was one.

    timeout: The connection timeout.
    close: Whether or not to close the old database connection beforehand.
           Should set to False if a timeout occurred just before the call to
           this function.
    returns: A database connection object.
    """
    if self.db and self.db.is_connected():
      # If timeout isn't specified, check if we're already at the default.
      if timeout is None and self.timeout == CONNECTION_TIMEOUT:
        return self.db
      # If the timeout is the same as before, then don't change anything.
      if timeout is not None and timeout == self.timeout:
        return self.db

    # Close any old connections and make another one with the new setting.
    if close:
      self.close_db_connection()
    self.timeout = timeout or CONNECTION_TIMEOUT
    log("New timeout: %d" % self.timeout)
    try:
      self.db = mysql.connector.connect(user=self.user,
                                        password=LOGIN[self.user],
                                        host=HOST,
                                        database=self.database,
                                        port=PORT,
                                        connection_timeout=self.timeout,
                                        autocommit=False)
      self.cursor = self.db.cursor(buffered=True)
    except mysql.connector.errors.Error as e:
      raise DatabaseError(e)
    return self


  def get_state(self):
    """
    Function: get_state
    -------------------
    Gets the current state of the database, which includes the tables, foreign,
    keys, views, functions, procedures, and triggers.

    returns: A DatabaseState object which contains the current state.
    """
    state = DatabaseState()
  
    try:
      # Get tables and their foreign keys.
      state.tables = self.execute_sql(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_type='BASE TABLE'"
      ).results
      state.foreign_keys = self.execute_sql(
        "SELECT DISTINCT table_name, constraint_name FROM "
        "information_schema.table_constraints WHERE constraint_type='FOREIGN KEY'"
      ).results
  
      # Get views, functions, procedures, and triggers.
      state.views = self.execute_sql(
        "SELECT table_name FROM information_schema.views"
      ).results
      state.functions = self.execute_sql(
        "SELECT routine_name FROM information_schema.routines "
        "WHERE routine_type='FUNCTION'"
      ).results
      state.procedures = self.execute_sql(
        "SELECT routine_name FROM information_schema.routines "
        "WHERE routine_type='PROCEDURE'"
      ).results
      state.triggers = self.execute_sql(
        "SELECT trigger_name FROM information_schema.triggers"
      ).results
    except (mysql.connector.errors.Error, DatabaseError, TimeoutError):
      err("Could not get the database state. Future gradings are possibly " +
          "affected.")

    return state


  def kill_query(self):
    """
    Function: kill_query
    --------------------
    Kills the running query by terminating the connection.
    """
    if not self.db or not self.db.is_connected(): return

    thread_id = self.db.connection_id
    try:
      self.terminator.terminate(thread_id)
    except mysql.connector.errors.Error:
      err("Unable to kill %d (was probably already killed)." % thread_id)
    # If the terminator doesn't even exist, then this is a problem.
    except AttributeError:
      err("Terminator doesn't exist to kill queries!", True)
    self.savepoints = []


  def purge_db(self):
    """
    Function: purge_db
    ------------------
    Remove everything from the database.
    """
    state = self.get_state()
    self.reset_state(DatabaseState(), state)


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
    try:
      self.execute_sql("RELEASE SAVEPOINT %s" % savepoint)
    except mysql.connector.errors.Error:
      pass


  def reset_state(self, old, new):
    """
    Function: reset_state
    ---------------------
    Resets the state of the database from 'new' back to 'old'. This involves
    removing all functions, views, functions, procedures, and triggers that
    have been newly created.

    old: The old state of the database to be reverted back to.
    new: The new (current) state of the database.
    """
    new.subtract(old)

    try:
      # Drop all functions procedures, and triggers first.
      for trig in new.triggers:
        self.execute_sql("DROP TRIGGER IF EXISTS %s" % trig)
      for proc in new.procedures:
        self.execute_sql("DROP PROCEDURE IF EXISTS %s" % proc)
      for func in new.functions:
        self.execute_sql("DROP FUNCTION IF EXISTS %s" % func)
  
      # Drop views.
      for view in new.views:
        self.execute_sql("DROP VIEW IF EXISTS %s" % view)
  
      # Drop tables. First must drop foreign keys on the tables in order to be
      # able to drop the tables without any errors.
      for (table, fk) in new.foreign_keys:
        self.execute_sql("ALTER TABLE %s DROP FOREIGN KEY %s" % (table, fk))
      for table in new.tables:
        self.execute_sql("DROP TABLE IF EXISTS %s" % table)
    except (mysql.connector.errors.Error, DatabaseError, TimeoutError):
      err("Could not reset database state. Possible errors in future grading.")

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
        self.execute_sql("ROLLBACK TO %s" % savepoint)
        self.savepoints = self.savepoints[0:self.savepoints.index(savepoint)+1]
      else:
        try:
          self.db.rollback()
        except mysql.connector.errors.Error as e:
          raise DatabaseError(e)
        self.savepoints = []


  def savepoint(self, savepoint):
    """
    Function: savepoint
    -------------------
    Creates a savepoint with the specified name.

    savepoint: The name of the savepoint.
    """
    try:
      self.execute_sql("SAVEPOINT %s" % savepoint)
    except mysql.connector.errors.Error:
      err("Could not create savepoint %s!" % savepoint)

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
    self.db.commit()
    if not self.db.in_transaction:
      try:
        self.db.start_transaction()
      except mysql.connector.errors.Error as e:
        raise DatabaseError(e)

  # ----------------------------- Query Utilities ---------------------------- #

  def execute_sql(self, sql, setup=None, teardown=None, cached=False):
    """
    Function: execute_sql
    ---------------------
    Runs one or more queries as well as the setup and teardown necessary for
    that query (if provided).

    sql: The SQL query to run.
    setup: The setup query to run before executing the actual query.
    teardown: The teardown query to run after executing the actual query.
    cached: Whether or not the result should be pulled from the cache. True if
            so, False otherwise.

    returns: A Result object containing the result.
    """
    # Run the query setup.
    result = Result()
    if setup is not None:
      self.run_multi(setup)

    try:
      result = self.run_multi(sql, cached)

    # Run the query teardown.
    finally:
      if teardown is not None:
        self.run_multi(teardown)
    return result


  def get_column_names(self):
    """
    Function: get_column_names
    --------------------------
    Gets the column names of the results.
    """
    if self.cursor.description is None:
      return []
    return [col[0] for col in self.cursor.description]


  def get_results(self):
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

      # Pretty-printed output.
      result.output = prettyprint(result.results, self.get_column_names())

    return result


  def get_schema(self):
    """
    Function: get_schema
    --------------------
    Gets the schema of the result. Returns a list of tuples, where each tuple is
    of the form (column_name, type, None, None, None, None, null_ok, flags).
    """
    return self.cursor.description


  def run_multi(self, queries, cached=False):
    """
    Function: run_multi
    -------------------
    Runs multiple SQL statements at once.
    """
    # Consume old results if needed.
    [row for row in self.cursor]
    sql_list = split(queries)

    result = Result()
    for sql in sql_list:
      sql = sql.rstrip().rstrip(";")
      if len(sql) == 0:
        continue

      query_results = Cache.get(sql)

      # Results are not to be cached or are not in the cache and needs to
      # be cached. Run the query.
      if not query_results or not cached:
        try:
          self.cursor.execute(sql)

        # If the query times out.
        except mysql.connector.errors.OperationalError:
          raise TimeoutError

        # If something is wrong with their query.
        except mysql.connector.errors.ProgrammingError as e:
          raise DatabaseError(e)

        # If the query can't be run as a single query, attempt to do it with a
        # multi-line query.
        except mysql.connector.errors.Error as e:
          try:
            self.cursor.execute(sql, multi=True)
          except mysql.connector.errors.Error as e:
            raise DatabaseError(e)

        query_results = self.get_results()
        if cached:
          Cache.put(sql, query_results)

      result = query_results

    # If no longer in a transaction, remove all savepoints.
    if not self.db.in_transaction:
      self.savepoints = []

    return result

  # ----------------------------- File Utilities ----------------------------- #

  def import_file(self, assignment, f):
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

    # Make sure the file exists.
    if not os.path.exists(filename):
      err("File to import %s does not exist!" % filename, True)
    try:
      subprocess.call("mysqlimport -h " + HOST + " -P " + PORT + " -u " +
                      self.user + " -p" + LOGIN[self.user] +
                      " --delete --local " + self.database + " " + filename)
    except OSError:
      err("Could not import file %s! The 'mysqlimport' library does not exist!",
          True)


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
    try:
      fname = ASSIGNMENT_DIR + assignment + "/" + f
      f = codecs.open(fname, "r", "utf-8")
    except IOError:
      err("Could not find or open sourced file %s!" % fname, True)

    sql_list = split(preprocess_sql(f))
    for sql in sql_list:
      # Skip this line if there is nothing in it.
      if len(sql.strip()) == 0:
        continue
      # Otherwise execute each line. Output must be consumed for the query
      # to actually be executed.
      for _ in self.cursor.execute(sql.rstrip(), multi=True): pass
      self.commit()
    f.close()
