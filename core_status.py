from gi.repository import Gtk, GtkSource
class Status:
  def __init__(self):
    self.connect('view-created', lambda _, view:
        view.connect('draw', self.draw_status))
    self.connect('edit-mode-entered', lambda _:
        self.current_view.queue_draw())
    self.connect('command-mode-entered', lambda _:
        self.current_view.queue_draw())

  def draw_status(self, view, cr):
    if self.operation_mode == self.COMMAND:
        rect = view.get_allocation()
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.move_to(rect.width / 2, rect.height / 2)
        cr.select_font_face('Times')
        cr.set_font_size(256)
        cr.show_text('C')
