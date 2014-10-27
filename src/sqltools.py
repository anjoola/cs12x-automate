"""
Module: sqltools
----------------
Contains tools to help with parsing and checking SQL.
"""

import re
from cStringIO import StringIO

# Used to find delimiters in the file.
DELIMITER_RE = re.compile(r"^\s*delimiter\s*([^\s]+)\s*$", re.I)

# Dictionary of keywords of the form <start keyword> : <end keyword>. If
# <end keyword> is empty, then this kind of statement ends with a semicolon.
KEYWORDS_DICT = {
  "ALTER TABLE": "",
  "CALL": "",
  "COMMIT": "",
  "CREATE FUNCTION": "END",
  "CREATE INDEX": "",
  "CREATE PROCEDURE": "END",
  "CREATE TABLE" : ");",
  "CREATE TRIGGER": "END",
  "CREATE VIEW": "",
  "DELETE": "",
  "DO": "",
  "DROP FUNCTION": "",
  "DROP INDEX": "",
  "DROP PROCEDURE": "",
  "DROP TABLE": "",
  "DROP TRIGGER": "",
  "DROP VIEW": "",
  "HANDLER": "",
  "INSERT" : "",
  "LOAD DATA": "",
  "RELEASE SAVEPOINT": "",
  "REPLACE": "",
  "ROLLBACK": "",
  "SAVEPOINT": "",
  "SELECT": "",
  "START TRANSACTION": "",
  "UPDATE": "",
}
KEYWORDS = KEYWORDS_DICT.keys()

# Control keywords. Used to figure out where a function begins and ends.
CTRL_KEYWORDS = [
  ("CASE", "END CASE"),
  ("IF", "END IF"),
  ("WHILE", "END WHILE"),
  ("BEGIN", "END")
]
CTRL_KEYWORDS_IGNORE = [
  "ELSEIF"
]

# Types of quotes.
QUOTES = ['\'', '\"']

def check_valid_query(query, query_type):
  """
  Function: check_valid_query
  ---------------------------
  Check to see that a query is a valid query (i.e. it is not a malicious query).
  Does this by making sure the query_type is found in the beginning of the query
  and that there are no other SQL statements being run. For example, if the
  query_type is an INSERT statement, makes sure that the 'INSERT' keyword is
  found in the beginning of query.

  This does not work for multi-statement SQL queries, such as CREATE TABLEs.

  Obviously this is not perfect and plenty of statements can get through.
  However, it should be sufficient unless there are some very evil students.

  query: The query to check.
  query_type: The query type (e.g. INSERT, DELETE, SELECT).
  returns: True if the query is valid, False otherwise.
  """
  return True
  # TODO: This is turned off because students like to put code before their
  #       answer, causing this function to return false negatives. Really,
  #       this function needs to be improved.
  return (
    # Make sure the query type can be found in the query.
    query.lower().strip().find(query_type.lower()) == 0 and
    # Make sure there is only one SQL statement.
    query.strip().strip().rstrip(";").find(";") == -1
  )


def find_valid_sql(query, query_type):
  """
  Function: find_valid_sql
  ------------------------
  Finds the valid SQL statement of query_type within a large SQL statement. If
  it cannot be found, return None.

  query: The query to search within.
  query_type: The query type (e.g. INSERT, DELETE, SELECT).
  returns: The query if valid SQL can be found, False otherwise.
  """
  if query.lower().strip().find(query_type.lower()) == 0:
    return query.strip()[0:query.strip().find(";")]
  else:
    return None


