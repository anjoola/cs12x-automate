import mysql.connector

from CONFIG import (
  HOST,
  LOGIN,
  MAX_TIMEOUT,
  PORT
)

class Terminator:
  """
  Class: Terminator
  -----------------
  Terminates unruly queries by killing the corresponding connection.
  """
  # The database connection.
  db = None

  # The database cursor.
  cursor = None

  def __init__(self, user, database):
    self.db = mysql.connector.connect(user=user,
                                      password=LOGIN[user],
                                      host=HOST,
                                      database=database,
                                      port=PORT,
                                      connection_timeout=MAX_TIMEOUT)
    self.cursor = self.db.cursor(buffered=True)


  def terminate(self, thread_id):
    """
    Function: terminate
    -------------------
    Terminates a connection.

    thread_id: ID of the connection.
    """
    self.cursor.execute("KILL %d" % thread_id)
