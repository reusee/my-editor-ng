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
    def is_word_char(self, c):
        if len(c) == 0: return False
        o = ord(c.lower())
        if o >= ord('a') and o <= ord('z'): return True
        if c.isdigit(): return True
        if c in {'-', '_'}: return True
        return False
