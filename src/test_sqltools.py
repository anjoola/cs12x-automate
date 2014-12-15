from cStringIO import StringIO

import sqltools
import unittest

class TestSQLTools(unittest.TestCase):

  def test_is_valid(self):

    self.assertEqual(
      sqltools.is_valid(
      '''
      CREATE FUNCTION avg_submit_interval(input_sub_id INTEGER) RETURNS DOUBLE
BEGIN
    -- Average submit interval (in seconds), initially set to 0.
    DECLARE avg_interval INTEGER DEFAULT 0;
    
    -- Find the latest sub_date and earliest sub_date for a given
    -- submission, and count how many submissions were made.
    -- The sub_dates are stored as Unix timestamps.
    DECLARE earliest_sub_date INTEGER;
    DECLARE latest_sub_date INTEGER;
    DECLARE num_submissions INTEGER;
    
    -- Take the Unix timestamp *after* finding the relevant sub_dates.
    -- This reduces the number of operations needed.
    SELECT UNIX_TIMESTAMP(MIN(sub_date)),
           UNIX_TIMESTAMP(MAX(sub_date)),
           COUNT(*)
    INTO earliest_sub_date, latest_sub_date, num_submissions
    FROM fileset
    WHERE sub_id = input_sub_id;
    

    -- Return NULL when < 2 submissions
    IF num_submissions < 2 THEN
        RETURN NULL;
    END IF;

    -- Otherwise, take the difference between the latest and earliest
    -- sub_dates to get the total time interval in seconds. Then divide
    -- by num_submissions - 1 (number of intervals).
    RETURN (latest_sub_date-earliest_sub_date)/(num_submissions-1);

END !
      '''),
      True
    )

    


  def test_preprocess_sql(self):

    self.assertEqual(
      sqltools.preprocess_sql(StringIO(
      '''
      DELIMITER !
      SELECT * FROM a !
      ''')),
      '''
      
      SELECT * FROM a ;
      '''
    )

    self.assertEqual(
      sqltools.preprocess_sql(StringIO(
      '''
      SELECT ; DELIMITER $
      SELECT $
      ''')),
      '''
      SELECT ; 
      SELECT ;
      '''
    )

    self.assertEqual(
      sqltools.preprocess_sql(StringIO(
      '''
      DELIMITER ! SELECT 5!
      SELECT 10
      ''')),
      '''
       SELECT 5;
      SELECT 10
      '''
    )

    self.assertEqual(
      sqltools.preprocess_sql(StringIO(
      '''
      SELECT 4; DELIMITER $$ SELECT 10 ;
      ''')),
      '''
      SELECT 4;  SELECT 10 ;
      '''
    )

    self.assertEqual(
      sqltools.preprocess_sql(StringIO(
      '''
      SELECT 4; delimiter ! DELIMITER & SELECT 1&
      ''')),
      '''
      SELECT 4;   SELECT 1;
      '''
    )


  def test_remove_comments(self):

    self.assertEqual(
      sqltools.remove_comments(
      '''
      SELECT this -- comment at the end
      '''),
      '''
      SELECT this 
      '''
    )

    self.assertEqual(
      sqltools.remove_comments(
      '''
      SELECT
      -- this is a comment
      '''),
      '''
      SELECT
      
      '''
    )

    self.assertEqual(
      sqltools.remove_comments(
      '''
      SELECT /* comment */ * FROM a
      '''),
      '''
      SELECT  * FROM a
      '''
    )

    self.assertEqual(
      sqltools.remove_comments(
      '''
      SELECT /* lots of stuff
      more stuff
      end */
      * FROM a
      '''),
      '''
      SELECT 

      * FROM a
      '''
    )

    self.assertEqual(
      sqltools.remove_comments(
      '''
      SELECT
      /* lots of stuff */
      * FROM a
      '''),
      '''
      SELECT
      
      * FROM a
      '''
    )

    self.assertEqual(
      sqltools.remove_comments(
      '''
      SELECT
      /* lots of
      stuff */ * FROM a
      '''),
      '''
      SELECT
      
 * FROM a
      '''
    )

    self.assertEqual(
      sqltools.remove_comments(
      '''
      SELECT -- /* nested! */ * FROM a
      '''),
      '''
      SELECT 
      '''
    )

    self.assertEqual(
      sqltools.remove_comments(
      '''
      SELECT 
      -- /* nested!
      * FROM a
      '''),
      '''
      SELECT 
      
      * FROM a
      '''
    )

    self.assertEqual(
      sqltools.remove_comments(
      '''
      SELECT /* -- moar
      nested */
      '''),
      '''
      SELECT 

      '''
    )


if __name__ == '__main__':
  unittest.main()
