import argparse
import json
import os, sys


def grade(specs, f):
  print "hi!"

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
                         