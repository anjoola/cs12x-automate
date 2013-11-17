"""
Module: dbtools
---------------
Contains helper methods involving the database and queries.
"""

import codecs
import mysql.connector
import sqlparse
import prettytable
from models import Result

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

  # TODO source files in a better way
  def quote(value):
    """
    Function: quote
    ---------------
    Puts quotes around a value to be used in an INSERT statement. If the value
    is null, then change it to the MySQL syntax.
    """
    if value == "\N":
      return "NULL"
    else:
      return "'" + str(value) + "'"

  if len(files) <= 0:
    return

  # Loop through each source file.
  for source in files:
    # If the source is a SQL file, run it.
    if source.find(".sql") != -1:
      f = codecs.open(source, "r", "utf-8")
      sql_list = sqlparse.split(f.read())
      for sql in sql_list:
        if len(sql.strip()) == 0:
          continue
        cursor.execute(sql)
      f.close()

    # If the source is a TSV file, then read each line individually and
    # insert the values into the database.
    else:
      data = open(source, "r")
      # Assume the table name is the source file name.
      table = source[source.rfind("/") + 1:source.rfind(".")]
      for row in data:
        insert = "INSERT INTO " + table + " VALUES(" + \
          ", ".join([quote(x) for x in row.strip().split("\t")]) + \
          ");"
        cursor.execute(insert)
      data.close()


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
  if "source" in setup:
    source_files(setup["source"], cursor)

  # Query setup.
  if "setup" in setup:
    cursor.execute(setup["setup"])
  cursor.execute(query)

  # Get the query results and schema.
  result = Result()
  result.results = [row for row in cursor]
  result.schema = get_schema(cursor)
  result.col_names = get_column_names(cursor)

  # Truncate the output if it is too long.
  output_results = result.results
  if len(output_results) > 15:
    output_results = result.results[0:7]
    filler = ("   ...  ", ) * len(output_results[0])
    output_results += [filler] + result.results[-7:]

  # Pretty-print output.
  output = prettytable.PrettyTable(get_column_names(cursor))
  output.align = "l"
  for row in output_results:
    output.add_row(row)
  result.output = output.get_string()

  # Query teardown.
  if "teardown" in setup:
    cursor.execute(setup["teardown"])
  return result