def split(raw_sql):
  """
  Function: split
  ---------------
  Splits SQL into separate statements.
  """

  def find_keyword(sql, keyword, start_idx=0):
    """
    Function: find_keyword
    ----------------------
    Finds a SQL keyword within a statement as long as it is not enclosed
    by quotes.

    sql: The SQL to search within.
    keyword: The keyword to search for.
    start_idx: Where to start searching for the keyword.

    returns: The starting index of the keyword.
    """
    quotes = []
    comment_type = None

    while True:
      idx = sql.find(keyword, start_idx)
      if idx == -1:
        return -1

      # Make sure not surrounded by quotes.
      for i in range(start_idx, idx):
        # Make sure this is not a quote within a comment.
        if sql[i:].startswith("/*"):
          comment_type = "block"
          i += 1
        elif comment_type == "block" and sql[i:].startswith("*/"):
          comment_type = None
          i += 1
        elif sql[i:].startswith("--"):
          comment_type = "single"
          i += 1
        elif comment_type == "single" and sql[i:].startswith("\n"):
          comment_type = None
          i += 1
        elif comment_type is None and sql[i] in QUOTES:
          if len(quotes) > 0 and quotes[-1] == sql[i]:
            quotes.pop()
          else:
            quotes.append(sql[i])

      # If the keyword is "END", make sure it wasn't an END WHILE, END LOOP,
      # END IF, etc. If it is, continue.
      if keyword.lower() == "end":
        result = re.sub('\s+', ' ', sql[i:]).strip()
        if not (result.startswith("end;") or
                result.startswith("end ;") or
                result == "end"):
          if idx + 1 < len(sql):
            start_idx = idx + 1
            continue
          else:
            return -1

      # If not surrounded by quotes, then this is the keyword.
      if len(quotes) == 0:
        return idx

      # Otherwise, continue if possible.
      if idx + 1 < len(sql):
        start_idx = idx + 1

      # Could not find keyword.
      else:
        return -1

  def get_start_idx(sql, keyword):
    """
    Function: get_start_idx
    -----------------------
    Checks if this SQL statement starts with this keyword, ignoring comments.

    sql: The SQL to search.
    keyword: The keyword to search for.
    returns: THe starting index of the keyword if found, -1 otherwise.
    """
    start_idx = 0
    while start_idx < len(sql):
      clean_sql = sql[start_idx:].strip()

      # Ignore comments.
      if clean_sql.startswith("/*"):
        end_idx = sql.find("*/", start_idx)
        # This whole thing must be a comment because can't even find end of it!
        if end_idx == -1:
          return -1
        else:
          start_idx = end_idx + len("*/")
      elif clean_sql.startswith("--"):
        end_idx = sql.find("\n", start_idx)
        if end_idx == -1:
          return -1
        else:
          start_idx = end_idx + len("\n")

      # Found the keyword.
      elif clean_sql.startswith(keyword):
        return start_idx

      # Could not find the keyword.
      else:
        return -1

    return -1

  sql = raw_sql.strip()
  sql_list = []
  while len(sql) > 0:
    found_sql = False
    for keyword in KEYWORDS:
      start_idx = get_start_idx(sql.lower(), keyword.lower())
      if start_idx != -1:
        keyword_end = KEYWORDS_DICT[keyword] or ";"
        end_idx = find_keyword(sql.lower(), keyword_end.lower(), start_idx)
        end_idx = end_idx + len(keyword_end) if end_idx != -1 else len(sql)
        sql_list.append(sql[0:end_idx])
        sql = sql[end_idx + 1:].lstrip(";").strip()
        found_sql = True
        break

    if not found_sql:
      break

  return sql_list


def parse_func_and_proc(full_sql, is_procedure=False):
  """
  Function: parse_func_and_proc
  -----------------------------
  Parses functions and procedures such that only the CREATE statement is
  extracted (no unnecessary or random SELECT statements, for example).

  full_sql: The statement to parse.
  is_procedure: True if this is for a procedure, False if for a function.
  """
  sql_lines = []
  stack = []

  # Make sure this is actually a CREATE PROCEDURE or CREATE FUNCTION statement.
  check_keyword = "CREATE PROCEDURE" if is_procedure else "CREATE FUNCTION"
  if check_keyword in full_sql.upper() and "BEGIN" in full_sql.upper():
    sql_lines.append(full_sql[
      full_sql.upper().index(check_keyword):
      full_sql.upper().index("BEGIN")])
    sql = full_sql[full_sql.upper().index("BEGIN"):].strip()
  else:
    raise Exception

  # Go through each line.
  for line in sql.split("\n"):
    for (open, close) in CTRL_KEYWORDS:
      # A close "parenthesis".
      if re.search('(\\W|^)%s(\\W|$)' % close, line, re.IGNORECASE):
        to_pop = stack[-1]
        if to_pop != open:
          raise Exception
        stack.pop()
        break

      # An open "parenthesis".
      elif re.search('(\\W|^)%s(\\W|$)' % open, line, re.IGNORECASE):
        stack.append(open)
        break
    sql_lines.append(line + "\n")

    # If there are no more open "parenthesis", then we have reached the end of
    # the procedure or function.
    if not stack:
      break

  # If they are unbalanced at this point, the function or procedure definition
  # was never terminated.
  if stack:
    raise Exception
  return "".join(sql_lines)


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
