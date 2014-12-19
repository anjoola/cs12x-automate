"""
Module: sqltools
----------------
Contains tools to help with parsing and checking SQL.
"""

import itertools
import re
from cStringIO import StringIO

from errors import ParseError

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
  "CREATE TEMPORARY TABLE": ";",
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
  "IFNULL (": ")",
  "LOOP": "END LOOP",
  "WHILE": "END WHILE",
  "REPEAT": "END REPEAT",
  "(": ")"
}
KEYWORDS_START = KEYWORDS_DICT.keys()
KEYWORDS_END = KEYWORDS_DICT.values()

# Special cases for end keywords.
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
  "FOR EACH ROW CALL",
  "ON DELETE",
  "ON DELETE SET",
  "ON DUPLICATE KEY UPDATE",
  "ON UPDATE",
  "ON UPDATE SET"
]

# TODO comment
# keyword: [before]
KEYWORDS_IGNORE_PREV = {
  "DO": ["WHILE"],
  "SELECT": [
    "CREATE TABLE",
    "CREATE TEMPORARY TABLE",
    "DECLARE",
    "IF",
    "INSERT",
    "CREATE VIEW",
    "CREATE OR REPLACE VIEW"
  ],
  "SET": ["UPDATE"]
}

ALL_KEYWORDS = KEYWORDS_START + KEYWORDS_END + KEYWORDS_IGNORE

# Possible things to drop.
DROP_KEYWORDS = ["FUNCTION", "PROCEDURE", "TABLE", "TRIGGER", "VIEW"]

def fix_sql(in_sql):
  """
  Function: fix_sql
  -----------------
  Applies various fixes to a SQL statement, including:
    - Fix DROP statements so they all have IF EXISTS.
    - Remove SET statements (they are disallowed).
  """

  def fix_drop_statement(sql):
    """
    Function: fix_drop_statement
    ----------------------------
    Fixes DROP * statements, since they won't work in the autograder. Replaces
    them by DROP * IF EXISTS statements.
    """
    for drop in DROP_KEYWORDS:
      # Fix if they did not use IF EXISTS.
      if "DROP " + drop in sql and "DROP " + drop + " IF EXISTS" not in sql:
        sql = sql.replace("DROP " + drop, "DROP " + drop + " IF EXISTS")
      elif "drop " + drop.lower() in sql and \
           "drop " + drop.lower() + " if exists" not in sql:
        sql = sql.replace("drop " + drop.lower(),
                          "drop " + drop.lower() + " if exists")
    return sql


  def remove_set_statement(sql):
    """
    Function: remove_set_statement
    ------------------------------
    Removes any SET statements.
    """
    if sql.strip().upper().startswith("SET"):
      return ""
    return sql


  return fix_drop_statement(remove_set_statement(in_sql))

# TODO
import sqlparse
def parse_sql(in_sql):
  return filter(lambda sql: len(sql) > 0,
                [fix_sql(sql) for sql in sqlparse.split(in_sql)])

def parse_sql2(in_sql):
  """
  Function: parse_sql
  -------------------
  Parses given SQL into separate SQL statements. If the SQL is invalid, then
  throws a ParseError.
  """
  # The parsed list of SQL statements and current SQL that is being constructed.
  sql_list = []
  sql = ""

  # Stores start keywords. Pops from this when a corresponding end keyword is
  # found.
  stack = []
  # Stores whether or not the stack was just popped from.
  just_popped = [False]
  # True if the previously added keyword was a special case for end keywords.
  was_special_case = False

  # State variables.
  prev = ""
  curr = ""
  # List of keywords to find matches from. This should get smaller as the
  # possible keyword gets longer.
  keyword_matches = ALL_KEYWORDS

  # Split the SQL statement into word tokens. Cleans up the SQL by:
  #   - Removing comments
  #   - Replacing newlines with spaces
  #   - Treating semicolons as keywords
  # TODO ignore stuff within strings
  #   - Removing extra spaces TODO
  words_iter = iter([x for x in
    remove_comments(in_sql).replace("\n", " ")
                           .replace(";", " ; ")
                           .replace(")", " ) ")
                           .replace("(", " ( ")
                           .split(" ")
    if len(x) > 0])

  def add_keyword(keyword, sql, sql_list):
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
          raise ParseError
        elif KEYWORDS_DICT[start] == keyword:
          just_popped[0] = True
          stack.pop()

      # An extra end keyword not balanced by a start keyword. Ignore if the
      # previous keyword was a special case.
      except IndexError:
        if not was_special_case and keyword == ";":
          raise ParseError

    # Otherwise, successfully modified the stack.
    return True


  # Go through all of the individual word tokens in the SQL statement.
  while True:
    try:
      prev = curr
      next_word = words_iter.next()
      curr = (curr + " " + next_word).strip().upper()
      # Add to the current SQL statement.
      sql += next_word + " "

      # Get the keywords that match the current token.
      new_keyword_matches = \
        list(set([k for k in keyword_matches if k.startswith(curr)]))
      # If the current token does not match, maybe the previous one does. This
      # can happen when the current token is a strict substring of possible
      # keywords.
      if len(new_keyword_matches) == 0:
        if prev in keyword_matches:
          add_keyword(prev, sql, sql_list)

          # Set the special case variable.
          if prev in SPECIAL:
            was_special_case = True
          else:
            was_special_case = False

        # Now only check the next word by itself.
        curr = next_word.upper()
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
        add_keyword(add_word, sql, sql_list)

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

      # If adding this causes the stack to become empty, then we found a
      # complete SQL statement.
      if len(stack) == 0 and just_popped[0]:
        just_popped[0] = False
        # Fix the SQL statement if necessary.
        sql_list.append(fix_sql(sql))
        sql = ""

    # No more words to consume.
    except StopIteration:
      break

  # Add remaining SQL as final SQL statement.
  if len(sql) > 0 and len(stack) <= 1:
    sql_list.append(sql)
  elif len(stack) > 1:
    raise ParseError

  return sql_list


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
    # DELIMITER statements or DELIMITER statmeents nested within SQL statements.
    # Ignore any mention of a delimiter in comments.
    match = re.search(DELIMITER_RE, remove_comments(line))
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
