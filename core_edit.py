from gi.repository import Gtk, Gdk

class Edit:
  def __init__(self):

    self.emit('bind-command-key', 'i', self.enter_edit_mode)

    self.emit('bind-command-key', 'd', self.delete_selection)
    self.emit('bind-command-key', 'c', self.change_selection)
    self.emit('bind-command-key', 'y', self.copy_selection)
    self.emit('bind-command-key', 'p', self.paste)

    self.emit('bind-command-key', 'u', self.undo)
    self.emit('bind-command-key', 'Y', self.redo)

    self.emit('bind-command-key', 'o', self.newline_below)
    self.emit('bind-command-key', 'O', self.newline_above)
    self.emit('bind-command-key', 'a', self.append_current_pos)
    self.emit('bind-command-key', 'A', self.append_current_line)
    self.emit('bind-command-key', 'x', self.delete_current_char)

    self.emit('bind-edit-key', 'k d', self.enter_command_mode)

    self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

  def delete_selection(self, view):
    if self._delete_selection(view):
      self.enter_none_selection_mode(view)
    else:
      return self.make_text_object_handler(self._delete_selection)

  def _delete_selection(self, view):
    buf = view.get_buffer()
    if buf.get_has_selection():
        buf.copy_clipboard(self.clipboard)
        buf.delete_selection(True, True)
        return True

  def change_selection(self, view):
    if self._delete_selection(view):
      self.enter_none_selection_mode(view)
      self.enter_edit_mode()
    else:
      return self.make_text_object_handler(self._change_selection)

  def _change_selection(self, view):
      self._delete_selection(view)
      self.enter_edit_mode()

  def copy_selection(self, view):
    buf = view.get_buffer()
    if 'copy-mark' not in buf.attr:
      buf.attr['copy-mark'] = buf.create_mark(None, buf.get_iter_at_mark(buf.get_insert()))
    else:
      buf.move_mark(buf.attr['copy-mark'], buf.get_iter_at_mark(buf.get_insert()))
    if not self._copy_selection(view):
      return self.make_text_object_handler(self._copy_selection)

  def _copy_selection(self, view):
    buf = view.get_buffer()
    if buf.get_has_selection():
      buf.copy_clipboard(self.clipboard)
      self.enter_none_selection_mode(view)
      buf.place_cursor(buf.get_iter_at_mark(buf.attr['copy-mark']))
      return True

  def paste(self, view):
    buf = view.get_buffer()
    buf.paste_clipboard(self.clipboard, None, True)

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

  def newline_above(self, view):
    buf = view.get_buffer()
    buf.begin_user_action()
    it = buf.get_iter_at_mark(buf.get_insert())
    it.set_line_offset(0)
    buf.insert(it, '\n')
    it.backward_line()
    #TODO indent
    buf.place_cursor(it)
    self.enter_edit_mode()
    buf.end_user_action()

  def newline_below(self, view):
    buf = view.get_buffer()
    buf.begin_user_action()
    it = buf.get_iter_at_mark(buf.get_insert())
    if not it.ends_line(): it.forward_to_line_end()
    buf.insert(it, '\n')
    #TODO indent
    buf.place_cursor(it)
    self.enter_edit_mode()
    buf.end_user_action()

  def append_current_line(self, view):
    self.move_to_line_end(view)
    self.enter_edit_mode()    

  def append_current_pos(self, view):
    self.move_char(view, 1)
    self.enter_edit_mode()    

  def delete_current_char(self, view):
    buf = view.get_buffer()
    start = buf.get_iter_at_mark(buf.get_insert())
    end = start.copy()
    end.forward_char()
    buf.delete(start, end)
