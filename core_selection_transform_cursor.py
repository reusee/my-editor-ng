class CoreSelectionTransformCursor:
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
