class Edit:
  def __init__(self):

    self.emit('bind-command-key', 'i', self.enter_edit_mode)
    self.emit('bind-command-key', 'd', self.delete)

    self.emit('bind-edit-key', 'k d', self.enter_command_mode)

  def delete(self, view):
    buf = view.get_buffer()
    if buf.get_has_selection():
      buf.delete_selection(True, True)
      self.toggle_char_selection(view)
