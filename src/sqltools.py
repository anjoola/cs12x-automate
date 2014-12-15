"""
Module: sqltools
----------------
Contains tools to help with parsing and checking SQL.
"""

import itertools
import re
from cStringIO import StringIO

# Used to find delimiters in the file.
DELIMITER_RE = re.compile(r"delimiter\s*([^\s]+)", re.I)

# Contains a dictionary with the key as the start keyword and the value as the
# corresponding end keyword.
KEYWORDS_DICT = {
  "ALTER TABLE": ";",
  "CALL": ";",
  "CLOSE": ";",
  "COMMIT": ";",
  "CREATE FUNCTION": ";",
  "CREATE OR REPLACE FUNCTION": ";",
  "CREATE INDEX": ";",
  "CREATE OR REPLACE PROCEDURE": ";",
  "CREATE PROCEDURE": ";",
  "CREATE TABLE" : ";",
  "CREATE OR REPLACE TRIGGER": ";",
  "CREATE TRIGGER": ";",
  "CREATE OR REPLACE VIEW": ";",
  "CREATE VIEW": ";",
  "DECLARE": ";",
  "DELETE": ";",
  "DO": ";",
  "DROP FUNCTION": ";",
  "DROP FUNCTION IF EXISTS": ";",
  "DROP INDEX": ";",
  "DROP PROCEDURE": ";",
  "DROP PROCEDURE IF EXISTS": ";",
  "DROP TABLE": ";",
  "DROP TABLE IF EXISTS": ";",
  "DROP TRIGGER": ";",
  "DROP TRIGGER IF EXISTS": ";",
  "DROP VIEW": ";",
  "DROP VIEW IF EXISTS": ";",
  "FETCH": ";",
  "INSERT" : ";",
  "LOAD DATA": ";",
  "OPEN": ";",
  "RELEASE SAVEPOINT": ";",
  "REPLACE": ";",
  "RETURN": ";",
  "ROLLBACK": ";",
  "SAVEPOINT": ";",
  "SELECT": ";",
  "( SELECT": ")",
  "SET": ";",
  "START TRANSACTION": ";",
  "UPDATE": ";",

  # Special cases. Many statements can be enclosed by these.
  "BEGIN": "END",
  "CASE": "END CASE",
  "IF": "END IF",
  "IF (": ")",
  "LOOP": "END LOOP",
  "WHILE": "END WHILE",
  "REPEAT": "END REPEAT",
  "(": ")"
}
KEYWORDS_START = KEYWORDS_DICT.keys()
KEYWORDS_END = KEYWORDS_DICT.values()

# Special cases end keywords.
SPECIAL = [
  "END", "END CASE", "END IF", ")", "END LOOP", "END WHILE", "END REPEAT"
]

# Keywords to ignore.
KEYWORDS_IGNORE = [
  "AFTER INSERT ON",
  "AFTER DELETE ON",
  "AFTER UPDATE ON",
  "BEFORE INSERT ON",
  "BEFORE DELETE ON",
  "BEFORE UPDATE ON",
  "ON DUPLICATE KEY UPDATE"
]
# TODO comment
KEYWORDS_IGNORE_PREV = {
  "SELECT": ["DECLARE", "IF", "INSERT", "CREATE VIEW", "CREATE OR REPLACE VIEW"],
  "SET": ["UPDATE"]
}

ALL_KEYWORDS = KEYWORDS_START + KEYWORDS_END + KEYWORDS_IGNORE

