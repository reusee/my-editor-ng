class Edit:
  def __init__(self):
    self.emit('bind-command-key', 'i', self.enter_edit_mode)
    self.emit('bind-edit-key', 'k d', self.enter_command_mode)
