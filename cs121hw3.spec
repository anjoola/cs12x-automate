{"files": ["queries.sql"],

  "queries.sql": [
    {
      "number": "1a",
      "comments": "true",
      "points": "5",
      "tests": [
        {
          "points": "3",
          "setup": "INSERT INTO a VALUES(5)",
          "query": "SELECT * FROM a",
          "teardown": ""
        },
        {
          "points": "2",
          "setup": "",
          "query": "SELECT * FROM a LIMIT 1",
          "teardown": ""
        }
      ]
    },
    {
      "number": "1b",
      "comments": "false",
      "points": "5",
      "tests": [
        {
          "points": "5",
          "setup": "",
          "query": "SELECT * FROM a",
          "teardown": ""
        }
      ]
    }
  ]
}