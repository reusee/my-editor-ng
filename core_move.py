from gi.repository import Gtk

class Move:
  def __init__(self):
    self.emit('bind-command-key', 'j', lambda view: self.move_line(view, 1))
    self.emit('bind-command-key', 'k', lambda view: self.move_line(view, -1))

    self.connect('buffer-created',
        lambda _, buf: buf.connect('notify::cursor-position', 
          lambda buf, _: self.update_offset(buf)))

  def move_line(self, view, n):
    buf = view.get_buffer()
    it = buf.get_iter_at_mark(buf.get_insert())
    if n > 0:
      for i in range(n): view.forward_display_line(it)
    else:
      for i in range(abs(n)): view.backward_display_line(it)
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
