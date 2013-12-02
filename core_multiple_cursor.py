class MultipleCursor:
    def __init__(self):
        self.connect('buffer-created', lambda _, buf:
            self.setup_multiple_cursor(buf))

        self.emit('bind-command-key', 't', self.select_current_position)

    def setup_multiple_cursor(self, buf):
        buf.connect('delete-range', self.on_buffer_delete_range)
        buf.connect('insert-text', self.on_buffer_insert_text)
        buf.attr['selections'] = []

    def on_buffer_delete_range(self, buf, start, end):
        if self.operation_mode != self.EDIT: return
        print('delete', start.get_offset(), end.get_offset())

    def on_buffer_insert_text(self, buf, location, text, length):
        if self.operation_mode != self.EDIT: return
        print('insert', location.get_offset(), text, length)

    def select_current_position(self, view):
        buf = view.get_buffer()
        start = buf.create_mark(None, buf.get_iter_at_mark(buf.get_insert()))
        end = buf.create_mark(None, buf.get_iter_at_mark(buf.get_insert()))
        self.buffer_add_selection(buf, start, end)

    def buffer_add_selection(self, buf, start, end):
        buf.attr['selections'].append(Selection(start, end))

class Selection:
    def __init__(self, start, end):
        self.start = start # Gtk.TextMark
        self.end = end
