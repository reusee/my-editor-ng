class Formatter:
  def __init__(self):
    self.connect('before-saving', self.strip_trailing_whitespace)
    self.connect('before-saving', self.ensure_last_newline)

  def ensure_last_newline(self, _, buf):
    it = buf.get_end_iter()
    if not it.backward_char(): return
    if it.get_char() != '\n':
      buf.insert(buf.get_end_iter(), '\n', -1)

  def strip_trailing_whitespace(self, _, buf):
    for l in range(buf.get_line_count()):
      start = buf.get_iter_at_line(l)
      end = start.copy()
      if not end.ends_line():
        end.forward_to_line_end()
      eol = end.copy()
      while end.compare(start) == 1:
        end.backward_char()
        if not end.get_char().isspace():
          end.forward_char()
          break
      buf.delete(end, eol)
