from gi.repository import Gtk, GtkSource

class Status:
  def __init__(self):
    self.connect('view-created', lambda _, view:
        view.connect('draw', self.draw_status))
    self.connect('key-pressed', lambda _:
        self.current_view.queue_draw())

    # relative numer
    self.connect('view-created', lambda _, view:
        self.setup_relative_line_number(view))

    # command
    self.command_prefix = []
    self.connect('key-handler-reset', lambda w: self.command_prefix.clear())
    self.connect('key-handler-prefix', lambda w, c: self.command_prefix.append(c))

    # status line
    self.status_line = Gtk.Grid()
    self.status_line.set_hexpand(True)
    self.connect('realize', lambda _: self.south_area.add(self.status_line))
    self.current_buffer_filename = Gtk.Entry()
    self.current_buffer_filename.set_hexpand(True)
    self.status_line.add(self.current_buffer_filename)
    self.status_line.show_all()

    # current buffer filename
    self.connect('view-created', lambda _, view:
      view.connect('notify::buffer', lambda view, _:
        self.current_buffer_filename.set_text(
          view.get_buffer().attr['filename'])))
    self.connect('view-created', lambda _, view:
      view.connect('grab-focus', lambda view:
        self.current_buffer_filename.set_text(
          view.get_buffer().attr['filename'])))

  def draw_status(self, view, cr):
    if not view.is_focus(): return
    rect = view.get_allocation()
    cr.select_font_face('Times')
    cr.set_font_size(256)
    cr.set_source_rgb(0.2, 0.2, 0.2)
    cr.move_to(rect.width / 3, rect.height / 2)

    # operation_mode
    if self.operation_mode == self.COMMAND:
        cr.show_text('C')

    # command
    cr.set_font_size(128)
    t = ''.join(self.command_prefix)
    if self.n != 0: t = str(self.n) + t
    cr.show_text(t)

    # selection_mode
    cr.move_to(rect.width / 3 + 50, rect.height / 2 - 50)
    if self.selection_mode == self.CHAR:
        cr.show_text('c')
    elif self.selection_mode == self.LINE:
        cr.show_text('l')
    elif self.selection_mode == self.RECT:
        cr.show_text('r')

    # current column
    buf = view.get_buffer()
    cursor_rect = view.get_iter_location(buf.get_iter_at_mark(buf.get_insert()))
    if buf.get_modified():
      cr.set_source_rgb(0, 0.3, 0.5)
    else:
      cr.set_source_rgb(0, 0.5, 0)
    if self.operation_mode == self.COMMAND:
      cr.set_line_width(2)
    else:
      cr.set_line_width(4)
    x, _ = view.buffer_to_window_coords(Gtk.TextWindowType.WIDGET, cursor_rect.x, 0)
    cr.move_to(x, 0)
    cr.line_to(x, rect.height)
    cr.stroke()

  def setup_relative_line_number(self, view):
      gutter = view.get_gutter(Gtk.TextWindowType.LEFT)
      renderer = RelativeNumberRenderer(view)
      gutter.insert(renderer, 0)

class RelativeNumberRenderer(GtkSource.GutterRendererText):
    def __init__(self, view):
      GtkSource.GutterRendererText.__init__(self)
      self.set_alignment(1, 1)
      self.view = view

    def do_query_data(self, start, end, state):
      if not self.view.is_focus():
        self.set_size(0)
        return
      buf = start.get_buffer()
      current_line = buf.get_iter_at_mark(buf.get_insert()).get_line()
      text = str(abs(start.get_line() - current_line))
      self.set_text(text, -1)
      self.set_size(30)
      self.queue_draw()
