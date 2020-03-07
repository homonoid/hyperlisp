from fractions import Fraction
from .func import Func, External


def fmt(value):
  """Make a Python `value` look like it's Hyperlisp"""
  if type(value) is list:
    return '[%s]' % ' '.join(fmt(elem) for elem in value)
  elif type(value) is Fraction:
    whole = value.numerator / value.denominator
    return str(int(whole) if whole.is_integer() else whole)
  elif type(value) is str:
    return '"%s"' % value
  elif type(value) is bool:
    return (value and 1) or 0
  elif type(value) in (Func, External):
    return str(value)
