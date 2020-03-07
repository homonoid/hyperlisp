# NOTE: this shall be rewritten!

import sys

from .reader import HlReader
from .error import HlError
from .exec import HlInterpreter
from .fmt import fmt


def treeify(tree, prefix = '  '):
  if type(value := tree.value) is tuple:
    value = \
      '\n' + '\n'.join([treeify(node, prefix + '  ') for node in value])
  return f'{prefix}{tree.type} {value}'


from operator import add, sub, mul, truediv as div, eq
from fractions import Fraction


exe = HlInterpreter()


exe.function('__python_print', print)
exe.function('__python_input', input)
exe.function('__python_add', add)
exe.function('__python_sub', sub)
exe.function('__python_mul', mul)
exe.function('__python_div', div)
exe.function('__python_equ', eq)
exe.function('__s_to_fraction', lambda s: Fraction(s).limit_denominator())


if len(args := sys.argv[1:]) == 1:
  with open(args[0]) as file:
    source = file.read()
    try:
      reader = HlReader(args[0], source)
      exe.update(reader)
      exe.execute()
    except HlError as error:
      print('=== Sorry! ===\n', repr(error))
elif len(args) == 0:
  import readline
  while True:
    line = input('~| ')
    try:
      reader = HlReader('<stdin>', line)
      exe.update(reader)
      res = exe.execute()
      res is not None and print(fmt(res))
    except HlError as error:
      print('=== Sorry! ===\n', repr(error))
else:
  print('hyperlisp interpreter.\nusage: hyperlisp [file.hl]')
