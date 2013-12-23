from gi.repository import Pango
import regex
from datetime import datetime

class CoreDefs:
    def __init__(self):
        self.BRACKETS = {
            '(': ')',
            '[': ']',
            '{': '}',
            '<': '>',
            '"': '"',
            "'": "'",
            '`': '`',
            '|': '|',
            '/': '/',
            '-': '-',
            '_': '_',
            }

        self.default_indent_width = 2

        self.default_font = Pango.FontDescription.from_string('Terminus 13')
        hour = datetime.now().hour
        if hour >= 6 and hour <= 10:
            self.scheme_name = 'solarizedlight'
        else:
            self.scheme_name = 'solarizeddark'

        self.word_regex = regex.compile('[a-zA-Z0-9-_]+')

    def is_word_char(self, c, buf):
        if len(c) == 0: return False
        if 'is-word-char-func' in buf.attr:
            return buf.attr['is-word-char-func'](c)
        o = ord(c.lower())
        if o >= ord('a') and o <= ord('z'): return True
        if c.isdigit(): return True
        if c in {'-', '_'}: return True
        return False
