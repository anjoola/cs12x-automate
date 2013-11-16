{
  "files": ["file.sql"],          # [string] -> Files to grade
  "dependencies": [],             # [string] -> Source files needed for grading

  "file.sql": [
    {
      "number": "",               # string -> Problem number
      "comments": false,          # bool -> true if need to check for comments
      "points": 0,                # int -> Number of points
      "show-results": false,      # bool -> true if they have to attach their results
      "keywords": [],             # [string] -> List of keywords to check for
      "tests": [                  # List of tests to run on this problem
        {
          "points": 0,            # int -> Number of points to subtract if this test fails
          "type": "",             # string -> Type of test (select, create, etc.)
        },

        ###
        # SELECT-specific parameters
        #   Compares results of the test SELECT statement to the student's SELECT statement.
        ###
        {
          "source": [],           # [string] -> A list of files to source before running the query
          "setup": "",            # string -> A setup query before running the actual query
          "query": "",            # string -> Query to run and compare results with
          "teardown": "",         # string -> Query to run after the test to tear down
          "ordered": false,       # bool -> true if also need to check the order of the results
          "column-order": false   # bool -> true if the columns must be in a specific order
          "rename": false         # bool -> true if should check if derived relations (like subqueries, aggregates) are renamed
        },

        # 
        
        
      ]
    },
  ]
}



if not order by, take off ?
if not the right column order, take off ?
forget to limit? take off ?

if don't show results, take off ?

test should output if failed one of these (order, etc.)
missing distcint, etc. keyword?