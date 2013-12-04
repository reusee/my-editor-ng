from gi.repository import Gtk

class Move:
    def __init__(self):

        self.emit('bind-command-key', '%', self.move_to_matching_bracket)
        self.emit('bind-command-key', ';', self.locate_last)
        self.emit('bind-command-key', 'G', self.move_to_end)
        self.emit('bind-command-key', 'r', self.move_to_line_end)
        self.emit('bind-command-key', 'R', self.move_to_line_start)
        self.emit('bind-command-key', '[', lambda view: self.move_to_empty_line(view, backward = True))
        self.emit('bind-command-key', ']', lambda view: self.move_to_empty_line(view))

        self.connect('buffer-created',
            lambda _, buf: buf.connect('notify::cursor-position',
              lambda buf, _: self.update_preferred_line_offset(buf)))

    def update_preferred_line_offset(self, buf):
        if buf.attr.get('freeze', False): return
        buf.attr['preferred-line-offset'] = buf.get_iter_at_mark(buf.get_insert()).get_line_offset()

    def move_mark(self, buf, it):
        if self.selection_mode == self.NONE:
            buf.place_cursor(it)
        elif self.selection_mode == self.LINE:
            cur = buf.get_iter_at_mark(buf.get_insert())
            if cur.compare(it) == -1: # forward
                if not it.starts_line(): it.forward_line()
            else: # backward
                if not it.starts_line(): it.set_line_offset(0)
            buf.move_mark(buf.get_insert(), it)
        else:
            buf.move_mark(buf.get_insert(), it)

    def locate_last(self, view):
        if 'last_locate_func' in view.attr:
            view.attr['last_locate_func'](view)

    def move_to_end(self, view):
        buf = view.get_buffer()
        self.move_mark(buf, buf.get_end_iter())
        view.scroll_mark_onscreen(buf.get_insert())

    def move_to_line_start(self, view):
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(buf.get_insert())
        if it.starts_line(): # already at line start
            while it.get_char().isspace() and not it.ends_line():
                it.forward_char()
        else:
            it.set_line_offset(0)
        self.move_mark(buf, it)
        view.scroll_mark_onscreen(buf.get_insert())

    def move_to_line_end(self, view):
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(buf.get_insert())
        if not it.ends_line():
            it.forward_to_line_end()
        self.move_mark(buf, it)
        view.scroll_mark_onscreen(buf.get_insert())

    def move_to_empty_line(self, view, backward = False):
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(buf.get_insert())
        if backward: f = it.backward_line
        else: f = it.forward_line
        ret = f()
        while ret and it.get_bytes_in_line() != 1:
            ret = f()
        self.move_mark(buf, it)
        view.scroll_mark_onscreen(buf.get_insert())

    def move_to_matching_bracket(self, view):
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(buf.get_insert())

        start = it.get_char()
        is_left = False
        match = None
        for left, right in self.BRACKETS.items():
            if left == right: continue
            if left == start:
                is_left = True
                match = right
                break
            elif right == start:
                match = left
                break
        if not match: it.backward_char()

        start = it.get_char()
        is_left = False
        match = None
        for left, right in self.BRACKETS.items():
            if left == right: continue
            if left == start:
                is_left = True
                match = right
                break
            elif right == start:
                match = left
                break
        if not match: return

        balance = 0
        found = False
        if is_left: it.forward_char()
        else: it.backward_char()
        while True:
            c = it.get_char()
            if c == match and balance == 0: # found
                found = True
                break
            elif c == match:
                balance -= 1
            elif c == start:
                balance += 1
            if is_left:
                if not it.forward_char(): break
            else:
                if not it.backward_char(): break
        if not found: return

        self.move_mark(buf, it)
        view.scroll_mark_onscreen(buf.get_insert())
