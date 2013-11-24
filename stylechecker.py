from CONFIG import STYLE_DEDUCTIONS

class StyleError(Exception):
  """
  Class: StyleError
  -----------------
  TODO
  """
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)


def check(f, specs):
  """
  Function: check
  ---------------
  TODO

  raises: StyleError if the file is not in the right format and cannot be
          parsed.
  returns: A list of style violations (possible violations are the keys of the
           STYLE_DEDUCTIONS dictionary.
  """
  
  # raise StyleError
  # TODO implement
  return []


def deduct(student):
  """
  Function: deduct
  ----------------
  Deduct from the student's total score for style violations.

  student: The graded student.
  returns: The new graded student with the point deductions.
  """
  for deduction in student["style-deductions"]:
    (points, _) = STYLE_DEDUCTIONS[deduction]
    student["got_points"] = got_points - points

  return student
