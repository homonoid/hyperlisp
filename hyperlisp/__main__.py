# NOTE: this shall be rewritten!

import sys

from .reader import HlReader
from .error import HlError
from .exec import HlInterpreter


def treeify(tree, prefix = '  '):
  if type(value := tree.value) is tuple:
    value = \
      '\n' + '\n'.join([treeify(node, prefix + '  ') for node in value])
  return f'{prefix}{tree.type} {value}'


from operator import add, sub, mul, truediv as div, eq
from fractions import Fraction

exe = HlInterpreter()

original_input = input


exe.funcpy('__python_print', print)
exe.funcpy('__python_input', original_input)
exe.funcpy('__python_add', add)
exe.funcpy('__python_sub', sub)
exe.funcpy('__python_mul', mul)
exe.funcpy('__python_div', div)
exe.funcpy('__python_equ', eq)
exe.funcpy('__s_to_fraction', lambda s: Fraction(s).limit_denominator())


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
  import readline # it's here so __python_input is not `readline`d
  while True:
    line = input('>> ')
    try:
      reader = HlReader('<stdin>', line)
      exe.update(reader)
      res = exe.execute()
      res and print(res)
    except HlError as error:
      print('=== Sorry! ===\n', repr(error))
else:
  print('hyperlisp interpreter.\nusage: hyperlisp [file.hl]')
