class TimeoutError(Exception):
  """
  Class: TimeoutError
  -------------------
  A timeout error, thrown when a query times out.
  """
  pass


def timeout_handler(signum, frame):
  """
  Function: timeout_handler
  -------------------------
  Handler for when a timeout occurs.

  raises: TimeoutError if a timeout occurs.
  """
  raise TimeoutError
