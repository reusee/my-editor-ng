class CoreSelectionTransformCursor:
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

    def sel_trans_jump_search(self, view, n, selections, s,
        backward = False):
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

    def sel_trans_jump_to_empty_line(self, view, n, selections,
        backward = False):
        buf = view.get_buffer()
        for sel in selections:
            it = buf.get_iter_at_mark(sel.start)
            if backward: f = it.backward_line
            else: f = it.forward_line
            while n > 0:
                ret = f()
                while ret and it.get_bytes_in_line() != 1:
                    ret = f()
                n -= 1
            buf.move_mark(sel.start, it)
            buf.move_mark(sel.end, it)

    def sel_trans_jump_matching_bracket(self, view, n, selections):
        buf = view.get_buffer()
        for sel in selections:
            it = buf.get_iter_at_mark(sel.start)

            start = it.get_char()
            is_left = False
            match = None
            for left, right in self.BRACKETS.items():
                if left == right: continue
                if left == start:
                    is_left = True
                    match = right
                    break
                elif right == start:
                    match = left
                    break
            if not match: it.backward_char()

            start = it.get_char()
            is_left = False
            match = None
            for left, right in self.BRACKETS.items():
                if left == right: continue
                if left == start:
                    is_left = True
                    match = right
                    break
                elif right == start:
                    match = left
                    break
            if not match: return

            balance = 0
            found = False
            if is_left: it.forward_char()
            else: it.backward_char()
            while True:
                c = it.get_char()
                if c == match and balance == 0: # found
                    found = True
                    break
                elif c == match:
                    balance -= 1
                elif c == start:
                    balance += 1
                if is_left:
                    if not it.forward_char(): break
                else:
                    if not it.backward_char(): break
            if not found: return

            buf.move_mark(sel.start, it)
            buf.move_mark(sel.end, it)
