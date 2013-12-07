import codecs
from cStringIO import StringIO
from CONFIG import *
import mysql.connector
import re
import sqlparse
import subprocess
import multiprocessing
from time import sleep
import prettytable
from models import Result

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

    # The current connection timeout.
    self.timeout = CONNECTION_TIMEOUT
    
    self.stop_timer = False
    self.stop_query = False
  # --------------------------- Database Utilities --------------------------- #

  def close_db_connection(self):
    """
    Function: close_db_connection
    -----------------------------
    Close the database connection (only if it is already open) and any running
    queries.
    """
    if not self.db:
      return

    try:
      self.kill_query()
      self.cursor.close()
      self.db.close()
    except Exception:
      pass


  def kill_query(self):
    if self.db and self.db.is_connected():
      try:
        thread_id = self.db.connection_id
        self.db.cmd_process_kill(thread_id)
      except mysql.connector.errors.DatabaseError:
        pass


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
    Get a new database connection with a specified timeout (defaults to
    CONNECTION_TIMEOUT specified in the CONFIG file). Closes the old connection
    if there was one.

    returns: A database connection object.
    """
    if self.db and self.db.is_connected():
      return self.db

    self.db = mysql.connector.connect(user=USER, password=PASS, host=HOST, \
      database=DATABASE, port=PORT, connection_timeout=self.timeout, \
      autocommit=True)
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

    returns: A Result object containing the results of the query.
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

    return result


  def run_multi(self, queries):
    """
    Function: run_multi
    -------------------
    Runs multiple SQL statements at once.
    """
    sql_list = queries.split("CALL")
    sql_list = sqlparse.split(queries)
    result = Result()
    for sql in sql_list:
      sql = sql.rstrip().rstrip(";")
      if len(sql) == 0:
        continue

      try:
        query_thread = multiprocessing.Process(target=self.do_query, args=(sql,))
        #query_thread = multiprocessing.Process(target=do_query, args=(self.cursor, sql,))
        query_thread.start()
        
        query_thread.join(self.timeout)
        finished_query = not query_thread.is_alive()
        if not finished_query:
          query_thread.terminate()
          query_thread.join()
          
        if not finished_query:
          raise mysql.connector.errors.ProgrammingError
        print "terminated thread"
        
        # get results of query
        result.append(self.results())
      except IOError as e: # TODO rename this
        # kill the running query
        print str(e)
        self.kill_query()
        print "query killed"
        raise mysql.connector.errors.ProgrammingError
                                              
    return result

  def set_timeout(self, timeout):
    if timeout is None:
      self.timeout = CONNECTION_TIMEOUT
    else:
      self.timeout = timeout

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
    if timeout:
      self.set_timeout(timeout)

    # Query setup.
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

  def do_query(self, sql):
  #def do_query(cursor, sql):
    print "Executing:", sql
    #cursor.execute(sql)


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



