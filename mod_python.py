class ModPython:
    def __init__(self, editor):
        self.editor = editor
        editor.connect('language-detected', lambda _, buf, lang:
            self.setup_python(buf) if lang == 'Python' else None)
        editor.connect('buffer-created', lambda _, buf:
            self.setup(buf) if 'language' in buf.attr
            and buf.attr['language'] == 'Python' else None)

    def setup_python(self, buf):
        buf.attr['indent-width'] = 4
        buf.attr['language'] = 'Python'

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
