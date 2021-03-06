class ModPython:
    def __init__(self, editor):
        self.editor = editor
        editor.connect('language-detected', lambda _, buf, lang:
            self.setup_python(buf) if lang == 'Python' else None)

    def setup_python(self, buf):
        buf.attr['indent-width'] = 4

        self.add_line_start_abbre(buf, 'ii', 'import ')
        self.add_line_start_abbre(buf, 'dd', 'def ')
        self.add_line_start_abbre(buf, 'cc', 'class ')
        self.add_line_start_abbre(buf, 'ss', 'self.')
        self.add_line_start_abbre(buf, 'rr', 'return ')
        self.add_line_start_abbre(buf, 'pp', 'print(')

        # macros

        self.editor.bind_key_handler(buf.command_key_handler, '.c', self.comment_lines,
            'comment lines')

    def add_line_start_abbre(self, buf, s, replace):
        self.editor.add_pattern(buf, s, lambda buf:
            self.editor.insert_snippet(buf, [replace + '$1']),
            drop_key_event = True, clear_matched_text = True,
            predict = self.editor.pattern_predict_at_line_start)

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
