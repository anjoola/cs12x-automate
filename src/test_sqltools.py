import sqltools
import unittest

class TestSQLTools(unittest.TestCase):

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
