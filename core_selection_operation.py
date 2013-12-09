class CoreSelectionOperation:
    def __init__(self):
        self.bind_command_key('d', self.cmd_delete_selection, 'delete selections')
        self.bind_command_key('c', self.cmd_change_selection, 'change selections')
        self.bind_command_key('y', self.cmd_copy_selection, 'copy selections')
        self.bind_command_key(',>', self.cmd_indent_selection, 'indent selections')
        self.bind_command_key(',<', self.cmd_dedent_selection, 'dedent selections')

    def delete_selection(self, buf):
        deleted = False
        buf.begin_user_action()
        for sel in buf.attr['selections']:
            start_iter = buf.get_iter_at_mark(sel.start)
            end_iter = buf.get_iter_at_mark(sel.end)
            if start_iter.compare(end_iter) != 0: deleted = True
            buf.delete(start_iter, end_iter)
        deleted = buf.delete_selection(True, True)
        buf.end_user_action()
        return deleted

    def copy_selection(self, buf):
        has_selection = False
        if buf.get_has_selection():
            buf.copy_clipboard(self.clipboard)
            has_selection = True
        number = 0
        for sel in buf.attr['selections']:
            start_iter = buf.get_iter_at_mark(sel.start)
            end_iter = buf.get_iter_at_mark(sel.end)
            if start_iter.compare(end_iter) == 0: continue
            has_selection = True
            if number >= len(self.extra_clipboard):
                self.extra_clipboard.append('')
            self.extra_clipboard[number] = buf.get_text(
                start_iter, end_iter, False)
            number += 1

        return has_selection

    def cmd_delete_selection(self, view):
        buf = view.get_buffer()
        def func():
            if not self.copy_selection(buf): # nothing is selected
                return False
            self.delete_selection(buf)
            self.clear_selections(buf)
            return True
        if not func():
            buf.attr['delayed-selection-operation'] = func
            return self.selection_extend_handler

    def cmd_change_selection(self, view):
        buf = view.get_buffer()
        def func():
            if not self.copy_selection(buf): # nothing is selected
                return False
            self.delete_selection(buf)
            self.enter_edit_mode()
            return True
        if not func():
            buf.attr['delayed-selection-operation'] = func
            return self.selection_extend_handler

    def cmd_copy_selection(self, view):
        buf = view.get_buffer()
        def func():
            if not self.copy_selection(buf): # nothing is selected
                return False
            self.clear_selections(buf)
            return True
        if not func():
            buf.attr['delayed-selection-operation'] = func
            return self.selection_extend_handler

    def indent_selection(self, buf, indent_string):
        for sel in buf.attr['selections'] + [buf.attr['cursor']]:
            start = buf.get_iter_at_mark(sel.start)
            end = buf.get_iter_at_mark(sel.end)
            while start.compare(end) < 0:
                if not start.starts_line():
                    start.forward_line()
                if start.compare(end) >= 0: break
                buf.begin_user_action()
                buf.insert(start, indent_string, -1)
                buf.end_user_action()
                end = buf.get_iter_at_mark(sel.end)

    def cmd_indent_selection(self, view, n):
        if n == 0: n = 1
        buf = view.get_buffer()
        indent_string = ' ' * view.get_indent_width() * n
        if not buf.get_has_selection(): # select current line
            it = buf.get_iter_at_mark(buf.get_insert())
            if not it.starts_line(): it.set_line_offset(0)
            buf.move_mark(buf.get_selection_bound(), it)
            if not it.ends_line(): it.forward_to_line_end()
            buf.move_mark(buf.get_insert(), it)
        self.indent_selection(buf, indent_string)
        self.clear_selections(buf)

    def dedent_selection(self, buf, dedent_level):
        for sel in buf.attr['selections'] + [buf.attr['cursor']]:
            start = buf.get_iter_at_mark(sel.start)
            end = buf.get_iter_at_mark(sel.end)
            if not start.starts_line(): start.forward_line()
            while start.compare(end) < 0:
                it = start.copy()
                while it.get_char() == ' ' and \
                    it.get_line_offset() < dedent_level:
                    it.forward_char()
                if it.get_line_offset() <= dedent_level:
                    buf.begin_user_action()
                    buf.delete(start, it)
                    buf.end_user_action()
                start.forward_line()
                end = buf.get_iter_at_mark(sel.end)
    def cmd_dedent_selection(self, view, n):
        if n == 0: n = 1
        buf = view.get_buffer()
        dedent_level = view.get_indent_width() * n
        if not buf.get_has_selection(): # select current line
            it = buf.get_iter_at_mark(buf.get_insert())
            if not it.starts_line(): it.set_line_offset(0)
            buf.move_mark(buf.get_selection_bound(), it)
            if not it.ends_line(): it.forward_to_line_end()
            buf.move_mark(buf.get_insert(), it)
        self.dedent_selection(buf, dedent_level)
        self.clear_selections(buf)
