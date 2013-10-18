{"files": ["queries.sql"],

  "queries.sql": [
    {
      "1a": {
        "comments": "true",
        "points": "5",
        "tests": [
          {
            "points": "1",
            "setup": "INSERT INTO a VALUES(5)",
            "query": "SELECT * FROM a"
          },
          {
            "points": "2",
            "setup": "",
            "query": "SELECT * FROM a LIMIT 1"
          }
        ]
      }
    },
    {
      "1b": {
        "comments": "false",
        "points": "5",
        "tests": [
          {
            "points": "5",
            "setup": "",
            "query": "SELECT * FROM a"
          }
        ]
      }
    }
  ]
}