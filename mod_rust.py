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
        # count indent
        it.set_line_offset(0)
        while not it.ends_line() and it.get_char().isspace():
            it.forward_char()
        indent_str = ' ' * it.get_line_offset()
        # insert
        buf.insert(start, '{\n%s\n%s}' % (indent_str, indent_str), -1)
        start.backward_line()
        start.set_line_offset(len(indent_str))
        buf.place_cursor(start)
        buf.end_user_action()
        return True
