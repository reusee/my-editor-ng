from gi.repository import Gtk, GObject, cairo, Gdk

class Layout:
  def __init__(self):
    self.emit('bind-command-key', ', v', lambda view: self.split_view(view, Gtk.Orientation.VERTICAL))
    self.emit('bind-command-key', ', h', lambda view: self.split_view(view, Gtk.Orientation.HORIZONTAL))
    self.emit('bind-command-key', ', s', self.sibling_view)
    self.emit('bind-command-key', ', z', self.close_view)

    self.emit('bind-command-key', 'J', self.south_view)
    self.emit('bind-command-key', 'K', self.north_view)
    self.emit('bind-command-key', 'H', self.west_view)
    self.emit('bind-command-key', 'L', self.east_view)

  def split_view(self, view, orientation):
    scroll = view.get_parent()
    grid = scroll.get_parent()
    new_view, new_scroll = self.new_view()
    new_view.set_buffer(view.get_buffer())

    left = GObject.Value()
    left.init(GObject.TYPE_INT)
    grid.child_get_property(scroll, 'left-attach', left)
    left = left.get_int()
    top = GObject.Value()
    top.init(GObject.TYPE_INT)
    grid.child_get_property(scroll, 'top-attach', top)
    top = top.get_int()

    grid.remove(scroll)
    new_grid = Gtk.Grid()
    new_grid.set_property('orientation', orientation)
    new_grid.add(scroll)
    new_grid.add(new_scroll)
    new_grid.show_all()
    grid.attach(new_grid, left, top, 1, 1)

    new_view.grab_focus()

  def sibling_view(self, view):
    grid = view.get_parent().get_parent()
    new_view, new_scroll = self.new_view()
    new_view.set_buffer(view.get_buffer())
    new_scroll.show_all()
    grid.add(new_scroll)
    new_view.grab_focus()

  def switch_to_view_at_pos(self, x, y):
    for view in self.views:
      alloc = view.get_allocation()
      win = view.get_window(Gtk.TextWindowType.WIDGET)
      _, left, top = win.get_origin()
      right = left + alloc.width
      bottom = top + alloc.height
      if x >= left and x <= right and y >= top and y <= bottom: # found
        self.switch_to_view(view)
        break

  def north_view(self, view):
    alloc = view.get_allocation()
    win = view.get_window(Gtk.TextWindowType.WIDGET)
    _, x, y = win.get_origin()
    self.switch_to_view_at_pos(x + alloc.width / 3, y - 30)

  def south_view(self, view):
    alloc = view.get_allocation()
    win = view.get_window(Gtk.TextWindowType.WIDGET)
    _, x, y = win.get_origin()
    self.switch_to_view_at_pos(x + alloc.width / 3, y + 30 + alloc.height)

  def west_view(self, view):
    alloc = view.get_allocation()
    win = view.get_window(Gtk.TextWindowType.WIDGET)
    _, x, y = win.get_origin()
    self.switch_to_view_at_pos(x - 30, y + alloc.height / 3)

  def east_view(self, view):
    alloc = view.get_allocation()
    win = view.get_window(Gtk.TextWindowType.WIDGET)
    _, x, y = win.get_origin()
    self.switch_to_view_at_pos(x + 20 + alloc.width, y + alloc.height / 3)

  def close_view(self, view):
    if len(self.views) == 1: return
    scroll = view.get_parent()
    index = self.views.index(view)
    self.views.remove(view)
    index -= 1
    if index < 0: index = 0
    next_view = self.views[index]
    scroll.destroy()
    self.switch_to_view(next_view)
