from copy import deepcopy

class Cache:
  """
  Class: Cache
  ------------
  A cache to store query results. Is used so that there are fewer requests to
  the database if students have the same exact query.
  """
  # The cache. The key is the SQL query and the value is the results of running
  # that query.
  cache = {}

  @classmethod
  def clear(cls):
    """
    Function: clear
    ---------------
    Clears all entries in the cache.
    """
    cls.cache.clear()


  @staticmethod
  def create_key(string):
    """
    Function: create_key
    --------------------
    Creates a key from a string by removing spaces between characters if not
    enclosed by single quotes. For example, this ensures that the following
    two queries result in the same key:
      SELECT MAX( DISTINCT count)   FROM bank;
      SELECT MAX (DISTINCT   count) FROM bank

    string: The string to create a key from.
    returns: The resulting key.
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


  @classmethod
  def delete(cls, key):
    """
    Function: delete
    ----------------
    Deletes a specific entry in the cache.

    key: The key for the entry to delete.
    """
    key = Cache.create_key(key)
    if key in cls.cache:
      del cls.cache[key]


  @classmethod
  def get(cls, key):
    """
    Function: get
    -------------
    Get an element in the cache. Returns a deep copy of the results since they
    might be modified.

    key: The key for the entry to get.
    returns: The entry in the cache, None if they key does not exist.
    """
    key = Cache.create_key(key)
    return deepcopy(cls.cache[key]) if key in cls.cache else None


  @classmethod
  def put(cls, key, value):
    """
    Function: put
    -------------
    Puts an entry into the cache.

    key: The key for the entry.
    value: The value to store in the cache.
    """
    cls.cache[Cache.create_key(key)] = deepcopy(value)
