class ModStatistics:
    def __init__(self, editor):
        editor.connect('key-pressed', self.collect_key)
        editor.connect('key-done', self.key_reseted)
        self.current_keys = []

    def collect_key(self, _, ev):
        print(ev.get_keyval()[1])

    def key_reseted(self, _):
        print('reset')
