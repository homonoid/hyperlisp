from .error import HlError


class Func:
  """Anonymous function execution & formatting engine
     In-lang usage: (func <Array|List|Identifier> ...)"""

  def __init__(self, engine, params, body, parent, position):
    self.engine = engine
    self.params = params
    self.body = body
    self.parent = parent
    self.position = position
    self.arity = len(params)

  def __call__(self, callpos, *args):
    if len(args) == self.arity:
      scope = zip(self.params, args)
      return self.engine(self.body, {**self.parent, **dict(scope)})
    raise TypeError('user', (len(args), self.arity))

  def __str__(self):
    return '(func (%s) ...)' % ' '.join(self.params)


class External:
  """External function execution & formatting engine
     Makes Python functions look Hyperlisp"""

  def __init__(self, name, function):
    self.name = name
    self.function = function
  
  def __call__(self, callpos, *args):
    try:
      return [self.function(*args)]
    except Exception as error:
      details = (self.name, self.function.__name__, type(error).__name__)
      raise TypeError('extern', details)

  def __str__(self):
    return f'<external "{self.name}">'
