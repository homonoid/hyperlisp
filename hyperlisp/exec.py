from fractions import Fraction
import inspect
from .error import HlError


class HlInterpreter:
  def __init__(self):
    self.reader = None
    self.metascope = {}

  def _error(self, position, message):
    """Produce a runtime error"""
    raise HlError(
      f'Runtime error: {message}', 
      self.reader.filename, position, self.reader.src, near=False
    )
  
  def _func(self, params, body, scope):
    """Implementation for builtin (func <Array|List|Identifier> _+)"""
    def callee(pos, *args):
      paramc, argc = len(params), len(args)
      if paramc == argc:
        params_str = [param.value for param in params]
        return self._eval(body, {**scope, **dict(zip(params_str, args),)})[-1]
      else:
        self._error(pos,
          f'invalid number of arguments: expected {paramc}, but found {argc}'
        )
    return callee

  def _bind(self, name, value, scope):
    """Implementation for builtin (bind Identifier _)"""
    if (var := name.value) not in self.metascope:
      scope[var] = self._eval(value, scope)
    else:
      self._error(name.pos, f'"{var}" is bound externally, so it cannot mutate')

  def _invoke(self, list_, scope):
    """Try to invoke a user-defined/builtin procedure; if not possible, 
       interpret it as an array"""
    name, *tail = list_
    arity = len(tail)
    if name.value == 'bind' and arity == 2 and tail[0].type == 'Identifier':
      return self._bind(*tail, scope)
    elif name.value == 'func':
      if arity >= 2:
        if tail[0].type == 'Identifier':
          return self._func([tail[0]], tail[1:], scope)
        elif tail[0].type in ('List', 'Array') and \
              all([param.type == 'Identifier' for param in tail[0].value]):
          return self._func(tail[0].value, tail[1:], scope)
      self._error(tail[0].pos, f'invalid parameters to func')
    elif name.type == 'Identifier' and name.value in scope.keys():
      if callable(callee := scope[name.value]):
        return callee(name.pos, *[self._eval(arg, scope) for arg in tail])
      self._error(name.pos, f'"{name.value}" is not a func')
    elif name.type == 'List' and callable(callee := self._eval(name, scope)):
      return callee(name.pos, *[self._eval(arg, scope) for arg in tail])
    else:
      return self._eval(list_, scope)

  def _eval(self, given, scope):
    """Execute a single node, or a `list` of nodes, according to `scope`"""
    if type(given) is list:
      return [self._eval(node, scope) for node in given]
    elif given.type == 'Root':
      return self._eval(given.value, scope)
    elif given.type == 'List':
      if not given.value:
        return []
      elif given.value[0].type not in ('Identifier', 'List'):
        return self._eval(given.value, scope)
      else:
        return self._invoke(given.value, scope)
    elif given.type == 'Array':
      return self._eval(given.value, scope)
    elif given.type == 'Identifier':
      if (name := given.value) not in scope:
        self._error(given.pos, f'symbol "{name}" is not bound to any value')
      return scope[name]
    elif given.type == 'Number':
      return Fraction(float(given.value),).limit_denominator()
    elif given.type == 'String':
      return given.value

  def funcpy(self, name, fun):
    """Import a Python callable `fun` into the metascope under the name `name`"""
    assert callable(fun)
    def _handler(pos, *args):
      try:
        return fun(*args)
      except Exception as e:
        # TODO: provide additional information about the error (lineno, file, etc.)
        self._error(pos, 
          f'external function "{fun.__name__}" (imported as "{name}")' \
          f' failed with {type(e).__name__}'
        )
    self.metascope[name] = _handler

  def bindpy(self, name, value):
    """Check if the value can be used within the language
       and, if so, import it into the metascope"""
    if callable(value): 
      raise TypeError('Use "funcpy" to import a callable')
    elif type(value) in (int, float):
      value = Fraction(value).limit_denominator()
    assert type(value) in (list, Fraction, str)
    self.metascope[name] = value

  def update(self, reader):
    """Update the reader that the interpreter interacts with"""
    self.reader = reader

  def execute(self):
    """Interact with the reader and execute the AST it returns"""
    return self._eval(self.reader.process(), self.metascope)[-1]
