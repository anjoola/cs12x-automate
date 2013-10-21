{
  "files": ["queries.sql"],
  "dependencies": ["make-banking.sql", "make-grades.sql"],

  "queries.sql": [
    {
      "number": "1a",
      "comments": "true",
      "points": "4",
      "tests": [
        {
          "points": "4",
          "source": ["hw3/make-banking.sql"],
          "setup": "",
          "query": "SELECT customer_name, COUNT(loan_number) AS num_loans FROM customer NATURAL LEFT JOIN borrower GROUP BY customer_name ORDER BY num_loans DESC",
          "teardown": ""
        }
      ]
    },
    {
      "number": "1b",
      "comments": "true",
      "points": "4",
      "tests": [
        {
          "points": "4",
          "source": ["hw3/make-banking.sql"],
          "setup": "",
          "query": "SELECT branch_name FROM branch NATURAL JOIN (SELECT branch_name, SUM(amount) AS total_loans FROM loan GROUP BY branch_name) AS branch_loans WHERE branch.assets < branch_loans.total_loans",
          "teardown": ""
        }
      ]
    },
    {
      "number": "1c",
      "comments": "false",
      "points": "4",
      "tests": [
        {
          "points": "4",
          "source": ["hw3/make-banking.sql"],
          "setup": "",
          "query": "SELECT branch_name, (SELECT COUNT(*) FROM account AS a WHERE a.branch_name = b.branch_name) AS num_accounts, (SELECT COUNT(*) from loan as l WHERE l.branch_name = b.branch_name) AS num_loans FROM branch AS b",
          "teardown": ""
        }
      ]
    },
    {
      "number": "1d",
      "comments": "false",
      "points": "6",
      "tests": [
        {
          "points": "6",
          "source": ["hw3/make-banking.sql"],
          "setup": "",
          "query": "SELECT branch_name, COUNT(DISTINCT account_number) AS num_accounts, COUNT(DISTINCT loan_number) AS num_loans FROM branch NATURAL LEFT JOIN account NATURAL LEFT JOIN loan GROUP BY branch_name",
          "teardown": ""
        }
      ]
    }
  ]
}