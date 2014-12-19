from cStringIO import StringIO

import sqltools
import unittest

class TestSQLTools(unittest.TestCase):

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
