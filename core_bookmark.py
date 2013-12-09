class Bookmark:
    def __init__(self):
        self.bind_command_key('b', self.create_mark, 'create bookmark')
        self.bind_command_key("'", self.jump_to_mark, 'jump to bookmark')
        self.connect('buffer-created', lambda _, buf:
          self.setup_mark(buf))

        self.bind_command_key('ge', lambda buf:
            buf.place_cursor(buf.get_iter_at_mark(
                buf.attr['mark-last-leave-edit'])), 'jump to last edit place')

    def setup_mark(self, buf):
        buf.attr['bookmarks'] = {}

        buf.attr['mark-last-leave-edit'] = buf.create_mark(None,
            buf.get_iter_at_mark(buf.get_insert()), True)
        self.connect('entered-command-mode', lambda _:
            buf.move_mark(buf.attr['mark-last-leave-edit'],
                buf.get_iter_at_mark(buf.get_insert())))

    def create_mark(self, view):
        def wait_key(keyval):
            if keyval >= 0x20 and keyval <= 0x7e:
                buf = view.get_buffer()
                mark = buf.create_mark(None,
                    buf.get_iter_at_mark(buf.get_insert()), True)
                buf.attr['bookmarks'][keyval] = mark
                print('mark', chr(keyval))
        return wait_key

    def jump_to_mark(self, view):
        def wait_key(keyval):
            if keyval >= 0x20 and keyval <= 0x7e:
                buf = view.get_buffer()
                mark = buf.attr['bookmarks'].get(keyval, None)
                if mark:
                    buf.place_cursor(buf.get_iter_at_mark(mark))
                view.scroll_to_mark(buf.get_insert(), 0, True, 1, 0.5)
        return wait_key

    #TODO auto bookmarks
