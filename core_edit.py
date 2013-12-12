from gi.repository import Gtk, Gdk
from core_selection_transform import Transform

class CoreEdit:
    def __init__(self):

        self.bind_command_key('p', self.paste, 'paste')
        self.bind_command_key(',p', self.paste_at_next_line, 'paste as next line')

        self.bind_command_key('u', self.undo, 'undo')
        self.bind_command_key('Y', self.redo, 'redo')

        self.bind_command_key('o', self.newline_below, 'insert newline below')
        self.bind_command_key('O', self.newline_above, 'insert newline above')
        self.bind_command_key('a', self.append_current_pos, 'append')
        self.bind_command_key('A', self.append_current_line, 'append at line start')
        self.bind_command_key('x', self.delete_current_char, 'delete current char')
        self.bind_command_key('I', self.enter_edit_mode_at_first_char, 'insert at first non-space char')
        self.bind_command_key('C', self.change_from_first_char, 'change from first non-space char')

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.extra_clipboard = []

        self.bind_edit_key([Gdk.KEY_BackSpace], self.backspace_with_dedent, 'backspace')

        # macros
        self.bind_command_key('.j', lambda view, n:
            self.feed_keys(view, 'b1' + str(n) + "ggdd'1,p"),
            'move line n to next line')
        self.bind_command_key('.k', lambda view, n:
            self.feed_keys(view, 'b1dd' + str(n) + "ggp'1"),
            'move current line to line n')
        self.bind_command_key('.l', lambda view, n:
            self.feed_keys(view, 'b1' + str(n) + "ggyy'1,p"),
            'copy line n to next line')

    def paste(self, view, n):
        buf = view.get_buffer()
        if n == 0: n = 1
        for _ in range(n):
            buf.paste_clipboard(self.clipboard, None, True)
        for i, sel in enumerate(buf.attr['selections'][:len(self.extra_clipboard)]):
            start_iter = buf.get_iter_at_mark(sel.start)
            end_iter = buf.get_iter_at_mark(sel.end)
            buf.begin_user_action()
            buf.delete(start_iter, end_iter)
            for _ in range(n):
                buf.insert(start_iter, self.extra_clipboard[i], -1)
            buf.end_user_action()
        self.clear_selections(buf)

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
        else:
            self.show_message('no undo action')

    def redo(self, view):
        buf = view.get_buffer()
        if buf.can_redo():
            buf.redo()
            buf.place_cursor(buf.get_iter_at_mark(buf.get_insert()))
            view.scroll_to_mark(buf.get_insert(), 0, True, 1, 0.5)

    def newline_above(self, view):
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(buf.get_insert())
        it.set_line_offset(0)
        line_end_iter = it.copy()
        if not line_end_iter.ends_line(): line_end_iter.forward_to_line_end()
        st = it.copy()
        while st.get_char() == ' ' and st.compare(line_end_iter) < 0:
            st.forward_char()
        indent_level = st.get_line_offset()
        buf.begin_user_action()
        buf.insert(it, '\n')
        it.backward_line()
        buf.insert(it, ' ' * indent_level)
        buf.end_user_action()
        buf.place_cursor(it)
        self.enter_edit_mode(buf)

    def newline_below(self, view):
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(buf.get_insert())
        if not it.ends_line(): it.forward_to_line_end()
        st = it.copy()
        st.set_line_offset(0)
        while st.get_char() == ' ' and st.compare(it) < 0:
            st.forward_char()
        buf.begin_user_action()
        buf.insert(it, '\n' + ' ' * st.get_line_offset())
        buf.end_user_action()
        buf.place_cursor(it)
        self.enter_edit_mode(buf)

    def append_current_line(self, buf):
        Transform(
            (self.mark_jump_to_line_end, 0),
            ('iter',), 'cursor').apply(buf)
        self.enter_edit_mode(buf)

    def append_current_pos(self, buf):
        Transform(
            (self.mark_jump_relative_char, 1),
            ('iter',), 'cursor').apply(buf)
        self.enter_edit_mode(buf)

    def delete_current_char(self, view):
        buf = view.get_buffer()
        start = buf.get_iter_at_mark(buf.get_insert())
        end = start.copy()
        end.forward_char()
        buf.move_mark(buf.get_insert(), start)
        buf.move_mark(buf.get_selection_bound(), end)
        buf.copy_clipboard(self.clipboard)
        buf.begin_user_action()
        buf.delete(start, end)
        buf.end_user_action()

    def enter_edit_mode_at_first_char(self, view):
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(buf.get_insert())
        it.set_line_offset(0)
        while it.get_char().isspace() and not it.ends_line():
            it.forward_char()
        buf.place_cursor(it)
        self.enter_edit_mode(buf)

    def change_from_first_char(self, view):
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(buf.get_insert())
        it.set_line_offset(0)
        while it.get_char().isspace() and not it.ends_line():
            it.forward_char()
        line_end = it.copy()
        if not line_end.ends_line(): it.forward_to_line_end()
        buf.begin_user_action()
        buf.delete(it, line_end)
        buf.end_user_action()
        buf.place_cursor(it)
        self.enter_edit_mode(buf)

    def backspace_with_dedent(self, view):
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(buf.get_insert())
        end = it.copy()
        nonspace_deleted = False
        if it.backward_char():
            if it.get_char() != ' ': nonspace_deleted = True
            buf.begin_user_action()
            buf.delete(it, end)
            buf.end_user_action()
        if nonspace_deleted: return
        indent_width = self.default_indent_width
        if 'indent-width' in buf.attr:
            indent_width = buf.attr['indent-width']
        i = it.get_line_offset() % indent_width
        while i != 0:
            if it.backward_char() and it.get_char() == ' ':
                buf.begin_user_action()
                buf.delete(it, end)
                buf.end_user_action()
                i -= 1
            else:
                break
