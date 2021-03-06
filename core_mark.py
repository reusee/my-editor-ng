class CoreMark:
    def __init__(self):
        self.connect('buffer-created',
            lambda _, buf: buf.connect('notify::cursor-position',
              lambda buf, _: self.update_preferred_line_offset(buf)))

    def update_preferred_line_offset(self, buf):
        current_transform = buf.attr['current-transform']
        if current_transform is not None and self.operation_mode == self.COMMAND:
            if current_transform.start_func == self.mark_jump_relative_line_with_preferred_offset:
                return
        buf.attr['preferred-line-offset'] = buf.get_iter_at_mark(
            buf.get_insert()).get_line_offset()

    def mark_jump_relative_line_with_preferred_offset(self, mark, buf, n,
        backward = False):
        it = buf.get_iter_at_mark(mark)
        if backward:
            for _ in range(n): it.backward_line()
        else:
            for _ in range(n): it.forward_line()
        chars_in_line = it.get_chars_in_line() - 1
        offset = buf.attr['preferred-line-offset']
        if offset > chars_in_line: offset = chars_in_line
        if offset >= 0: it.set_line_offset(offset)
        buf.move_mark(mark, it)
        return it

    def mark_jump_relative_char(self, mark, buf, n, backward = False):
        it = buf.get_iter_at_mark(mark)
        if backward:
            for _ in range(n): it.backward_char()
        else:
            for _ in range(n): it.forward_char()
        buf.move_mark(mark, it)
        return it

    def mark_jump_to_string(self, mark, buf, n, s, backward = False):
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
        return it

    def mark_jump_to_line_n(self, mark, buf, n):
        it = buf.get_start_iter()
        it.set_line(n - 1)
        buf.move_mark(mark, it)
        return it

    def mark_jump_to_line_start_or_nonspace_char(self, mark, buf, n):
        it = buf.get_iter_at_mark(mark)
        if it.starts_line():
            while it.get_char().isspace() and not it.ends_line():
                it.forward_char()
        else:
            it.set_line_offset(0)
        buf.move_mark(mark, it)
        return it

    def mark_jump_to_first_nonspace_char(self, mark, buf, n):
        it = buf.get_iter_at_mark(mark)
        it.set_line_offset(0)
        while it.get_char().isspace() and not it.ends_line():
            it.forward_char()
        buf.move_mark(mark, it)
        return it

    def mark_jump_to_line_end(self, mark, buf, n):
        it = buf.get_iter_at_mark(mark)
        if not it.ends_line(): it.forward_to_line_end()
        buf.move_mark(mark, it)
        return it

    def mark_jump_to_empty_line(self, mark, buf, n, backward = False):
        it = buf.get_iter_at_mark(mark)
        if backward: f = it.backward_line
        else: f = it.forward_line
        while n > 0:
            ret = f()
            while ret and it.get_bytes_in_line() != 1:
                ret = f()
            n -= 1
        buf.move_mark(mark, it)
        return it

    def mark_jump_to_matching_bracket(self, mark, buf, n):
        it = buf.get_iter_at_mark(mark)

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

        buf.move_mark(mark, it)
        return it

    def mark_jump_to_line_start(self, mark, buf, n, backward = False):
        it = buf.get_iter_at_mark(mark)
        if not it.starts_line(): it.set_line_offset(0)
        for _ in range(n - 1):
            if backward: it.backward_line()
            else: it.forward_line()
        buf.move_mark(mark, it)
        return it

    def mark_jump_to_word_edge(self, mark, buf, n, backward = False):
        it = buf.get_iter_at_mark(mark)
        if backward: it.backward_char()
        at_begin = False
        while self.is_word_char(it.get_char(), buf):
            if backward:
                if not it.backward_char():
                    at_begin = True
                    break
            else:
                it.forward_char()
        if backward and not at_begin: it.forward_char()
        buf.move_mark(mark, it)
        return it

    def mark_jump_to_indent_block_edge(self, mark, buf, n, backward = False):
        it = buf.get_iter_at_mark(mark)
        indent_level = self.iter_get_indent_level(it)
        if backward:
            it.set_line_offset(0)
            buf.move_mark(mark, it)
            it.backward_line()
            i = self.iter_get_indent_level(it)
            while (it.get_bytes_in_line() == 1) or i >= indent_level:
                buf.move_mark(mark, it)
                if not it.backward_line(): break
                i = self.iter_get_indent_level(it)
        else: # forward
            end_of_buffer = buf.get_end_iter()
            it.forward_line()
            buf.move_mark(mark, it)
            i = self.iter_get_indent_level(it)
            while it.ends_line() or i >= indent_level:
                res = it.forward_line()
                buf.move_mark(mark, it)
                if not res: break
                i = self.iter_get_indent_level(it)

    def iter_get_indent_level(self, i):
        it = i.copy()
        it.set_line_offset(0)
        while not it.ends_line() and it.get_char().isspace():
            it.forward_char()
        return it.get_line_offset()
