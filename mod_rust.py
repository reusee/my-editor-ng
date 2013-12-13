class ModRust:
    def __init__(self, editor):
        self.editor = editor

        editor.connect('language-detected', lambda _, buf, lang:
            self.setup_rust(buf) if lang == 'Rust' else None)

    def setup_rust(self, buf):
        buf.attr['language'] = 'Rust'

        self.editor.add_pattern(buf, '{{', self.insert_braces)

    def insert_braces(self, buf):
        it = buf.get_iter_at_mark(buf.get_insert())
        start = it.copy()
        start.backward_char()
        buf.begin_user_action()
        buf.delete(start, it)
        buf.insert(start, '{\n\n}\n', -1)
        start.backward_line()
        start.backward_line()
        buf.place_cursor(start)
        buf.end_user_action()
        return True
