from gi.repository import Gtk

class MultipleCursor:
    def __init__(self):
        self.connect('buffer-created', lambda _, buf:
            self.setup_multiple_cursor(buf))
        self.connect('view-created', lambda _, view:
            view.connect('draw', self.draw_selections))

        self.emit('bind-command-key', 't', self.select_current_position)
        self.emit('bind-command-key', ', c', self.clear_selections)

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

    def clear_selections(self, view):
        buf = view.get_buffer()
        buf.attr['selections'].clear()

    def buffer_add_selection(self, buf, start, end):
        buf.attr['selections'].append(Selection(start, end))

    def draw_selections(self, view, cr):
        if not view.is_focus(): return
        buf = view.get_buffer()
        for selection in buf.attr['selections']:
            cr.set_source_rgb(1, 0, 0)
            start_rect = view.get_iter_location(
                buf.get_iter_at_mark(selection.start))
            x, y = view.buffer_to_window_coords(Gtk.TextWindowType.WIDGET,
                start_rect.x, start_rect.y)
            cr.move_to(x, y)
            cr.set_line_width(2)
            cr.line_to(x + 6, y)
            cr.stroke()
            cr.move_to(x, y)
            cr.set_line_width(1)
            cr.line_to(x, y + start_rect.height)
            cr.stroke()
            cr.set_source_rgb(0, 1, 0)
            end_rect = view.get_iter_location(
                buf.get_iter_at_mark(selection.end))
            x, y = view.buffer_to_window_coords(Gtk.TextWindowType.WIDGET,
                end_rect.x, end_rect.y)
            cr.move_to(x, y)
            cr.set_line_width(1)
            cr.line_to(x, y + end_rect.height)
            cr.stroke()
            cr.move_to(x, y + end_rect.height)
            cr.set_line_width(2)
            cr.line_to(x - 6, y + end_rect.height)
            cr.stroke()

class Selection:
    def __init__(self, start, end):
        self.start = start # Gtk.TextMark
        self.end = end
