"""
Module: dbtools
---------------
Contains helper methods involving the database and queries.
"""

import codecs
from cStringIO import StringIO
from CONFIG import *
import mysql.connector
import sqlparse
import subprocess
import prettytable
from models import Result

# The database connection. Parameters are specified in the CONFIG.py file.
DB = None

# ------------------------------ File Utilities ------------------------------ #

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
    if line.find("DELIMITER") != -1:
      delimiter = line.strip()[-1:]
      continue

    # If we've reached the end of a statement.
    if line.strip().endswith(delimiter):
      line = line.replace(delimiter, ";")
    lines.write(line)

  return lines.getvalue()


def source_files(assignment, files):
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
      for _ in DB.cursor().execute(sql, multi=True): pass
    f.close()

# ---------------------------- Database Utilities ---------------------------- #

def close_db_connection():
  """
  Function: close_db_connection
  -----------------------------
  Close the database connection (only if it is already open).
  """
  if DB.is_connected():
    DB.cursor().close()
    DB.close()


def get_db_connection(timeout=None):
  """
  Function: get_db_connection
  ---------------------------
  Get a new database connection with a specified timeout (defaults to
  CONNECTION_TIMEOUT specified in the CONFIG file). Closes the old connection
  if there was one.

  timeout: The connection timeout.
  returns: A database connection object.
  """
  global DB
  # Create a new connection if haven't connected yet.
  if DB is None or not DB.is_connected():
    DB = mysql.connector.connect(user=USER, password=PASS, host=HOST, \
      database=DATABASE, port=PORT, connection_timeout=CONNECTION_TIMEOUT)
  # If a timeout is specified, close the old connection and make a new one
  # with the new timeout settings.

  elif timeout is not None:
    close_db_connection()
    DB = mysql.connector.connect(user=USER, password=PASS, host=HOST, \
      database=DATABASE, port=PORT, connection_timeout=timeout)
  return DB

# ------------------------------ Query Utilities ----------------------------- #

def get_column_names(cursor):
  """
  Function: get_column_names
  --------------------------
  Gets the column names of the results.

  cursor: The database cursor.
  returns: A list of strings containing the column names.
  """
  if cursor.description is None:
    return []
  return [col[0] for col in cursor.description]


def get_schema(cursor):
  """
  Function: get_schema
  --------------------
  Gets the schema of the result. Returns a list of tuples, where each tuple is
  of the form (column_name, type, None, None, None, None, null_ok, flags).

  cursor: The database cursor.
  returns: A list of tuples representing the schema.
  """
  return cursor.description


def prettyprint(cursor, results):
  """
  Function: prettyprint
  ---------------------
  Gets the pretty-printed version of the results.

  cursor: The database cursor.
  results: The results to pretty-print.
  returns: A string contained the pretty-printed results.
  """
  output = prettytable.PrettyTable(get_column_names(cursor))
  output.align = "l"
  for row in results:
    output.add_row(row)
  return output.get_string()


def run_multi(cursor, queries):
  """
  Function: run_multi
  -------------------
  Runs multiple SQL statements at once.

  cursor: The database cursor.
  queries: The queries to run.
  """
  sql_list = sqlparse.split(queries)
  for sql in sql_list:
    if len(sql.strip()) > 0:
      cursor.execute(sql)


def run_query(cursor, query, setup=None, teardown=None):
  """
  Function: run_query
  -------------------
  Runs one or more queries as well as the setup and teardown necessary for that
  query (if provided).

  cursor: The database cursor.
  query: The query to run.
  setup: The setup query to run before executing the actual query.
  teardown: The teardown query to run after executing the actual query.

  returns: A Result object containing the result, the schema of the results and
           pretty-printed output.
  """
  # Query setup.
  if setup is not None:
    run_multi(cursor, setup)
  run_multi(cursor, query)

  # Get the query results and schema.
  result = Result()
  result.results = [row for row in cursor]
  result.schema = get_schema(cursor)
  result.col_names = get_column_names(cursor)

  # Pretty-print output.
  result.output = prettyprint(cursor, result.results)

  # Query teardown.
  if teardown is not None:
    run_multi(cursor, teardown)
  return result
