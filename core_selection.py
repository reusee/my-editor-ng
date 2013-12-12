from gi.repository import Gtk
from core_selection_transform import Transform

class Selection:
    def __init__(self, start, end):
        self.start = start # Gtk.TextMark
        self.end = end
        self.buf = start.get_buffer()

    def get_text(self):
        buf = self.start.get_buffer()
        return buf.get_text(
            buf.get_iter_at_mark(self.start),
            buf.get_iter_at_mark(self.end), False)

class CoreSelection:
    def __init__(self):
        self.connect('buffer-created', lambda _, buf:
            self.selection_buffer_setup(buf))
        self.connect('view-created', lambda _, view:
            self.selection_view_setup(view))

        self.bind_command_key('t',
            lambda buf: self.toggle_selection_mark(buf), 'toggle selection cursor')
        self.bind_command_key(',t', self.place_selection_to_search_results,
            'toggle selection cursors at all search results')
        self.bind_command_key(',c', lambda view:
            self.clear_selections(view.get_buffer()), 'clear all selections')
        self.bind_command_key('{', lambda view:
            self.jump_selection_mark(view, backward = True), 'jump to previous selection')
        self.bind_command_key('}', lambda view:
            self.jump_selection_mark(view, backward = False), 'jump to next selection')
        self.bind_command_key('mt',
            self.toggle_selections_vertically, 'toggle selection cursors vertically')

    def selection_view_setup(self, view):
        view.connect('draw', self.draw_selections)
        indicator = Gtk.Label(
            valign = Gtk.Align.START, halign = Gtk.Align.END)
        view.attr['overlay'].add_overlay(indicator)
        view.attr['number-of-selections-indicator'] = indicator
        view.connect('notify::buffer', lambda view, _:
            self.update_number_of_selections_indicator(view.get_buffer()))

    def selection_buffer_setup(self, buf):
        buf.connect('delete-range', self.on_delete_range)
        buf.connect_after('delete-range', self.after_delete_range)
        buf.connect_after('insert-text', self.after_insert_text)

        buf.attr['selections'] = []
        buf.attr['skip-insert-delete-signals'] = False
        buf.attr['cursor'] = Selection(buf.get_selection_bound(), buf.get_insert())
        buf.attr['delayed-selection-operation'] = None
        buf.attr['current-transform'] = None
        buf.attr['last-transform'] = None

        buf.attr['delete-range-start-offset'] = 0
        buf.attr['delete-range-end-offset'] = 0

    # get offset range of deletion
    def on_delete_range(self, buf, start, end):
        if self.operation_mode != self.EDIT: return
        if buf.attr['skip-insert-delete-signals']: return
        it = buf.get_iter_at_mark(buf.get_insert())
        start_offset = start.get_offset() - it.get_offset()
        end_offset = end.get_offset() - it.get_offset()
        buf.attr['delete-range-start-offset'] = start_offset
        buf.attr['delete-range-end-offset'] = end_offset

    def after_delete_range(self, buf, start, end):
        if self.operation_mode != self.EDIT: return
        if buf.attr['skip-insert-delete-signals']: return
        start_mark = buf.create_mark(None, start)
        end_mark = buf.create_mark(None, end)
        buf.attr['skip-insert-delete-signals'] = True
        for selection in buf.attr['selections']:
            sel_start = buf.get_iter_at_mark(selection.start)
            sel_end = buf.get_iter_at_mark(selection.end)
            sel_start.set_offset(sel_start.get_offset()
                + buf.attr['delete-range-start-offset'])
            sel_end.set_offset(sel_end.get_offset()
                + buf.attr['delete-range-end-offset'])
            buf.begin_user_action()
            buf.delete(sel_start, sel_end)
            buf.end_user_action()
        buf.attr['skip-insert-delete-signals'] = False
        start.assign(buf.get_iter_at_mark(start_mark))
        end.assign(buf.get_iter_at_mark(end_mark))
        buf.delete_mark(start_mark)
        buf.delete_mark(end_mark)

    def after_insert_text(self, buf, location, text, length):
        if self.operation_mode != self.EDIT: return
        if buf.attr['skip-insert-delete-signals']: return
        cursor_offset = buf.get_iter_at_mark(buf.get_insert()).get_offset()
        if cursor_offset == location.get_offset(): # input by user
            m = buf.create_mark(None, location, True)
            buf.attr['skip-insert-delete-signals'] = True
            for selection in buf.attr['selections']:
                it = buf.get_iter_at_mark(selection.start)
                buf.begin_user_action()
                buf.insert(it, text)
                buf.end_user_action()
            buf.attr['skip-insert-delete-signals'] = False
            location.assign(buf.get_iter_at_mark(m))
            buf.delete_mark(m)

    def view_get_cursor(self, view):
        return view.get_buffer().attr['cursor']

    def toggle_selection_mark(self, buf, it = None):
        if it is None:
            it = buf.get_iter_at_mark(buf.get_insert())
        for selection in buf.attr['selections']:
            if it.compare(buf.get_iter_at_mark(selection.start)) == 0:
                buf.delete_mark(selection.start)
                buf.delete_mark(selection.end)
                buf.attr['selections'].remove(selection)
                # update indicators
                self.update_number_of_selections_indicator(buf)
                return
        start = buf.create_mark(None, it)
        end = buf.create_mark(None, it)
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
        buf.place_cursor(buf.get_iter_at_mark(buf.get_insert()))
        buf.attr['selections'].clear()
        # update indicators
        self.update_number_of_selections_indicator(buf)

    def buffer_add_selection(self, buf, start, end):
        buf.attr['selections'].append(Selection(start, end))
        self.update_number_of_selections_indicator(buf)

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

    def toggle_selections_vertically(self, buf, n):
        if n == 0: n = 1
        offset = buf.get_iter_at_mark(buf.get_insert()).get_line_offset()
        for _ in range(n):
            if buf.get_iter_at_mark(buf.get_insert()).get_line_offset() == offset:
                self.toggle_selection_mark(buf)
            Transform(
                (self.mark_jump_relative_line_with_preferred_offset, 1),
                ('iter',), 'cursor').apply(buf)

    def place_selection_to_search_results(self, buf):
        self.clear_selections(buf)
        it = buf.get_start_iter()
        tag = buf.attr['search-result-tag']
        while it.forward_to_tag_toggle(tag):
            if it.ends_tag(tag): continue
            self.toggle_selection_mark(buf, it)

    def update_number_of_selections_indicator(self, buf):
        n = len(buf.attr['selections'])
        for view in self.views:
            if view.get_buffer() != buf: continue
            indicator = view.attr['number-of-selections-indicator']
            if n == 0:
                indicator.hide()
                continue
            indicator.set_markup('<span foreground="yellow">'
                + str(n) + ' Selections</span>')
            indicator.show()
