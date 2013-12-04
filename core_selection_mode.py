class CoreSelectionMode:
    def __init__(self):
        self.emit('bind-command-key', 'v', self.toggle_char_selection)
        self.connect('buffer-created', lambda _, buf:
            self.setup_selection_mode(buf))

    def setup_selection_mode(self, buf):
        buf.attr['selection-mode-anchor'] = None
        buf.connect('notify::cursor-position', lambda buf, _:
            self.ensure_selection_of_mode(buf))

    def toggle_char_selection(self, view):
        if self.selection_mode != self.CHAR:
            self.selection_mode = self.CHAR
            buf = view.get_buffer()
            buf.attr['selection-mode-anchor'] = buf.create_mark(None,
                buf.get_iter_at_mark(buf.get_insert()))
        else:
            self.enter_none_selection_mode(view)

    def enter_none_selection_mode(self, view):
        self.selection_mode = self.NONE
        buf = view.get_buffer()
        buf.delete_mark(buf.attr['selection-mode-anchor'])
        buf.attr['selection-mode-anchor'] = None
        it = buf.get_iter_at_mark(buf.get_insert())
        buf.place_cursor(it)

    def ensure_selection_of_mode(self, buf):
        if not buf.attr['selection-mode-anchor']: return
        anchor_iter = buf.get_iter_at_mark(buf.attr['selection-mode-anchor'])
        if self.selection_mode == self.CHAR:
            buf.move_mark(buf.get_selection_bound(), anchor_iter)
