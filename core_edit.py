from gi.repository import Gtk, Gdk

class Edit:
    def __init__(self):

        self.emit('bind-command-key', 'i', self.enter_edit_mode)
        self.emit('bind-command-key', 'I', self.enter_edit_mode_at_first_char)

        self.emit('bind-command-key', 'c', self.change_selection)
        self.emit('bind-command-key', 'C', self.change_from_first_char)
        self.emit('bind-command-key', 'y', self.copy_selection)
        self.emit('bind-command-key', 'p', self.paste)
        self.emit('bind-command-key', ', p', self.paste_at_next_line)

        self.emit('bind-command-key', ', >', self.indent_selection)
        self.emit('bind-command-key', ', <', self.dedent_selection)

        self.emit('bind-command-key', 'u', self.undo)
        self.emit('bind-command-key', 'Y', self.redo)

        self.emit('bind-command-key', 'o', self.newline_below)
        self.emit('bind-command-key', 'O', self.newline_above)
        self.emit('bind-command-key', 'a', self.append_current_pos)
        self.emit('bind-command-key', 'A', self.append_current_line)
        self.emit('bind-command-key', 'x', self.delete_current_char)

        self.emit('bind-edit-key', 'k d', self.enter_command_mode)

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        self.edit_key_handler[Gdk.KEY_BackSpace] = self.backspace_with_dedent

    def change_selection(self, view):
        buf = view.get_buffer()
        if self._delete_selection(view, buf.get_selection_bound(), buf.get_insert()):
            self.enter_none_selection_mode(view)
            self.enter_edit_mode()
        else:
            return self.make_text_object_handler(self._change_selection)

    def _change_selection(self, view, start_mark, end_mark):
        buf = view.get_buffer()
        self._delete_selection(view, start_mark, end_mark)
        if start_mark == buf.get_selection_bound():
            self.enter_edit_mode()

    def copy_selection(self, view):
        buf = view.get_buffer()
        if 'copy-mark' not in buf.attr:
            buf.attr['copy-mark'] = buf.create_mark(None, buf.get_iter_at_mark(buf.get_insert()))
        else:
            buf.move_mark(buf.attr['copy-mark'], buf.get_iter_at_mark(buf.get_insert()))
        if not self._copy_selection(view, None, None):
            return self.make_text_object_handler(self._copy_selection)

    def _copy_selection(self, view, _start_mark, _end_mark):
        buf = view.get_buffer()
        if buf.get_has_selection():
            buf.copy_clipboard(self.clipboard)
            self.enter_none_selection_mode(view)
            buf.place_cursor(buf.get_iter_at_mark(buf.attr['copy-mark']))
            return True

    def paste(self, view):
        buf = view.get_buffer()
        buf.paste_clipboard(self.clipboard, None, True)

    def paste_at_next_line(self, view):
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(buf.get_insert())
        it.forward_line()
        buf.paste_clipboard(self.clipboard, it, True)

    def undo(self, view):
        buf = view.get_buffer()
        if buf.can_undo():
            buf.undo()
            buf.place_cursor(buf.get_iter_at_mark(buf.get_insert()))
            view.scroll_to_mark(buf.get_insert(), 0, True, 1, 0.5)

    def redo(self, view):
        buf = view.get_buffer()
        if buf.can_redo():
            buf.redo()
            buf.place_cursor(buf.get_iter_at_mark(buf.get_insert()))
            view.scroll_to_mark(buf.get_insert(), 0, True, 1, 0.5)

    def newline_above(self, view):
        buf = view.get_buffer()
        buf.begin_user_action()
        it = buf.get_iter_at_mark(buf.get_insert())
        it.set_line_offset(0)
        line_end_iter = it.copy()
        if not line_end_iter.ends_line(): line_end_iter.forward_to_line_end()
        st = it.copy()
        while st.get_char() == ' ' and st.compare(line_end_iter) < 0:
            st.forward_char()
        indent_level = st.get_line_offset()
        buf.insert(it, '\n')
        it.backward_line()
        buf.insert(it, ' ' * indent_level)
        buf.end_user_action()
        buf.place_cursor(it)
        self.enter_edit_mode()

    def newline_below(self, view):
        buf = view.get_buffer()
        buf.begin_user_action()
        it = buf.get_iter_at_mark(buf.get_insert())
        if not it.ends_line(): it.forward_to_line_end()
        st = it.copy()
        st.set_line_offset(0)
        while st.get_char() == ' ' and st.compare(it) < 0:
            st.forward_char()
        buf.insert(it, '\n' + ' ' * st.get_line_offset())
        buf.end_user_action()
        buf.place_cursor(it)
        self.enter_edit_mode()

    def append_current_line(self, view):
        self.move_to_line_end(view)
        self.enter_edit_mode()

    def append_current_pos(self, view):
        self.move_char(view, 1)
        self.enter_edit_mode()

    def delete_current_char(self, view):
        buf = view.get_buffer()
        buf.begin_user_action()
        start = buf.get_iter_at_mark(buf.get_insert())
        end = start.copy()
        end.forward_char()
        buf.move_mark(buf.get_insert(), start)
        buf.move_mark(buf.get_selection_bound(), end)
        buf.copy_clipboard(self.clipboard)
        buf.delete(start, end)
        buf.end_user_action()

    def enter_edit_mode_at_first_char(self, view):
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(buf.get_insert())
        it.set_line_offset(0)
        while it.get_char().isspace() and not it.ends_line():
            it.forward_char()
        buf.place_cursor(it)
        self.enter_edit_mode()

    def change_from_first_char(self, view):
        buf = view.get_buffer()
        buf.begin_user_action()
        it = buf.get_iter_at_mark(buf.get_insert())
        it.set_line_offset(0)
        while it.get_char().isspace() and not it.ends_line():
            it.forward_char()
        line_end = it.copy()
        if not line_end.ends_line(): it.forward_to_line_end()
        buf.delete(it, line_end)
        buf.end_user_action()
        buf.place_cursor(it)
        self.enter_edit_mode()

    def indent_selection(self, view, n):
        buf = view.get_buffer()
        if n == 0: n = 1
        indent_string = ' ' * view.get_indent_width() * n
        if not buf.get_has_selection(): # select current line
            it = buf.get_iter_at_mark(buf.get_insert())
            if not it.starts_line(): it.set_line_offset(0)
            buf.move_mark(buf.get_selection_bound(), it)
            if not it.ends_line(): it.forward_to_line_end()
            buf.move_mark(buf.get_insert(), it)
        start, end = buf.get_selection_bounds()
        while start.compare(end) < 0:
            if not start.starts_line():
                start.forward_line()
            if start.compare(end) >= 0: break
            buf.insert(start, indent_string, -1)
            _, end = buf.get_selection_bounds()
        buf.place_cursor(buf.get_iter_at_mark(buf.get_insert()))
        self.selection_mode = self.NONE

    def dedent_selection(self, view, n):
        buf = view.get_buffer()
        if n == 0: n = 1
        dedent_level = view.get_indent_width() * n
        if not buf.get_has_selection(): # select current line
            it = buf.get_iter_at_mark(buf.get_insert())
            if not it.starts_line(): it.set_line_offset(0)
            buf.move_mark(buf.get_selection_bound(), it)
            if not it.ends_line(): it.forward_to_line_end()
            buf.move_mark(buf.get_insert(), it)
        start, end = buf.get_selection_bounds()
        if not start.starts_line():
            start.forward_line()
        while start.compare(end) < 0:
            it = start.copy()
            while it.get_char() == ' ' and it.get_line_offset() < dedent_level:
                it.forward_char()
            if it.get_line_offset() <= dedent_level:
                buf.delete(start, it)
            start.forward_line()
            _, end = buf.get_selection_bounds()
        buf.place_cursor(buf.get_iter_at_mark(buf.get_insert()))
        self.selection_mode = self.NONE

    def backspace_with_dedent(self, view):
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(buf.get_insert())
        end = it.copy()
        nonspace_deleted = False
        if it.backward_char():
            if it.get_char() != ' ': nonspace_deleted = True
            buf.delete(it, end)
        if nonspace_deleted: return
        indent_width = self.default_indent_width
        if 'indent-width' in buf.attr:
            indent_width = buf.attr['indent-width']
        i = it.get_line_offset() % indent_width
        while i != 0:
            if it.backward_char() and it.get_char() == ' ':
                buf.delete(it, end)
                i -= 1
            else:
                break
