class CoreSelectionTransformCursor:
    def __init__(self):
        self.connect('buffer-created',
            lambda _, buf: buf.connect('notify::cursor-position',
              lambda buf, _: self.update_preferred_line_offset(buf)))

    def update_preferred_line_offset(self, buf):
        if buf.attr.get('freeze', False): return
        buf.attr['preferred-line-offset'] = buf.get_iter_at_mark(buf.get_insert()).get_line_offset()

    def sel_trans_jump_line_with_preferred_offset(self, view, n, selections, backward = False):
        buf = view.get_buffer()
        for sel in selections:
            it = buf.get_iter_at_mark(sel.start)
            if not backward:
                for i in range(n): view.forward_display_line(it)
            else:
                for i in range(n): view.backward_display_line(it)
        chars_in_line = it.get_chars_in_line() - 1
        offset = buf.attr['preferred-line-offset']
        if offset > chars_in_line: offset = chars_in_line
        if offset > 0: it.set_line_offset(offset)
        buf.attr['freeze'] = True
        buf.move_mark(sel.start, it)
        buf.move_mark(sel.end, it)
        buf.attr['freeze'] = False

    def sel_trans_jump_char(self, view, n, selections, backward = False):
        buf = view.get_buffer()
        for sel in selections:
            it = buf.get_iter_at_mark(sel.start)
            if not backward:
                for i in range(n): it.forward_char()
            else:
                for i in range(n): it.backward_char()
            buf.move_mark(sel.start, it)
            buf.move_mark(sel.end, it)

    def sel_trans_jump_search(self, view, n, selections, s, backward = False):
        buf = view.get_buffer()
        for sel in selections:
            it = buf.get_iter_at_mark(sel.start)
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
            buf.move_mark(sel.start, it)
            buf.move_mark(sel.end, it)

    def sel_trans_jump_to_line_n(self, view, n, selections):
        buf = view.get_buffer()
        for sel in selections:
            it = buf.get_start_iter()
            it.set_line(n - 1)
            buf.move_mark(sel.start, it)
            buf.move_mark(sel.end, it)

    def sel_trans_jump_to_buffer_end(self, view, n, selections):
        buf = view.get_buffer()
        for sel in selections:
            buf.move_mark(sel.start, buf.get_end_iter())
            buf.move_mark(sel.end, buf.get_end_iter())

    def sel_trans_jump_to_line_start(self, view, n, selections):
        buf = view.get_buffer()
        for sel in selections:
            it = buf.get_iter_at_mark(sel.start)
            if it.starts_line():
                while it.get_char().isspace() and not it.ends_line():
                    it.forward_char()
            else:
                it.set_line_offset(0)
            buf.move_mark(sel.start, it)
            buf.move_mark(sel.end, it)

    def sel_trans_jump_to_line_end(self, view, n, selections):
        buf = view.get_buffer()
        for sel in selections:
            it = buf.get_iter_at_mark(sel.start)
            if not it.ends_line(): it.forward_to_line_end()
            buf.move_mark(sel.start, it)
            buf.move_mark(sel.end, it)
