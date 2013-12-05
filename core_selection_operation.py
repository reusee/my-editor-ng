class CoreSelectionOperation:
    def __init__(self):
        pass

    def delete_selection(self, buf):
        deleted = False
        for sel in buf.attr['selections']:
            start_iter = buf.get_iter_at_mark(sel.start)
            end_iter = buf.get_iter_at_mark(sel.end)
            if start_iter.compare(end_iter) != 0: deleted = True
            buf.delete(start_iter, end_iter)
        deleted = buf.delete_selection(True, True)
        return deleted

    def copy_selection(self, buf):
        #TODO multiple clipboard
        if buf.get_has_selection():
            buf.copy_clipboard(self.clipboard)
            return True
        return False

    def indent_selection(self, buf, indent_string):
        for sel in buf.attr['selections'] + [buf.attr['cursor']]:
            start = buf.get_iter_at_mark(sel.start)
            end = buf.get_iter_at_mark(sel.end)
            while start.compare(end) < 0:
                if not start.starts_line():
                    start.forward_line()
                if start.compare(end) >= 0: break
                buf.insert(start, indent_string, -1)
                end = buf.get_iter_at_mark(sel.end)

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
                    buf.delete(start, it)
                start.forward_line()
                end = buf.get_iter_at_mark(sel.end)
