try:
  import re2 as re
except ImportError:
  import re


from dataclasses import dataclass
from .error import HlError


@dataclass
class HlNode:
  type: str
  value: str
  pos: int


class HlReader:
  def __init__(self, filename, source):
    self.filename = filename
    self.src = source + '\0'
    self.pos = 0
    self.token = self._fetch()

  def _matches(self, seq):
    assert type(seq) is str
    if match := re.match(seq, self.src[(start := self.pos):]):
      value = match.group()
      self.pos += len(value)
      return value, start

  def _fetch(self):
    if _ := self._matches(r'\-?([0-9]+\.[0-9]+|[1-9][0-9]*|0)'):
      return 'NUM', *_
    elif _ := self._matches(r'[a-zA-Z_][a-zA-Z0-9_]*|[\+\-\*\/]'):
      return 'ID', *_
    elif _ := self._matches(r'"([^"\n\\]|\\[rbnv"\\])*"'):
      return 'STR', _[0][1:-1], _[1]
    elif _ := self._matches(r'[\(\)\[\]]'):
      return _[0], *_
    elif self._matches(r';[^\n\0]*|[ \n\t\r]+'):
      return self._fetch()
    elif _ := self._matches('\0'):
      return 'EOF', *_
    else:
      raise HlError('Lexical error', self.filename, self.pos, self.src)

  def _syntax_error(self):
    raise HlError(
      'Syntax error: invalid syntax',
      self.filename, self.token[2], self.src
    )

  def _found(self, type_):
    if (token := self.token)[0] == type_:
      if self.pos < len(self.src): 
        self.token = self._fetch()
      return token

  def _listy(self, terminator):
    if not self._found(terminator):
      if item := self._atom() or self._list() or self._syntax_error(): 
        return [item] + (self._listy(terminator) or [])

  def _atom(self):
    atomar = { 'ID': 'Identifier', 'NUM': 'Number', 'STR': 'String' }

    for type_ in atomar.keys():
      if _ := self._found(type_):
        return HlNode(atomar[type_], _[1], _[2])
    
    if _ := self._found('['):
      return HlNode('Array', self._listy(']') or [], _[2])

  def _list(self):
    if _ := self._found('('):
      return HlNode('List', self._listy(')') or [], _[2])

  def process(self):
    return HlNode('Root', self._listy('EOF') or [], 0)
