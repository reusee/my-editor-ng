class ModPython:
    def __init__(self, editor):
        self.editor = editor
        editor.connect('language-detected', lambda _, buf, lang:
            self.setup_python(buf) if lang == 'Python' else None)
        editor.connect('buffer-created', lambda _, buf:
            self.setup(buf) if 'language' in buf.attr
            and buf.attr['language'] == 'Python' else None)

        # macros
        self.command_keymap = {}
        editor.bind_key_handler(self.command_keymap, '.fv', lambda view:
            editor.feed_keys(view, 'vmwvt(v%vl'),
            'select current function call')
        editor.bind_key_handler(self.command_keymap, '.fi', lambda view, buf: [
            editor.feed_keys(view, 'f(%i'),
            buf.begin_user_action(),
            buf.insert(buf.get_iter_at_mark(buf.get_insert()),
                ', ', -1),
            buf.end_user_action(),
            ], 'insert argument to current function')

        editor.bind_key_handler(self.command_keymap, '.c', self.comment_lines,
            'comment lines')

    def setup_python(self, buf):
        buf.attr['indent-width'] = 4
        buf.attr['language'] = 'Python'
        buf.command_key_handler.insert(0, self.command_keymap)

    def setup(self, buf):
        self.add_line_start_abbre(buf, 'ii', 'import ')
        self.add_line_start_abbre(buf, 'dd', 'def ')
        self.add_line_start_abbre(buf, 'cc', 'class ')
        self.add_line_start_abbre(buf, 'ss', 'self.')
        self.add_line_start_abbre(buf, 'rr', 'return ')
        self.add_line_start_abbre(buf, 'pp', 'print(')

    def add_line_start_abbre(self, buf, s, replace):
        def callback(buf):
            it = buf.get_iter_at_mark(buf.get_insert())
            for _ in range(len(s) - 1): it.backward_char()
            start = it.copy()
            start.set_line_offset(0)
            while start.compare(it) < 0 and not start.ends_line():
                if start.get_char().isspace(): start.forward_char()
                else: break
            if start.compare(it) != 0: return
            buf.begin_user_action()
            buf.delete(start, buf.get_iter_at_mark(buf.get_insert()))
            buf.insert(start, replace, -1)
            buf.end_user_action()
            return True
        self.editor.add_pattern(buf, s, callback)

    def comment_lines(self, buf, n):
        it = buf.get_iter_at_mark(buf.get_insert())
        m = buf.create_mark(None, it, True)
        buf.begin_user_action()
        n += 1
        for _ in range(n):
            buf.insert(it, '#', -1)
            it.forward_line()
        buf.end_user_action()
        buf.place_cursor(buf.get_iter_at_mark(m))
        buf.delete_mark(m)
