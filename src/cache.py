from copy import deepcopy

class Cache:
  """
  Class: Cache
  ------------
  A cache to store query results. Is used so that there are fewer requests to
  the database if students have the same exact query.
  """
  def __init__(self):
    # The cache. The key is the function arguments and the value contains the
    # function call details.
    self.cache = {}


  def clear(self):
    """
    Function: clear
    ---------------
    Clears all entries in the cache.
    """
    self.cache.clear()


  def create_key(self, string):
    """
    Function: create_key
    --------------------
    Creates a key from a string by removing spaces between characters if not
    enclosed by single quotes. For example, this ensures that the following
    two queries result in the same key:
      SELECT MAX( DISTINCT count)   FROM bank;
      SELECT MAX (DISTINCT   count) FROM bank
    """
    key = ""
    prev_char = ""
    started_quotes = False
    for char in string:
      if char == "'" and prev_char != "\\":
        started_quotes = not started_quotes
      key += char if char != " " or started_quotes else ""
      prev_char = char

    return key


  def delete(self, key):
    """
    Function: delete
    ----------------
    Deletes a specific entry in the cache.

    key: The key for the entry to delete.
    """
    key = self.create_key(key)
    if key in self.cache:
      del self.cache[key]


  def get(self, key):
    """
    Function: get
    -------------
    Get an element in the cache. Returns a deep copy of the results since they
    might be modified.

    key: The key for the entry to get.
    returns: The entry in the cache, None if they key does not exist.
    """
    key = self.create_key(key)
    return deepcopy(self.cache[key]) if key in self.cache else None


  def put(self, key, value):
    """
    Function: put
    -------------
    Puts an entry into the cache.

    key: The key for the entry.
    value: The value to store in the cache.
    """
    self.cache[self.create_key(key)] = value
