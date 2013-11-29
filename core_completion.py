class Completion:
  def __init__(self):
    self.connect('view-created', self.setup_completion)

  def setup_completion(self, _, view):
    pass
