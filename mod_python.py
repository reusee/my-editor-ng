class ModPython:
    def __init__(self, editor):
        editor.connect('language-detected', lambda _, buf, lang:
            self.setup(buf) if lang == 'Python' else None)

    def setup(self, buf):
        buf.attr['indent-width'] = 4
