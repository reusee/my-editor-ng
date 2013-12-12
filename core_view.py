from gi.repository import GtkSource, Gtk, GObject
import time

class CoreView:
    def __init__(self):
        self.views = []

        self.new_signal('view-created', (GtkSource.View,))
        self.connect('view-created', lambda editor, view:
            view.connect('key-press-event', self.handle_key))
        self.connect('destroy', lambda _: [v.freeze_notify() for v in self.views])

        self.bind_command_key(',z', self.close_view, 'close current view')

        self.new_signal('should-redraw', ())
        self.connect('should-redraw', lambda _: self.redraw_current_view())
        self.redraw_time = int(time.time() * 1000)

        self.default_indent_width = 2

        self.connect('view-created', self.setup_buffer_switching)

        self.bind_command_key('>', self.switch_next_buffer, 'switch to next buffer')
        self.bind_command_key('<', self.switch_prev_buffer, 'switch to previous buffer')

        # scroll
        self.bind_command_key('M', self.page_down, 'scroll page down')
        self.bind_command_key('U', self.page_up, 'scroll page up')
        self.bind_command_key('gt', lambda view: self.scroll_cursor(view, 1, 0), 'scroll cursor to screen top')
        self.bind_command_key('gb', lambda view: self.scroll_cursor(view, 1, 1), 'scroll cursor to screen bottom')
        self.bind_command_key('gm', lambda view: self.scroll_cursor(view, 1, 0.5), 'scroll cursor to middle of screen')

    def create_view(self, buf = None):
        view = GtkSource.View()
        if buf:
            view.set_buffer(buf)
        self.views.append(view)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_placement(Gtk.CornerType.TOP_RIGHT)
        scroll.set_property('expand', True)
        scroll.add(view)

        overlay = Gtk.Overlay()
        overlay.set_property('expand', True)
        overlay.add(scroll)

        setattr(view, 'attr', {})
        view.attr['wrapper'] = overlay
        view.attr['overlay'] = overlay

        view.modify_font(self.default_font)
        view.set_auto_indent(True)
        view.set_indent_on_tab(True)
        view.set_indent_width(self.default_indent_width)
        view.set_insert_spaces_instead_of_tabs(True)
        view.set_smart_home_end(GtkSource.SmartHomeEndType.BEFORE)
        view.set_show_line_marks(False)
        view.set_show_line_numbers(True)
        view.set_tab_width(2)
        view.set_wrap_mode(Gtk.WrapMode.NONE)

        view.connect('notify::buffer', lambda view, _:
            self.update_buffer_list(view.get_buffer()))
        view.connect('grab-focus', lambda view:
            self.update_buffer_list(view.get_buffer()))

        self.emit('view-created', view)

        return view

    def switch_to_view(self, view):
        # save cursor position if current focused is view
        for v in self.views:
            if v.is_focus():
                self.save_current_buffer_cursor_position(v)

        buf = view.get_buffer()
        # focus on view
        view.scroll_mark_onscreen(buf.get_insert())
        view.grab_focus()
        # restore saved buffer cursor position
        self.restore_current_buffer_cursor_position(view)
        view.scroll_to_mark(buf.get_insert(), 0, False, 0, 0)
        self.emit('should-redraw')

    def save_current_buffer_cursor_position(self, view):
        buf = view.get_buffer()
        mark = buf.create_mark(None,
            buf.get_iter_at_mark(buf.get_insert()), True)
        view.attr['buffer-cursor-position'][buf] = mark

    def restore_current_buffer_cursor_position(self, view):
        buf = view.get_buffer()
        if buf in view.attr['buffer-cursor-position']:
            mark = view.attr['buffer-cursor-position'][buf]
            buf.place_cursor(buf.get_iter_at_mark(mark))
            buf.delete_mark(mark)
            del view.attr['buffer-cursor-position'][buf]

    def close_view(self, view):
        if len(self.views) == 1: return
        wrapper = view.attr['wrapper']
        index = self.views.index(view)
        self.views.remove(view)
        index -= 1
        if index < 0: index = 0
        next_view = self.views[index]
        view.freeze_notify()
        wrapper.get_parent().remove(wrapper)
        self.switch_to_view(next_view)

    def get_current_view(self):
        for v in self.views:
            if v.is_focus(): return v
        return None

    def with_current_view(self, func):
        for v in self.views:
            if v.is_focus(): return func(v)

    def redraw_current_view(self):
        if int(time.time() * 1000) - self.redraw_time < 20:
            return
        for v in self.views:
            if v.is_focus():
                v.queue_draw()
                self.redraw_time = int(time.time() * 1000)
                return

    def setup_buffer_switching(self, _, view):
        view.attr['buffer-cursor-position'] = {}

    def switch_next_buffer(self, view):
        index = self.buffers.index(view.get_buffer())
        index += 1
        if index == len(self.buffers):
            index = 0
        self.switch_to_buffer(view, self.buffers[index])

    def switch_prev_buffer(self, view):
        index = self.buffers.index(view.get_buffer())
        index -= 1
        if index < 0:
            index = len(self.buffers) - 1
        self.switch_to_buffer(view, self.buffers[index])

    def page_down(self, view):
        alloc = view.get_allocation()
        buf = view.get_buffer()
        it = view.get_line_at_y(alloc.height - 50 + view.get_vadjustment().get_value())[0]
        buf.place_cursor(it)
        view.scroll_to_mark(buf.get_insert(), 0, True, 0, 0)

    def page_up(self, view):
        alloc = view.get_allocation()
        buf = view.get_buffer()
        it = view.get_line_at_y(view.get_vadjustment().get_value() - alloc.height + 50)[0]
        buf.place_cursor(it)
        view.scroll_to_mark(buf.get_insert(), 0, True, 0, 0)

    def scroll_cursor(self, view, x, y):
        buf = view.get_buffer()
        view.scroll_to_mark(buf.get_insert(), 0, True, x, y)
