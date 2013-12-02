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

# ------------------------------ File Utilities ------------------------------ #

def import_files(assignment, files):
  """
  Function: import_files
  ----------------------
  Imports raw data files into the database. This uses the "mysqlimport"
  command on the terminal. We will have to invoke the command via python.

  assignment: The assignment name. Is prepended to all the files.
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


def source_files(assignment, files, cursor):
  """
  Function: source_files
  ----------------------
  Sources files into the database. Since the "source" command is for the
  MySQL command-line interface, we have to parse the source file and run
  each command one at a time.

  assignment: The assignment name. Is prepended to all the files.
  files: The source files to source.
  cursor: The database cursor.
  """

  if len(files) == 0:
    return

  # Loop through each source file.
  for source in files:
    # If the source is a SQL file, run it.
    if source.find(".sql") != -1:
      f = codecs.open(assignment + "/" + source, "r", "utf-8")
      sql_list = sqlparse.split(preprocess_sql(f))
      for sql in sql_list:
        # Skip this line if there is nothing in it.
        if len(sql.strip()) == 0:
          continue
        for _ in cursor.execute(sql, multi=True): pass
      f.close()

# ---------------------------- Database Utilities ---------------------------- #

def get_column_names(cursor):
  """
  Function: get_column_names
  --------------------------
  Gets the column names of the results.
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


def run_query(setup, query, teardown, cursor):
  """
  Function: run_query
  -------------------
  Runs a query and does all the setup and teardown required for the query.

  setup: The setup query to run before executing the actual query.
  query: The query to run.
  teardown: The teardown query to run after executing the actual query.
  cursor: The database cursor.

  returns: A Result object containing the result, the schema of the results and
           pretty-printed output.
  """
  # Query setup.
  if setup is not None:
    for _ in cursor.execute(setup, multi=True): pass
  cursor.execute(query)

  # Get the query results and schema.
  result = Result()
  result.results = [row for row in cursor]
  result.schema = get_schema(cursor)
  result.col_names = get_column_names(cursor)

  # Pretty-print output.
  result.output = prettyprint(cursor, result.results)

  # Query teardown.
  if teardown is not None:
    for _ in cursor.execute(teardown, multi=True): pass
  return result


def prettyprint(cursor, results):
  """
  Function: prettyprint
  ---------------------
  TODO
  """
  output = prettytable.PrettyTable(get_column_names(cursor))
  output.align = "l"
  for row in results:
    output.add_row(row)
  return output.get_string()
