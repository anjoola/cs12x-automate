"""
Module: dbtools
---------------
Contains helper methods involving the database and queries.
"""

import mysql.connector
import sqlparse
import prettytable
from response import Result

def source_files(files, cursor):
  """
  Function: source_files
  ----------------------
  Sources files into the database. Since the "source" command is for the
  MySQL command-line interface, we have to parse the source file and run
  each command one at a time.

  files: The source files to source.
  cursor: The database cursor.
  """
  if len(files) <= 0:
    return

  # Loop through each source file.
  for source in files:
    sql = open(source).read()
    sql_list = sqlparse.split(sql)
    for sql in sql_list:
      if len(sql.strip()) == 0:
        continue
      cursor.execute(sql)


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


def get_column_names(cursor):
  """
  Function: get_column_names
  --------------------------
  Gets the column names of the results.
  """
  return [col[0] for col in cursor.description]


def run_query(setup, query, cursor):
  """
  Function: run_query
  -------------------
  Runs a query and does all the setup and teardown required for the query.

  setup: A JSON object containing the setup for the query.
  query: The query to run.
  cursor: The database cursor.

  returns: A Result object containing the result, the schema of the results and
           pretty-printed output.
  """
  # Source files to insert data needed for the query.
  source_files(setup["source"], cursor)

  # Query setup.
  cursor.execute(setup["setup"])
  cursor.execute(query)

  # Get the query results and schema.
  result = Result()
  result.results = [row for row in cursor]
  result.schema = get_schema(cursor)

  # Pretty-print output.
  output = prettytable.PrettyTable(get_column_names(cursor))
  output.align = "l"
  for row in result.results:
    output.add_row(row)
  result.output = output.get_string()

  # Query teardown.
  cursor.execute(setup["teardown"])
  return result
