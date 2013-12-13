import regex

class ModRust:
    def __init__(self, editor):
        self.editor = editor

        editor.connect('language-detected', lambda _, buf, lang:
            self.setup_rust(buf) if lang == 'Rust' else None)

    def setup_rust(self, buf):
        buf.attr['is-word-char-func'] = self.is_word_char
        buf.attr['word-regex'] = regex.compile('[a-zA-Z0-9-_!]+')

        self.editor.add_pattern(buf, '{{', lambda buf:
            self.editor.insert_snippet(buf, [
                '{$>',
                '$1$<',
                '}$2',
            ]),
            drop_key_event = True, clear_matched_text = True)

    def is_word_char(self, c):
        o = ord(c.lower())
        if o >= ord('a') and o <= ord('z'): return True
        if c.isdigit(): return True
        if c in {'-', '_', '!'}: return True
        return False
