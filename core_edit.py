class Edit:
  def __init__(self):
    self.emit('bind-command-key', 'i', self.enter_edit_mode)

    self.new_signal('edit-mode-entered', ())

  def enter_edit_mode(self):
    self.operation_mode = self.EDIT
    self.reset_key_handler(self.edit_key_handler)
    self.emit('edit-mode-entered')
