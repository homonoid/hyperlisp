from fractions import Fraction
from .func import Func, External
from .error import HlError


class HlInterpreter:
  """Hyperlisp tree-walking interpreter
     Implements the semantics of Hyperlisp"""

  def __init__(self):
    self.reader = None
    self.globals = {}
    self.immutables = []

  ### PRIVATE: ###

  def _error(self, position, message):
    file, src = self.reader.filename, self.reader.src
    raise HlError(f'Runtime error: {message}', file, position, src, near=False)

  def _bind(self, name, value, scope):
    if (var := name.value) in self.immutables:
      self._error(name.pos, f'"{var}" is bound externally, so it cannot be changed')
    scope[name.value] = self._eval(value, scope)

  def _list(self, elements, scope):
    name, *tail = elements
    if name.value == 'bind': # (bind Identifier _)
      if len(tail) == 2 and tail[0].type == 'Identifier':
        return self._bind(*tail, scope)
      self._error(name.pos, 'invalid arguments to bind')
    elif name.value == 'func': # (func <Array|List|Identifier> ...)
      if len(tail) >= 2:
        params = tail[0].value if tail[0].type in ('List', 'Array') else [tail[0]]
        if all(params := [p.type == 'Identifier' and p.value for p in params]):
          return Func(self._eval, params, tail[1:], scope, name.pos)
      self._error(name.pos, 'invalid arguments to func')
    elif name.type in ('Identifier', 'List'): # (<Identifier|List> ...)
      callee = self._eval(name, scope)
      if callable(callee):
        args = (self._eval(arg, scope) for arg in tail)
        try:
          return callee(name.pos, *args)[-1]
        except TypeError as error:
          kind, details = error.args
          extern = 'external "{}", imported as "{}", failed with {}'
          user = kind == 'user' and '{} argument(s) found where {} is expected'
          self._error(name.pos, (user or extern).format(*details))
    return self._eval(elements, scope)

  def _eval(self, node, scope):
    if type(node) is list:
      return [self._eval(node, scope) for node in node]
    elif node.type == 'Root':
      return self._eval(node.value, scope)
    elif node.type == 'List':
      if not node.value:
        return []
      elif node.value[0].type in ('Identifier', 'List'):
        return self._list(node.value, scope)
      else:
        return self._eval(node.value, scope)
    elif node.type == 'Array':
      return self._eval(node.value, scope)
    elif node.type == 'Identifier':
      if (name := node.value) not in scope:
        self._error(node.pos, f'symbol "{name}" is not bound to any value')
      return scope[name]
    elif node.type == 'Number':
      return Fraction(float(node.value)).limit_denominator()
    elif node.type == 'String':
      return node.value
    else:
      raise TypeError('Internal error: trying to interpret invalid node')

  ### PUBLIC: ###

  def function(self, name, callable_):
    """Import a Python callable under the name `name`"""
    assert callable(callable_), f'"{name}" must be a function'
    self.globals[name] = External(name, callable_)
    self.immutables.append(name)

  def const(self, name, value):
    """Import `value` under the name `name` 
       if Hyperlisp will be able to understand it"""
    assert not callable(value), \
      'Use "function" to import a function'
    assert type(value) in (list, int, float, bool, Fraction, str), \
      f'Hyperlisp cannot understand the value for "{name}"'
    self.globals[name] = \
      Fraction(value).limit_denominator() if type(value) in (int, float, bool) else value
    self.immutables.append(name)

  def update(self, reader):
    """Update/set the reader"""
    self.reader = reader

  def execute(self):
    """Interact with the reader 
       and execute the AST it returns"""
    assert self.reader is not None, 'There is no reader to interact with'
    return self._eval(self.reader.process(), self.globals)[-1]
