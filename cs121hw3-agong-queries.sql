-- [Problem 1a]
-- asdf
SELECT customer_name, COUNT(loan_number) AS num_loans FROM customer
NATURAL LEFT JOIN borrower GROUP BY customer_name ORDER BY num_loans DESC;

-- [Problem 1b]
-- asdf
SELECT branch_name FROM branch NATURAL JOIN (SELECT branch_name, SUM(amount)
AS total_loans FROM loan GROUP BY branch_name) AS branch_loans
WHERE branch.assets < branch_loans.total_loans;

-- [Problem 1c]
SELECT branch_name, (SELECT COUNT(*) FROM account AS a 
WHERE a.branch_name = b.branch_name) AS num_accounts,
(SELECT COUNT(*) from loan as l WHERE l.branch_name = b.branch_name) AS
num_loans FROM branch AS b;

-- [Problem 1d]
SELECT branch_name, COUNT(DISTINCT account_number) AS num_accounts,
COUNT(DISTINCT loan_number) AS num_loans FROM branch NATURAL LEFT JOIN account
NATURAL LEFT JOIN loan GROUP BY branch_name;