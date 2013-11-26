class Edit:
  def __init__(self):

    self.emit('bind-command-key', 'i', self.enter_edit_mode)

    self.emit('bind-command-key', 'd', self.delete_selection)

    self.emit('bind-command-key', 'u', self.undo)
    self.emit('bind-command-key', 'Y', self.redo)

    self.emit('bind-edit-key', 'k d', self.enter_command_mode)

  def delete_selection(self, view):
    if self._delete_selection(view):
      self.enter_none_selection_mode(view)
    else:
      return self.make_text_object_handler(lambda view: self._delete_selection(view))

  def _delete_selection(self, view):
    buf = view.get_buffer()
    if buf.get_has_selection():
        buf.delete_selection(True, True)
        return True

  def undo(self, view):
    buf = view.get_buffer()
    if buf.can_undo():
        buf.undo()
        buf.place_cursor(buf.get_iter_at_mark(buf.get_insert()))

  def redo(self, view):
    buf = view.get_buffer()
    if buf.can_redo():
        buf.redo()
        buf.place_cursor(buf.get_iter_at_mark(buf.get_insert()))
