class Mark:
    def __init__(self):
        self.emit('bind-command-key', '.', self.create_mark)
        self.emit('bind-command-key', "'", self.jump_to_mark)
        self.connect('buffer-created', lambda _, buf:
          self.setup_mark(buf))

    def setup_mark(self, buf):
        buf.attr['bookmarks'] = {}

    def create_mark(self, view):
        def wait_key(ev):
            _, val = ev.get_keyval()
            if val >= 0x20 and val <= 0x7e:
                buf = view.get_buffer()
                mark = buf.create_mark(None, buf.get_iter_at_mark(buf.get_insert()))
                buf.attr['bookmarks'][val] = mark
                print('mark', chr(val))
        return wait_key

    def jump_to_mark(self, view):
        def wait_key(ev):
            _, val = ev.get_keyval()
            if val >= 0x20 and val <= 0x7e:
                buf = view.get_buffer()
                mark = buf.attr['bookmarks'].get(val, None)
                if mark:
                    buf.place_cursor(buf.get_iter_at_mark(mark))
                view.scroll_to_mark(buf.get_insert(), 0, True, 1, 0.5)
        return wait_key
