class CoreMark:
    def __init__(self):
        self.connect('buffer-created',
            lambda _, buf: buf.connect('notify::cursor-position',
              lambda buf, _: self.update_preferred_line_offset(buf)))

    def update_preferred_line_offset(self, buf):
        if buf.attr.get('freeze', False): return
        buf.attr['preferred-line-offset'] = buf.get_iter_at_mark(
            buf.get_insert()).get_line_offset()

    def mark_jump_relative_line_with_preferred_offset(self, mark, view, n,
        backward = False):
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(mark)
        if backward:
            for _ in range(n): it.backward_line()
        else:
            for _ in range(n): it.forward_line()
        chars_in_line = it.get_chars_in_line() - 1
        offset = buf.attr['preferred-line-offset']
        if offset > chars_in_line: offset = chars_in_line
        if offset >= 0: it.set_line_offset(offset)
        buf.attr['freeze'] = True
        buf.move_mark(mark, it)
        buf.attr['freeze'] = False
