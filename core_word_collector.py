import re

class WordCollector:
  def __init__(self):
    self.connect('buffer-created', self.buffer_setup_completion)
    self.connect('entered-edit-mode', self.update_word_bound_entering_edit)
    self.connect('entered-command-mode', self.update_word_bound_leaving_edit)

    self.new_signal('found-word', (str,))

    self.connect('file-loaded', self.collect_file_words)

  def buffer_setup_completion(self, _, buf):
    buf.attr['word-start'] = buf.create_mark(None,
      buf.get_start_iter(), left_gravity = True)
    buf.attr['word-end'] = buf.create_mark(None,
      buf.get_start_iter(), left_gravity = True)
    buf.connect('changed', self.update_word_bound)

  def word_start_iter_extend(self, start_iter):
    it = start_iter.copy()
    while it.backward_char():
      if self.is_word_char(it.get_char()):
        start_iter.backward_char()
      else:
        break
    return start_iter

  def word_end_iter_extend(self, end_iter, limit_iter):
    word_ended = False
    while end_iter.compare(limit_iter) < 0:
      if self.is_word_char(end_iter.get_char()):
        end_iter.forward_char()
      else:
        word_ended = True
        break
    return end_iter, word_ended

  def update_word_bound_entering_edit(self, _):
    buf = self.get_current_buffer()
    start_iter = buf.get_iter_at_mark(buf.get_insert())
    end_iter = start_iter.copy()

    start_iter = self.word_start_iter_extend(start_iter)

    buf.move_mark(buf.attr['word-end'], end_iter)
    buf.move_mark(buf.attr['word-start'], start_iter)

  def update_word_bound_leaving_edit(self, _):
    buf = self.get_current_buffer()
    start_iter = buf.get_iter_at_mark(buf.attr['word-start'])
    end_iter = buf.get_iter_at_mark(buf.attr['word-end'])

    end_iter, _ = self.word_end_iter_extend(end_iter, buf.get_end_iter())

    if start_iter.compare(end_iter) < 0:
      self.emit('found-word', buf.get_text(start_iter, end_iter, False))

  def update_word_bound(self, buf):
    if self.operation_mode != self.EDIT: return
    start_iter = buf.get_iter_at_mark(buf.attr['word-start'])
    end_iter = buf.get_iter_at_mark(buf.attr['word-end'])
    cursor_iter = buf.get_iter_at_mark(buf.get_insert())

    start_iter = self.word_start_iter_extend(start_iter)

    end_iter, word_ended = self.word_end_iter_extend(end_iter, cursor_iter)

    if word_ended or start_iter.compare(end_iter) == 0: # reset start and end
      if start_iter.compare(end_iter) < 0:
        self.emit('found-word', buf.get_text(start_iter, end_iter, False))
      buf.move_mark(buf.attr['word-start'], cursor_iter)
      buf.move_mark(buf.attr['word-end'], cursor_iter)
    else:
      buf.move_mark(buf.attr['word-end'], end_iter)
      buf.move_mark(buf.attr['word-start'], start_iter)

  def is_word_char(self, c):
    od = ord(c.lower())
    if od >= ord('a') and od <= ord('z'): return True
    if c.isdigit(): return True
    if c in {'-', '_'}: return True
    return False

  def collect_file_words(self, _, buf):
    text = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False)
    words = re.findall('[a-zA-Z0-9-_]+', text)
    words = {w for w in words if len(w) > 1}
    for word in words:
      self.emit('found-word', word)
