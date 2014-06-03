from create import Create
from delete import Delete
from function import Function
from insert import Insert
from manual import Manual
from procedure import Procedure
from select import Select
from trigger import Trigger
from update import Update
from view import View

from types import *

# The types of problems there are and the classes to handle each type.
PROBLEM_TYPES = {
  "create" : Create,
  "delete" : Delete,
  "function": Function,
  "insert" : Insert,
  "manual" : Manual,
  "procedure" : Procedure,
  "select" : Select,
  "trigger" : Trigger,
  "update" : Update,
  "view" : View
}
