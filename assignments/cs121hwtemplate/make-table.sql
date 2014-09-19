DROP TABLE IF EXISTS t;
CREATE TABLE t (
  username    VARCHAR(20) PRIMARY KEY,
  amount      NUMERIC(10, 2) NOT NULL
);

INSERT INTO t VALUES
  ('Angela', 100000),
  ('Bob', 42938.32),
  ('Charles', 329348),
  ('David', 2.12),
  ('Ellen', 3192.32),
  ('Fred', 1000),
  ('George', 10382.21),
  ('Harry', 1023),
  ('Ian', 23),
  ('Jack', 3482223.3);
