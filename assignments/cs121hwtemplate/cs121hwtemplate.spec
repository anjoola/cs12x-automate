{
  "assignment": "cs121hwtemplate",
  "files": ["firstfile.sql"],
  "setup": [
    {"type": "dependency", "file": "make-table.sql"}
  ],

  "firstfile.sql": [
    {
      "number": "1",
      "points": 4,
      "comments": true,
      "type": "select",
      "tests": [
        {
          "points": 4,
          "query": "SELECT * FROM t"
        }
      ]
    },
    {
      "number": "2",
      "points": 10,
      "type": "select",
      "tests": [
        {
          "points": 10,
          "query": "SELECT * FROM t WHERE amount >= 1000 ORDER BY amount"
        }
      ]
    }
  ]
}
