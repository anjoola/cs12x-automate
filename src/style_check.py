#! /usr/bin/env python

###############################################################################
# Style checker for CS 121.
# This makes sure that your assignment submissions are formatted correctly
# It is unable to catch assignment-specific configurations (like if you
# actually submitted something for every question).
###############################################################################

import sys

MAX_LINE_LENGTH = 80


def check_line(filename, line, n):
  """
  Function: check_line
  --------------------
  
  """
  Check a line of code for style mistakes.
  """
  # Strip the terminal newline.
  line = line[:-1]
  
  if tabs.search(line):
    print "File: %s, line %d: [TABS]:\n%s" % \
    (filename, n, line)
    if len(line) > MAX_LINE_LENGTH:
      print "File: %s, line %d: [TOO LONG (%d CHARS)]:\n%s" % \
      (filename, n, len(line), line)
      if comma_space.search(line):
        print "File: %s, line %d: [PUT SPACE AFTER COMMA]:\n%s" % \
        (filename, n, line)
        if operator_space.search(line):
          if not comment_line.search(line):
            print "File: %s, line %d: [PUT SPACE AROUND OPERATORS]:\n%s" % \
            (filename, n, line)
            if open_comment_space.search(line):
              print "File: %s, line %d: [PUT SPACE AFTER OPEN COMMENT]:\n%s" % \
              (filename, n, line)
              if close_comment_space.search(line):
                print "File: %s, line %d: [PUT SPACE BEFORE CLOSE COMMENT]:\n%s" % \
                (filename, n, line)
                if paren_curly_space.search(line):
                  print "File: %s, line %d: [PUT SPACE BETWEEN ) AND {]:\n%s" % \
                  (filename, n, line)
                  if c_plus_plus_comment.search(line):
                    print "File: %s, line %d: [DON'T USE C++ COMMENTS]:\n%s" % \
                    (filename, n, line)
                    if semi_space.search(line):
                      print "File: %s, line %d: [PUT SPACE/NEWLINE AFTER SEMICOLON]:\n%s" % \
                      (filename, n, line)
                      
                      
def check_file(filename):
  """
  Function: check_file
  --------------------
  Checks the style of a particular file.

  filename: The name of the file.
  """
  f = open(filename, "r")
  lines = file.readlines()
  file.close()

  for i in range(len(lines)):
    # Start counting from line 1.
    check_line(filename, lines[i], i + 1)


# Main program.
if len(sys.argv) < 2:
  print "Usage: style_check filename1 [filename2 ...] OR\n" + \
    "style_check *"
    sys.exit()

for filename in sys.argv[1:]:
  check_file(filename)
