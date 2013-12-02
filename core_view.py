from gi.repository import GtkSource, Gtk, GObject

class View:
    def __init__(self):
        self.views = []

        self.new_signal('view-created', (GtkSource.View,))
        self.connect('view-created', lambda editor, view:
            view.connect('key-press-event', self.handle_key_press))
        self.connect('destroy', lambda _: [v.freeze_notify() for v in self.views])

        self.emit('bind-command-key', ', z', self.close_view)

        self.new_signal('should-redraw', ())
        self.connect('should-redraw', lambda _: self.redraw_current_view())

        self.default_indent_width = 2

        self.connect('view-created', self.setup_buffer_switching)

    def create_view(self, buf = None):
        if buf:
            view = GtkSource.View.new_with_buffer(buf)
        else:
            view = GtkSource.View()
        self.views.append(view)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_placement(Gtk.CornerType.TOP_RIGHT)
        scroll.set_property('expand', True)
        scroll.add(view)

        setattr(view, 'attr', {})

        view.modify_font(self.default_font)
        view.set_auto_indent(True)
        view.set_indent_on_tab(True)
        view.set_indent_width(self.default_indent_width)
        view.set_insert_spaces_instead_of_tabs(True)
        view.set_smart_home_end(GtkSource.SmartHomeEndType.BEFORE)
        view.set_highlight_current_line(True)
        view.set_show_line_marks(False)
        view.set_show_line_numbers(True)
        view.set_tab_width(2)
        view.set_wrap_mode(Gtk.WrapMode.NONE)

        self.emit('view-created', view)

        return view, scroll

    def switch_to_view(self, view):
        # save cursor position of current buffer
        for v in self.views:
            if v.is_focus():
                self.save_buffer_position(v)

        view.grab_focus()
        self.emit('should-redraw')

    def close_view(self, view):
        if len(self.views) == 1: return
        scroll = view.get_parent()
        index = self.views.index(view)
        self.views.remove(view)
        index -= 1
        if index < 0: index = 0
        next_view = self.views[index]
        view.freeze_notify()
        #TODO destroy gracefully
        scroll.destroy()
        self.switch_to_view(next_view)

    def get_current_view(self):
        for v in self.views:
            if v.is_focus(): return v
        return None

    def redraw_current_view(self):
        for v in self.views:
            if v.is_focus():
                v.queue_draw()
                return
