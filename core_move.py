from gi.repository import Gtk

class Move:

  FORWARD, BACKWARD = range(2)

  def __init__(self):
    self.emit('bind-command-key', 'j', lambda view, n: self.move_line(view, self.FORWARD, n))
    self.emit('bind-command-key', 'k', lambda view, n: self.move_line(view, self.BACKWARD, n))
    self.emit('bind-command-key', 'h', lambda view, n: self.move_char(view, self.BACKWARD, n))
    self.emit('bind-command-key', 'l', lambda view, n: self.move_char(view, self.FORWARD, n))
    self.emit('bind-command-key', 'f', self.make_char_locator())
    self.emit('bind-command-key', 'F', self.make_char_locator(backward = True))
    self.emit('bind-command-key', ';', self.locate_last)

    self.connect('buffer-created',
        lambda _, buf: buf.connect('notify::cursor-position', 
          lambda buf, _: self.update_offset(buf)))

  def move_line(self, view, direction, n):
    if n == 0: n = 1
    buf = view.get_buffer()
    it = buf.get_iter_at_mark(buf.get_insert())
    if direction == self.FORWARD:
      for i in range(n): view.forward_display_line(it)
    else:
      for i in range(n): view.backward_display_line(it)
    bytes_in_line = it.get_bytes_in_line()
    offset = buf.attr['current_offset']
    if bytes_in_line <= buf.attr['current_offset']:
      offset = bytes_in_line - 1
    if offset > 0:
      it.set_line_offset(offset)
    buf.attr['freeze'] = True
    buf.place_cursor(it)
    buf.attr['freeze'] = False

  def update_offset(self, buf):
    if buf.attr.get('freeze', False): return
    buf.attr['current_offset'] = buf.get_iter_at_mark(buf.get_insert()).get_line_offset()

  def move_char(self, view, direction, n):
    if n == 0: n = 1
    buf = view.get_buffer()
    it = buf.get_iter_at_mark(buf.get_insert())
    if direction == self.FORWARD:
      for i in range(n): it.forward_char()
    else:
      for i in range(n): it.backward_char()
    buf.place_cursor(it)

  def make_char_locator(self, backward = False):
    handler = {}
    def make(c):
      if backward:
        def f(view):
          buf = view.get_buffer()
          it = buf.get_iter_at_mark(buf.get_insert())
          orig = it.copy()
          it = it.backward_search(c, 0, buf.get_start_iter())
          if it: 
            buf.place_cursor(it[0])
            view.attr['last_locate_func'] = f
          else: 
            buf.place_cursor(orig)
        return f
      else:
        def f(view):
          buf = view.get_buffer()
          it = buf.get_iter_at_mark(buf.get_insert())
          orig = it.copy()
          it.forward_char()
          it = it.forward_search(c, 0, buf.get_end_iter())
          if it: 
            buf.place_cursor(it[0])
            view.attr['last_locate_func'] = f
          else: 
            buf.place_cursor(orig)
        return f
    for i in range(0x20, 0x7F):
      handler[chr(i)] = make(chr(i))
    return handler

  def locate_last(self, view):
    if 'last_locate_func' in view.attr:
      view.attr['last_locate_func'](view)
