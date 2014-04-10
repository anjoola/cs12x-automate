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


  def get(self, function, *args, **kwargs):
    """
    Function: get
    -------------
    Get the results of a query, if it exists. If not, runs the query then
    gets the results. Returns a deep copy of the results since they might be
    modified.
    """
    key = (tuple(args), frozenset(kwargs.iteritems()))
    if key in self.cache:
      return deepcopy(self.cache[key])

    # If it doesn't exist in the cache, run the query, then store it.
    else:
      result = function(*args, **kwargs)
      self.cache[key] = result
      return deepcopy(result)


  def clear(self):
    """
    Function: clear
    ---------------
    Clears all entries in the cache.
    """
    self.cache.clear()
