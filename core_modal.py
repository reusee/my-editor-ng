from gi.repository import GObject, Gtk

class Modal:
  def __init__(self):
    self.connect('view-created', self.set_key_press_handler)

  def set_key_press_handler(self, widget, view):
    view.connect('key-press-event', self.handle_key_press)

  def handle_key_press(self, view, ev):
    print(view, ev)
    buf = view.get_buffer()
    it = buf.get_iter_at_mark(buf.get_insert())
    location = view.get_iter_location(it)
    print(location.x, location.y, location.width, location.height)
    print(view.buffer_to_window_coords(Gtk.TextWindowType.WIDGET, location.x, location.y))