def is_valid(sql):
  """
  Function: is_valid
  ------------------
  Returns whether or not a SQL statement is valid. TODO also have it split SQL?
  """
  # Stores start keywords. Pops from this when a corresponding end keyword is
  # found.
  stack = []
  # State variables.
  prev = ""
  curr = ""
  # True if the previously added keyword was a special case.
  was_special_case = False # TODO name better
  # List of keywords to find matches from. This should get smaller as the
  # possible keyword gets longer.
  keyword_matches = ALL_KEYWORDS

  # Split the SQL statement into word tokens. Cleans up the SQL by:
  #   - Removing comments
  #   - Replacing newlines with spaces
  #   - Removing extra spaces TODO
  #   - Treating semicolons as keywords
  #   - Change to uppercase
  # TODO remove stuff within strings
  words_iter = iter([x for x in remove_comments(sql).upper().replace("\n", " ").replace(";", " ; ").replace(")", " ) ").replace("(", " ( ").split(" ") if len(x) > 0])

  def add_keyword(keyword):
    """
    Function: add_keyword
    ---------------------
    If the keyword is a starting keyword, adds it to the stack. If it is an
    ending keyword, pops the corresponding starting keyword from the stack. If
    the stack is unbalanced, returns False, otherwise returns True.
    """
    # Keyword to ignore. TODO add about KEYWORDS_IGNORE_PREV
    if keyword in KEYWORDS_IGNORE or \
       keyword in KEYWORDS_IGNORE_PREV and \
       len(stack) > 0 and stack[-1] in KEYWORDS_IGNORE_PREV[keyword]:
      return True

    # Start keyword. Add to the stack.
    if keyword in KEYWORDS_START:
      stack.append(keyword)

    # End keyword. Makes sure this matches with a start keyword.
    else:
      try:
        start = stack[-1]
        # Unbalanced, so invalid SQL! Ignore if the previous keyword was a
        # special case and this is a semicolon (in that case, this extra semi-
        # colon was part of a previous end keyword).
        if KEYWORDS_DICT[start] != keyword and \
           (not was_special_case and keyword == ";"):
          return False
        elif KEYWORDS_DICT[start] == keyword:
          stack.pop()

      # An extra end keyword not balanced by a start keyword. Ignore if the
      # previous keyword was a special case.
      except IndexError:
        if not was_special_case and keyword == ";":
          return False

    # Otherwise, successfully modified the stack.
    return True


  # Go through all of the individual word tokens in the SQL statement.
  while True:
    # TODO print stack
    try:
      prev = curr
      next_word = words_iter.next()
      curr = (curr + " " + next_word).strip()

      # Get the keywords that match the current token.
      new_keyword_matches = \
        list(set([k for k in keyword_matches if k.startswith(curr)]))
      # If the current token does not match, maybe the previous one does. This
      # can happen when the current token is a strict substring of possible
      # keywords.
      if len(new_keyword_matches) == 0:
        if prev in keyword_matches:
          if not add_keyword(prev):
            return False

          # Set the special case variable.
          if prev in SPECIAL:
            was_special_case = True
          else:
            was_special_case = False

        # Now only check the next word by itself.
        curr = next_word
        keyword_matches = ALL_KEYWORDS
        new_keyword_matches = [k for k in keyword_matches if k.startswith(curr)]

      # No matches, so look at the next word.
      if len(new_keyword_matches) == 0:
        keyword_matches = ALL_KEYWORDS
        curr = ""

      # Single keyword match.
      elif (len(new_keyword_matches) == 1 and new_keyword_matches[0] == curr) \
           or curr == ";":
        add_word = curr if curr == ";" else new_keyword_matches[0]
        if not add_keyword(add_word):
          return False

        # Set the special case variable.
        if add_word in SPECIAL:
          was_special_case = True
        else:
          was_special_case = False

        # Reset current list of keywords.
        keyword_matches = ALL_KEYWORDS
        curr = ""

      # Otherwise, there are multiple keyword matches. Need to keep going with
      # more words..
      else:
        keyword_matches = new_keyword_matches

    # No more words to consume.
    except StopIteration:
      break

  return len(stack) == 0


def preprocess_sql(sql_file):
  """
  Function: preprocess_sql
  ------------------------
  Preprocess the SQL in order to handle the DELIMITER statements.

  sql_file: The SQL file to preprocess.
  returns: The newly-processed SQL string.
  """
  lines = StringIO()
  delimiter = ';'
  for line in sql_file:
    # See if there is a new delimiter defined. Possible that they have multiple
    # DELIMITER statements or DELIMITEr statmeents nested within SQL statements.
    match = re.search(DELIMITER_RE, line)
    while match:
      delimiter = match.group(1)
      line = line[0:line.index(match.group(0))] + \
             line[line.index(match.group(0)) + len(match.group(0)):]
      match = re.search(DELIMITER_RE, line)

    # If we've reached the end of a statement.
    if line.strip().endswith(delimiter):
      line = line.replace(delimiter, ";")
    lines.write(line)

  return lines.getvalue()


def remove_comments(in_sql):
  """
  Function: remove_comments
  -------------------------
  Removes comments from SQL.
  """
  sql = []
  in_block_comment = False

  for line in in_sql.split("\n"):
    while "/*" in line and not in_block_comment:
      if "/*" in line and "*/" in line:
        line = line[0:line.index("/*")] + line[line.index("*/") + 2:]
      elif "/*" in line:
        # Ignore nested comments.
        if line.find("--") != -1 and line.find("--") < line.find("/*"):
          break
        line = line[0:line.index("/*")]
        sql.append(line)
        in_block_comment = True

    if in_block_comment and "*/" in line:
      line = line[line.index("*/") + 2:]
      in_block_comment = False
    if "--" in line:
      line = line[0:line.index("--")]

    elif in_block_comment:
      continue

    sql.append(line)

  return "\n".join(sql)


































