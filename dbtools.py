import codecs
from cStringIO import StringIO
from CONFIG import *
from models import Result
import mysql.connector
import re
import signal
import sqlparse
import subprocess
import prettytable
import timeouts

# Used to find delimiters in the file.
DELIMITER_RE = re.compile(r"^\s*delimiter\s+([^\s]+)\s*$", re.I)

class DBTools:
  """
  Class: DBTools
  --------------
  Contains helper methods involving the database and queries.
  """

  def __init__(self):
    # The database connection parameters are specified in the CONFIG.py file.
    self.db = None

    # The database cursor.
    self.cursor = None

    # Register the timeout handler.
    signal.signal(signal.SIGALRM, timeouts.timeout_handler)

  # --------------------------- Database Utilities --------------------------- #

  def close_db_connection(self):
    """
    Function: close_db_connection
    -----------------------------
    Close the database connection (only if it is already open) and any running
    queries.
    """
    if self.db:# and self.db.is_connected():
      self.kill_query()
      # TODO self.cursor.close()
      self.db.close()


  def kill_query(self):
    """
    Function: kill_query
    --------------------
    Kills the running query.
    """
    if not self.db:
      return

    #self.close_db_connection()
    #self.db.close()
    self.get_db_connection()
    try:
      self.db.cmd_process_kill(self.thread_id)
    except Exception:
      print "Killed thread", str(self.thread_id) # TODO
      pass

    # Get a new connection no matter what.
    finally:
      self.get_db_connection()


  def get_cursor(self):
    """
    Function: get_cursor
    --------------------
    Gets the cursor. Assumes the database has already been connected.
    """
    return self.cursor


  def get_db_connection(self):
    """
    Function: get_db_connection
    ---------------------------
    Gets the current database connection or creates a new one if it doesn't
    exist or disconnected.

    returns: A database connection object.
    """
    # Connect to the database.
    #if not self.db: #or not self.db.is_connected():
    self.db = mysql.connector.connect(user=USER, password=PASS, host=HOST, \
      database=DATABASE, port=PORT, autocommit=True)
    self.cursor = self.db.cursor()

    return self.db

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


  def results(self, iterator):
    """
    Function: results
    -----------------
    Get the results of a query.
    """
    results = Result()

    # Loop through all the query results (there could be many).
    for query in iterator:
      rows = [row for row in query]
      if len(rows) == 0:
        continue

      result = Result()
      result.results = rows
      result.schema = self.get_schema()
      result.col_names = self.get_column_names()

      # Pretty-print output.
      result.output = self.prettyprint(result.results)

      # If there are too many results.
      if len(result.results) > MAX_NUM_RESULTS:
        result.results = ["Too many results (" + str(len(rows)) + ") to print!"]

      results.append(result)

    return results


  def run_multi(self, queries):
    """
    Function: run_multi
    -------------------
    Runs multiple SQL statements at once.
    """
    print "Executing: " + queries

    # Get the thread ID of the query.
    self.thread_id = self.db.connection_id # TODO replace tabs with spaces
    iterator = self.cursor.execute(queries.replace("\t", "  "), multi=True)
    return self.results(iterator)


  def run_query(self, query, setup=None, teardown=None, timeout=None):
    """
    Function: run_query
    -------------------
    Runs one or more queries as well as the setup and teardown necessary for that
    query (if provided).

    query: The query to run.
    setup: The setup query to run before executing the actual query.
    teardown: The teardown query to run after executing the actual query.

    returns: A Result object containing the result, the schema of the results and
             pretty-printed output.
    """
    # Query setup.
    result = Result()
    if setup is not None:
      self.run_multi(setup)

    # Set to default timeout if none specified.
    signal.alarm(timeout or CONNECTION_TIMEOUT)
    print "Timeout:", str(timeout)
    try:
      result = self.run_multi(query)
    # Kill the query if it takes too long.
    except timeouts.TimeoutError:
      self.kill_query()
      raise

    # Always run the query teardown.
    finally:
      signal.alarm(0)
      if teardown is not None:
        self.run_multi(teardown)
    return result

  # ----------------------------- File Utilities ----------------------------- #

  def source_files(self, assignment, files):
    """
    Function: source_files
    ----------------------
    Sources files into the database. Since the "source" command is for the
    MySQL command-line interface, we have to parse the source file and run
    each command one at a time.

    assignment: The assignment name, which is prepended to all the files.
    files: The source files to source.
    """
    if len(files) == 0:
      return

    # Loop through each source file.
    for source in files:
      f = codecs.open(assignment + "/" + source, "r", "utf-8")
      sql_list = sqlparse.split(preprocess_sql(f))
      for sql in sql_list:
        # Skip this line if there is nothing in it.
        if len(sql.strip()) == 0:
          continue
        for _ in self.cursor.execute(sql.rstrip(), multi=True): pass
      f.close()


def import_files(assignment, files):
  """
  Function: import_files
  ----------------------
  Imports raw data files into the database. This uses the "mysqlimport"
  command on the terminal. We will have to invoke the command via Python.

  assignment: The assignment name, which is prepended to all the files.
  files: The files to import.
  """
  if len(files) == 0:
    return

  print "\nImporting files..."
  # Import all the data files.
  files = " ".join([assignment + "/" + f for f in files])
  subprocess.call("mysqlimport -h " + HOST + " -P " + PORT + " -u " + USER + \
    " -p" + PASS + " --delete --local " + DATABASE + " " + files)


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
    match = re.match(DELIMITER_RE, line)
    if match:
      delimiter = match.group(1)
      continue

    # If we've reached the end of a statement.
    if line.strip().endswith(delimiter):
      line = line.replace(delimiter, ";")
    lines.write(line)

  return lines.getvalue()


def run_script(script):
  """
  Function: run_script
  --------------------
  Runs a script.

  returns: The output from the script.
  """
  print "running", script
  return subprocess.check_output(script, stderr=subprocess.STDOUT, shell=True)
