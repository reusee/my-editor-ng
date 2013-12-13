import regex

class ModRust:
    def __init__(self, editor):
        self.editor = editor

        editor.connect('language-detected', lambda _, buf, lang:
            self.setup_rust(buf) if lang == 'Rust' else None)

    def setup_rust(self, buf):
        buf.attr['is-word-char-func'] = self.is_word_char
        buf.attr['word-regex'] = regex.compile('[a-zA-Z0-9-_!]+')

        self.editor.add_pattern(buf, '{{', self.insert_braces,
            drop_key_event = True, clear_matched_text = True)

    def is_word_char(self, c):
        o = ord(c.lower())
        if o >= ord('a') and o <= ord('z'): return True
        if c.isdigit(): return True
        if c in {'-', '_', '!'}: return True
        return False

    def insert_braces(self, buf):
        it = buf.get_iter_at_mark(buf.get_insert())
        start = it.copy()
        buf.begin_user_action()
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
