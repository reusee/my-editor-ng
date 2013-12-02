class Selection:
    def __init__(self):
        self.emit('bind-command-key', 'v', self.toggle_char_selection)
        self.emit('bind-command-key', 'V', self.toggle_line_selection)

    def toggle_char_selection(self, view):
        if self.selection_mode != self.CHAR:
            self.selection_mode = self.CHAR
        else:
            self.enter_none_selection_mode(view)

    def toggle_line_selection(self, view):
        if self.selection_mode != self.LINE:
            self.selection_mode = self.LINE
            buf = view.get_buffer()
            it = buf.get_iter_at_mark(buf.get_insert())
            it.set_line_offset(0)
            buf.move_mark(buf.get_selection_bound(), it)
            it.forward_line()
            buf.move_mark(buf.get_insert(), it)
        else:
            self.enter_none_selection_mode(view)

    def enter_none_selection_mode(self, view):
        self.selection_mode = self.NONE
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(buf.get_insert())
        buf.place_cursor(it)
