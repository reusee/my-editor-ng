from gi.repository import Gtk, GtkSource
class Status:
  def __init__(self):
    self.connect('view-created', lambda _, view:
        view.connect('draw', self.draw_status))
    self.connect('key-pressed', lambda _:
        self.current_view.queue_draw())

    self.command_prefix = []
    self.connect('key-handler-reset', lambda w: self.command_prefix.clear())
    self.connect('key-handler-prefix', lambda w, c: self.command_prefix.append(c))

  def draw_status(self, view, cr):
    rect = view.get_allocation()
    cr.select_font_face('Times')
    cr.set_font_size(256)
    cr.set_source_rgb(0.2, 0.2, 0.2)
    cr.move_to(rect.width / 2, rect.height / 2)
    # operation_mode
    if self.operation_mode == self.COMMAND:
        cr.show_text('C')
    # command
    cr.set_font_size(128)
    t = ''.join(self.command_prefix)
    if self.n != 0: t = str(self.n) + t
    cr.show_text(t)
    # selection_mode
    cr.move_to(rect.width / 2 + 50, rect.height / 2 - 50)
    if self.selection_mode == self.CHAR:
        t = 'c'
    elif self.selection_mode == self.LINE:
        t = 'l'
    elif self.selection_mode == self.RECT:
        t = 'r'
    cr.show_text(t)
