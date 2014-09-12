"""
Module: sqltools
----------------
Contains tools to help with parsing and checking SQL.
"""

import re
from cStringIO import StringIO

# Used to find delimiters in the file.
DELIMITER_RE = re.compile(r"^\s*delimiter\s+([^\s]+)\s*$", re.I)

def check_valid_query(query, query_type):
  """
  Function: check_valid_query
  ---------------------------
  Check to see that a query is a valid query (i.e. it is not a malicious query).
  Does this by making sure the query_type is found in the query and that there
  are no other SQL statements being run. For example, if the query_type is an
  INSERT statement, makes sure that the 'INSERT' keyword is found in the query.

  This does not work for multi-statement SQL queries, such as CREATE TABLEs.

  Obviously this is not perfect and plenty of statements can get through.
  However, it should be sufficient unless there are some very evil students.

  query: The query to check.
  query_type: The query type (e.g. INSERT, DELETE, CREATE TABLE).
  returns: True if the query is valid, False otherwise.
  """
  return (
    # Make sure the query type can be found in the query.
    query.lower().find(query_type.lower()) != -1 and
    # Make sure there is only one SQL statement.
    query.strip().rstrip(";").find(";") == -1
  )


def preprocess_sql(sql_file):
  """
  Function: preprocess_sql
  ------------------------
  Preprocess the SQL in order to handle the DELIMITER statements.

  sql_file: The SQL file to preprocess.
  returns: The newly-processed SQL stringL.
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
