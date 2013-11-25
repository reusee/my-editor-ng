class Selection:
  def __init__(self):
    self.emit('bind-command-key', 'v', self.toggle_char_selection)

  def toggle_char_selection(self, view):
    if self.selection_mode != self.CHAR:
      self.selection_mode = self.CHAR
    else:
      self.selection_mode = self.NONE
      buf = view.get_buffer()
      it = buf.get_iter_at_mark(buf.get_insert())
      buf.place_cursor(it)
