from gi.repository import Gtk
class Status:
  def __init__(self):
    self.connect('view-created', lambda _, view:
        view.connect('draw', self.draw_status))

  def draw_status(self, view, cr):
    cr.set_line_width(5)
    cr.move_to(0, 0)
    cr.line_to(500, 500)
    cr.stroke()
