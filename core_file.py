class File:
  def __init__(self):
    self.emit('bind-command-key', ', t', self.open_file)
    
  def open_file(self, view):
    pass