# TODO REMOVE
# Control keywords. Used to figure out where a function begins and ends.
CTRL_KEYWORDS = [
  ("CASE", "END CASE"),
  ("IF", "END IF"),
  ("IF(", ")"),
  ("LOOP", "END LOOP"),
  ("WHILE", "END WHILE"),
  ("REPEAT", "END REPEAT"),
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

  This does not work for multi-statement SQL queries, such as CREATE PROCEDURE.

  Obviously this is not perfect and plenty of statements can get through.
  However, it should be sufficient unless there are some very evil students.

  query: The query to check.
  query_type: The query type (e.g. INSERT, DELETE, SELECT).
  returns: True if the query is valid, False otherwise.
  """
  return query_type.upper() in query.upper() and query.count(";") <= 1
  # TODO: This is turned off because students like to put code before their
  #       answer, causing this function to return false negatives. Really,
  #       this function needs to be improved.
  '''
  return (
    # Make sure the query type can be found in the query.
    query.lower().strip().find(query_type.lower()) == 0 and
    # Make sure there is only one SQL statement.
    query.strip().strip().rstrip(";").find(";") == -1
  )
  '''


def find_valid_sql(query, query_type, ignore_irrelevant=False):
  """
  Function: find_valid_sql
  ------------------------
  Finds the valid SQL statement of query_type within a large SQL statement. If
  it cannot be found, return None.

  query: The query to search within.
  query_type: The query type (e.g. INSERT, DELETE, SELECT).
  ignore_irrelevant: True if should ignore non-relevant SQL, False otherwise.
  returns: The query if valid SQL can be found, False otherwise.
  """
  if query.lower().strip().find((query_type + " ").lower()) != -1:
    semicolon_pos = \
      query.strip().find(";", query.lower().find((query_type + " ").lower()))

    # Remove irrelevant SQL if specified.
    #if ignore_irrelevant:
    #  query = query[query.upper().find(query_type.upper() + " "):]
    #  semicolon_pos = \
    #    query.strip().find(";", query.lower().find((query_type + " ").lower()))
    if semicolon_pos == -1:
      return query.strip()
    return query.strip()[0:semicolon_pos]
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
        result = re.sub(r'\s+', ' ', sql[i:]).strip()
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
    Returns the starting index of the keyword if found.

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
    for keyword in KEYWORDS_START:
      start_idx = get_start_idx(sql.lower(), keyword.lower())
      if start_idx != -1:
        keyword_end = KEYWORDS_DICT[keyword] or ";"
        end_idx = find_keyword(sql.lower(), keyword_end.lower(), start_idx)
        end_idx = end_idx + len(keyword_end) if end_idx != -1 else len(sql)
        sql_list.append(sql[0:end_idx])
        sql = sql[end_idx + 1:].strip()

        # Remove start and end semicolons.
        while sql.startswith(";") or sql.endswith(";"):
          sql = sql.strip(";").strip()
        found_sql = True
        break

    if not found_sql:
      break

  return sql_list


def parse_create(sql):
  """
  Function: parse_create
  ----------------------
  Parses a CREATE TABLE statement and only runs those (instead of random INSERT
  statements that students should not be including).

  full_sql: The statement to parse.
  returns: Only the CREATE TABLE statement(s).
  """
  sql_lines = []
  started_table = False
  for line in remove_comments(sql).split("\n"):
    if "CREATE TABLE" in line.upper():
      line = line[line.upper().index("CREATE TABLE"):]
      started_table = True
    end_create = re.search(r"\)\s*;", line)
    if end_create and started_table:
      line = line[:line.find(end_create.group()) + len(end_create.group())]
      sql_lines.append(line)
      started_table = False
    if started_table:
      sql_lines.append(line)
    else:
      continue
  return "\n".join(sql_lines)


def parse_func_and_proc(full_sql, is_procedure=False):
  """
  Function: parse_func_and_proc
  -----------------------------
  Parses functions and procedures such that only the CREATE statement is
  extracted (no unnecessary or random SELECT statements, for example).

  full_sql: The statement to parse.
  is_procedure: True if this is for a procedure, False if for a function.
  returns: Only the function or procedure statement.
  """
  sql_lines = []
  stack = []

  # Make sure this is actually a CREATE PROCEDURE or CREATE FUNCTION statement
  # by seeing if the SQL starts with the proper CREATE statement.
  check_keyword = "CREATE PROCEDURE" if is_procedure else "CREATE FUNCTION"
  check_or_keyword = "CREATE OR REPLACE PROCEDURE" \
                     if is_procedure else "CREATE OR REPLACE FUNCTION"
  if check_keyword in full_sql.upper() and "BEGIN" in full_sql.upper():
    sql_lines.append(full_sql[
      full_sql.upper().index(check_keyword):
      full_sql.upper().index("BEGIN")])
    sql = full_sql[full_sql.upper().index("BEGIN"):].strip()
  elif check_or_keyword in full_sql.upper() and "BEGIN" in full_sql.upper():
    sql_lines.append(full_sql[
      full_sql.upper().index(check_or_keyword):
      full_sql.upper().index("BEGIN")])
  else:
    raise Exception

  # Go through each line.
  for line in remove_comments(sql).split("\n"):
    # TODO go through firs tword, then first and second word, etc.
    # once you find a keyword, look start from there and look at the first word, etc.
    # TODO problem if open and close at the same line
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
