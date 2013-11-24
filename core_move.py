from gi.repository import Gtk

class Move:

  FORWARD, BACKWARD = range(2)

  def __init__(self):
    self.emit('bind-command-key', 'j', lambda view, n: self.move_line(view, self.FORWARD, n))
    self.emit('bind-command-key', 'k', lambda view, n: self.move_line(view, self.BACKWARD, n))
    self.emit('bind-command-key', 'h', lambda view, n: self.move_char(view, self.BACKWARD, n))
    self.emit('bind-command-key', 'l', lambda view, n: self.move_char(view, self.FORWARD, n))

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
