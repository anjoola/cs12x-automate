class Cache:
  """
  Class: Cache
  ------------
  A cache to store query results.
  """
  def __init__(self):
    # The cache. The key is the function arguments and the value is a Result
    # object containing the function details.
    self.cache = {}


  def get(self, function, *args, **kwargs):
    """
    Function: get
    -------------
    Get the results of a query, if it exists. If not, runs the query then
    gets the results.
    """
    key = (tuple(args), frozenset(kwargs.iteritems()))
    if key in self.cache:
      return self.cache[key]

    # If it doesn't exist in the cache, run the query, then store it.
    else:
      result = function(*args, **kwargs)
      self.cache[key] = result
      return result


  def clear(self):
    """
    Function: clear
    ---------------
    Clears all entries in the cache.
    """
    self.cache.clear()
