class ModStatistics:
    def __init__(self, editor):
        editor.connect('key-pressed', self.collect_key)
        editor.connect('key-done', self.key_reseted)
        self.current_keys = []

    def collect_key(self, _, view, keyval):
        #print(chr(keyval))
        pass

    def key_reseted(self, _):
        #print('reset')
        pass
