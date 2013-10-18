import argparse
import json
import mysql.connector
import os, sys

# Database to connect to for data.
DB = mysql.connector.connect(user="angela", password="cs121",
  host="sloppy.cs.caltech.edu", database="angela_db", port="4306")

def grade(specs, filename):
  """
  grade
  -----
  Grades a file according to the specs. Will search the specs may contain details about multiple
  files, so gets the specs for the corresponding file.

  specs: The specs (an object).
  filename: The file name of the file to grade.
  """
  f = open(filename, "r")
  try:
    responses = parse_file(f)
  except Exception:
    print "SAD"
  finally:
    f.close()
  
  cursor = DB.cursor()
  query = ("SELECT * FROM a")
  cursor.execute(query)
  for a in cursor:
    print a
  cursor.close()
  

def parse_file(f):
  """
  parse_file
  ----------
  Parses the file into a dictionary of questions and the student's responses.

  f: The file object to parse.
  return: A dictionary containing a mapping of the question number and the student's response.
  """
  pass
  
  

if __name__ == "__main__":
  # Parse command-line arguments.
  parser = argparse.ArgumentParser(description="Get the arguments.")
  parser.add_argument("--specs")
  parser.add_argument("--files", nargs="+")
  args = parser.parse_args()
  (specs, files) = (args.specs, args.files)

  # If no arguments specified.
  if specs is None or files is None:
    print "Usage: main.py --specs [spec file] --files [files to check]"
    sys.exit()

  print "\n\n===========================START GRADING===========================\n\n"
    
  # TODO: Handle homeworks with multiple file submissions

  # IF * is specified as files, then find all files.
  if files[0] == "*":
    # TODO: deal with directories
    # TODO: need to untar stuff
    files = [f for f in os.listdir(".")] # TODO f.startswith(... etc)
  # The specs is a JSON string. Convert it into a JSON object.
  spec_file = open(specs, "r")
  specs = json.loads("".join(spec_file.readlines()))
  spec_file.close()

  # Grade each file.
  for f in files:
    grade(specs, f)

  # Close connection with the database.
  DB.close()
  print "\n\n===========================END GRADING===========================\n\n"
