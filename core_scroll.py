class Scroll:
    def __init__(self):
        self.emit('bind-command-key', 'M', self.page_down)
        self.emit('bind-command-key', 'U', self.page_up)
        self.emit('bind-command-key', 'z t', lambda view: self.scroll_cursor(view, 1, 0))
        self.emit('bind-command-key', 'z b', lambda view: self.scroll_cursor(view, 1, 1))
        self.emit('bind-command-key', 'z z', lambda view: self.scroll_cursor(view, 1, 0.5))

    def page_down(self, view):
        alloc = view.get_allocation()
        buf = view.get_buffer()
        it = view.get_line_at_y(alloc.height - 50 + view.get_vadjustment().get_value())[0]
        self.move_mark(buf, it)
        view.scroll_to_mark(buf.get_insert(), 0, True, 0, 0)

    def page_up(self, view):
        alloc = view.get_allocation()
        buf = view.get_buffer()
        it = view.get_line_at_y(view.get_vadjustment().get_value() - alloc.height + 50)[0]
        self.move_mark(buf, it)
        view.scroll_to_mark(buf.get_insert(), 0, True, 0, 0)

    def scroll_cursor(self, view, x, y):
        buf = view.get_buffer()
        view.scroll_to_mark(buf.get_insert(), 0, True, x, y)
