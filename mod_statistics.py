from gi.repository import Gdk
import os

class ModStatistics:
    def __init__(self, editor):
        self.editor = editor
        editor.connect('key-pressed', self.collect_key)
        editor.connect('key-done', self.key_reseted)
        self.current_keys = []
        self.log_file = open(os.path.join(
            os.path.dirname(__file__),
            'command-log'), 'a+')

    def collect_key(self, _, view, event):
        if self.editor.operation_mode != self.editor.COMMAND: return
        val = event.get_keyval()[1]
        if not (val >= 0x20 and val <= 0x7e): return
        self.current_keys.append(chr(val))

    def key_reseted(self, _):
        keys = ''.join(self.current_keys)
        if not keys: return
        self.current_keys.clear()
        self.log_file.write(keys + '\n')
        self.log_file.flush()
