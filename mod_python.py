class ModPython:
    def __init__(self, editor):
        self.editor = editor
        editor.connect('language-detected', lambda _, buf, lang:
            self.setup(buf) if lang == 'Python' else None)

    def setup(self, buf):
        buf.attr['indent-width'] = 4

        self.define_abbreviation('dd', 'def ', self.at_line_start)
        self.define_abbreviation('ii', 'import ', self.at_line_start)
        self.define_abbreviation('cc', 'class ', self.at_line_start)
        self.define_abbreviation('ss', 'self.', self.at_line_start)
        self.define_abbreviation('if', 'if ', self.at_line_start)
        self.define_abbreviation('ff', 'for ', self.at_line_start)
        self.define_abbreviation('ww', 'while ', self.at_line_start)
        self.define_abbreviation('pp', 'print(', self.at_line_start)
        self.define_abbreviation('rr', 'return ', self.at_line_start)

    def at_line_start(self, buf):
        return all(self.iter_to_line_start(buf.get_iter_at_mark(buf.get_insert()),
            lambda c: c.isspace())) or buf.get_iter_at_mark(buf.get_insert()).get_offset() == 0

    def define_abbreviation(self, cmd, replace, predict):
        def f(buf):
            insert = cmd
            if predict(buf):
                insert = replace
            buf.insert(buf.get_iter_at_mark(buf.get_insert()),
                insert, -1)
        self.editor.emit('bind-edit-key', ' '.join(c for c in cmd), f)

    def iter_to_line_start(self, it, func):
        start = it.copy()
        start.set_line_offset(0)
        it.backward_char()
        while it.compare(start) >= 0:
            yield func(it.get_char())
            it.backward_char()
