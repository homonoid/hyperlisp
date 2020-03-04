class HlError(Exception):
  def __init__(self, caption, filename, position, source, near=True):
    self.cap = caption
    self.filename = filename
    self.pos = position
    self.src = source
    self.near = near

  @property
  def char(self):
    return \
      'end-of-input' if self.pos == len(self.src) - 1 else f'"{self.src[self.pos]}"'

  @property
  def line(self):
    return self.src.count('\n', 0, self.pos) + 1

  @property
  def col(self):
    nl = self.src.rfind('\n', 0, self.pos)
    return self.pos - (0 if nl < 0 else nl) + 1

  def _fmt(self):
    near = f' near {self.char}' if self.near else ''
    return f'{self.cap}{near} (line {self.line}, column {self.col}, in "{self.filename}")'

  def __repr__(self):
    return self._fmt()

  def __str__(self):
    return f'<HlError {self.line=} {self.col=} {self.pos=} {self.cap=}>'
