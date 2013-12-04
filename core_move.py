from gi.repository import Gtk

class Move:
    def __init__(self):

        self.emit('bind-command-key', ';', self.locate_last)

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
