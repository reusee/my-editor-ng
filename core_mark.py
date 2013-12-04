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

    def mark_jump_relative_char(self, mark, view, n, backward = False):
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(mark)
        if backward:
            for _ in range(n): it.backward_char()
        else:
            for _ in range(n): it.forward_char()
        buf.move_mark(mark, it)

    def mark_jump_to_string(self, mark, view, n, s, backward = False):
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(mark)
        for _ in range(n):
            if backward:
                res = it.backward_search(s, 0, buf.get_start_iter())
                if res: it = res[0]
                else: break
            else:
                pin = it.copy()
                pin.forward_char()
                res = pin.forward_search(s, 0, buf.get_end_iter())
                if res: it = res[0]
                else: break
        buf.move_mark(mark, it)

    def mark_jump_to_line_n(self, mark, view, n):
        buf = view.get_buffer()
        it = buf.get_start_iter()
        it.set_line(n - 1)
        buf.move_mark(mark, it)

    def mark_jump_to_line_start(self, mark, view, n):
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(mark)
        if it.starts_line():
            while it.get_char().isspace() and not it.ends_line():
                it.forward_char()
        else:
            it.set_line_offset(0)
        buf.move_mark(mark, it)

    def mark_jump_to_line_end(self, mark, view, n):
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(mark)
        if not it.ends_line(): it.forward_to_line_end()
        buf.move_mark(mark, it)
