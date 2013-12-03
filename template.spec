{
  "files": ["file.sql"],            # [string] -> Files to grade
  "dependencies": [],               # [string] -> Source files needed for grading
  "import": [],                     # [string] -> A list of raw files to import.
  "setup": [],                      # [string] -> List of queries to run prior to grading.
  "teardown": [],                   # [string] -> List of queries to run after grading.

  "file.sql": [
    {
      "number": "",                 # string -> Problem number
      "comments": false,            # bool -> true if need to check for comments
      "points": 0,                  # int -> Number of points
      "show-results": false,        # bool -> true if they have to attach their results
      "dependencies": [],           # [string] -> A list of problem numbers this is dependent on.
                                    #             Runs the student's responses to those problems first.
      "setup": [],                  # [string] -> List of queries to run prior to grading this problem.
      "teardown": [],               # [string] -> List of queries to run after grading this problem.
      "keywords": [],               # [string] -> List of keywords to check for
      "tests": [                    # List of tests to run on this problem
        {
          "points": 0,              # int -> Number of points to subtract if this test fails
          "type": "",               # string -> Type of test (select, create, etc.)
          "desc": "",               # string -> Description of the test
          "timeout": 0,             # int -> The timeout in seconds for the test/student's query.
        },

        ###
        # SELECT-specific parameters
        #   Compares results of the test SELECT statement to the student's SELECT statement.
        ###
        {
          "setup": "",              # string -> A setup query before running the actual query
          "query": "",              # string -> Query to run and compare results with
          "teardown": "",           # string -> Query to run after the test
          "ordered": false,         # bool -> true if also need to check the order of the results
          "column-order": false     # bool -> true if the columns must be in a specific order
          "rename": false           # bool -> true if should check if derived relations (like subqueries, aggregates) are renamed
        },

        ###
        # CREATE TABLE-specific parameters
        #   TODO
        ###
        {
        
        },

        ###
        # STORED PROCEDURE-specific parameters
        #   TODO
        ###
        {
          "table": "",              # string -> The table the stored procedure is being run on.
          "query": "",              # string -> Query to run and compare the before and after results with.
          "run-query": false,       # bool -> Whether or not to run the student's response for this question
          "teardown": ""            # string -> Query to run after the test
        },

        ###
        # FUNCTION-specific parameters
        #   TODO
        ###
        {
          "query": "",              # string -> Query to run to compare the results.
          "expected": ""            # string -> The expected result of the query.
        }
      ]
    },
  ]
}