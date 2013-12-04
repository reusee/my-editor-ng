from gi.repository import Gtk

class Selection:
    def __init__(self, start, end):
        self.start = start # Gtk.TextMark
        self.end = end

    def transform(self, start_func, end_func):
        if start_func is not None:
            it = start_func(self.start)
        if end_func is 'func':
            start_func(self.end)
        elif end_func is 'iter':
            self.end.get_buffer().move_mark(self.end, it)
        elif end_func is not None:
            end_func(self.end)
        return self

    def get_text(self):
        buf = self.start.get_buffer()
        return buf.get_text(
            buf.get_iter_at_mark(self.start),
            buf.get_iter_at_mark(self.end), False)

    def with_copy(self, func):
        buf = self.start.get_buffer()
        sel = Selection(
            buf.create_mark(None, buf.get_iter_at_mark(self.start)),
            buf.create_mark(None, buf.get_iter_at_mark(self.end)))
        ret = func(sel)
        sel.delete()
        return ret

    def delete(self):
        buf = self.start.get_buffer()
        buf.delete_mark(self.start)
        buf.delete_mark(self.end)

class CoreSelection:
    def __init__(self):
        self.connect('buffer-created', lambda _, buf:
            self.setup_multiple_cursor(buf))
        self.connect('view-created', lambda _, view:
            view.connect('draw', self.draw_selections))

        self.emit('bind-command-key', 't', self.toggle_selection_mark)
        self.emit('bind-command-key', ', c', lambda view:
            self.clear_selections(view.get_buffer()))
        self.emit('bind-command-key', '{', lambda view:
            self.jump_selection_mark(view, backward = True))
        self.emit('bind-command-key', '}', lambda view:
            self.jump_selection_mark(view, backward = False))

    def setup_multiple_cursor(self, buf):
        buf.connect('delete-range', self.on_buffer_delete_range)
        buf.connect('insert-text', self.on_buffer_insert_text)
        buf.attr['selections'] = []
        buf.attr['skip-insert-delete-signals'] = False
        buf.attr['cursor'] = Selection(buf.get_selection_bound(), buf.get_insert())
        buf.attr['delayed-selection-operation'] = None

    def on_buffer_delete_range(self, buf, start, end):
        if self.operation_mode != self.EDIT: return
        if buf.attr['skip-insert-delete-signals']: return
        start_mark = buf.create_mark(None, start)
        end_mark = buf.create_mark(None, end)
        it = buf.get_iter_at_mark(buf.get_insert())
        start_offset_offset = start.get_offset() - it.get_offset()
        end_offset_offset = end.get_offset() - it.get_offset()
        buf.begin_user_action()
        buf.attr['skip-insert-delete-signals'] = True
        for selection in buf.attr['selections']:
            sel_start = buf.get_iter_at_mark(selection.start)
            sel_end = buf.get_iter_at_mark(selection.end)
            sel_start.set_offset(sel_start.get_offset() + start_offset_offset)
            sel_end.set_offset(sel_end.get_offset() + end_offset_offset)
            buf.delete(sel_start, sel_end)
        buf.attr['skip-insert-delete-signals'] = False
        buf.end_user_action()
        start.assign(buf.get_iter_at_mark(start_mark))
        end.assign(buf.get_iter_at_mark(end_mark))
        buf.delete_mark(start_mark)
        buf.delete_mark(end_mark)

    def on_buffer_insert_text(self, buf, location, text, length):
        if self.operation_mode != self.EDIT: return
        if buf.attr['skip-insert-delete-signals']: return
        cursor_offset = buf.get_iter_at_mark(buf.get_insert()).get_offset()
        if cursor_offset == location.get_offset():
            m = buf.create_mark(None, location)
            buf.begin_user_action()
            buf.attr['skip-insert-delete-signals'] = True
            for selection in buf.attr['selections']:
                it = buf.get_iter_at_mark(selection.start)
                buf.insert(it, text)
            buf.attr['skip-insert-delete-signals'] = False
            buf.end_user_action()
            location.assign(buf.get_iter_at_mark(m))
            buf.delete_mark(m)

    def toggle_selection_mark(self, view):
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(buf.get_insert())
        for selection in buf.attr['selections']:
            if it.compare(buf.get_iter_at_mark(selection.start)) == 0:
                buf.delete_mark(selection.start)
                buf.delete_mark(selection.end)
                buf.attr['selections'].remove(selection)
                return
        start = buf.create_mark(None, buf.get_iter_at_mark(buf.get_insert()))
        end = buf.create_mark(None, buf.get_iter_at_mark(buf.get_insert()))
        self.buffer_add_selection(buf, start, end)

    def jump_selection_mark(self, view, backward = False):
        buf = view.get_buffer()
        offset = buf.get_iter_at_mark(buf.get_insert()).get_offset()
        mark = None
        min_diff = 2 ** 32
        for selection in buf.attr['selections']:
            diff = buf.get_iter_at_mark(selection.start).get_offset() - offset
            if backward and diff < 0 and abs(diff) < min_diff:
                mark = selection.start
                min_diff = abs(diff)
            elif not backward and diff > 0 and diff < min_diff:
                mark = selection.start
                min_diff = diff
        if mark:
            buf.place_cursor(buf.get_iter_at_mark(mark))

    def clear_selections(self, buf):
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
