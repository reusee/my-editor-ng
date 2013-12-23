from gi.repository import Gtk, GtkSource
import os

class CoreStatus:
    def __init__(self):
        # redraw
        self.connect('view-created', lambda _, view:
            view.connect('draw', self.draw_status))

        # relative numer
        self.connect('view-created', lambda _, view:
            self.setup_relative_line_number(view))

    def draw_status(self, view, cr):
        if not view.is_focus(): return
        rect = view.get_allocation()

        # current line and column
        buf = view.get_buffer()
        cursor_rect = view.get_iter_location(buf.get_iter_at_mark(buf.get_insert()))
        if buf.get_modified():
            cr.set_source_rgb(0, 0.3, 0.5)
        else:
            cr.set_source_rgb(0, 0.5, 0)
        if self.operation_mode == self.COMMAND:
            cr.set_line_width(2)
        else:
            cr.set_line_width(4)
        x, y = view.buffer_to_window_coords(Gtk.TextWindowType.WIDGET,
            cursor_rect.x, cursor_rect.y)
        cr.move_to(x, 0)
        cr.line_to(x, rect.height)
        cr.stroke()
        cr.set_line_width(1)
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.move_to(0, y + cursor_rect.height)
        cr.line_to(rect.width, y + cursor_rect.height)
        cr.stroke()

    def setup_relative_line_number(self, view):
        gutter = view.get_gutter(Gtk.TextWindowType.LEFT)
        renderer = RelativeNumberRenderer(view)
        gutter.insert(renderer, 0)
        view.attr['_relative_line_number_renderer'] = renderer

class RelativeNumberRenderer(GtkSource.GutterRendererText):
    def __init__(self, view):
        GtkSource.GutterRendererText.__init__(self)
        self.set_alignment(1, 1)
        self.view = view

    def do_query_data(self, start, end, state):
        if not self.view.is_focus():
            self.set_text('', -1)
            self.set_size(0)
            return
        buf = start.get_buffer()
        current_line = buf.get_iter_at_mark(buf.get_insert()).get_line()
        text = str(abs(start.get_line() - current_line))
        self.set_text(text, -1)
        self.set_size(30)
