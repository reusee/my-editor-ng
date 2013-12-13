from gi.repository import Gdk
import os

class ModStatistics:
    def __init__(self, editor):
        self.editor = editor

        editor.connect('key-pressed', self.collect_key)
        editor.connect('key-done', self.key_reseted)
        self.current_keys = []
        self.command_log_file = open(os.path.join(
            os.path.dirname(__file__),
            'command-log'), 'a+')

        editor.connect('key-handler-execute', self.collect_handler)
        self.handler_log_file = open(os.path.join(
            os.path.dirname(__file__),
            'handler-log'), 'a+')

    def collect_key(self, _, view, event):
        if self.editor.operation_mode != self.editor.COMMAND: return
        val = event.get_keyval()[1]
        if not (val >= 0x20 and val <= 0x7e): return
        self.current_keys.append(chr(val))

    def key_reseted(self, _):
        keys = ''.join(self.current_keys)
        if not keys: return
        self.current_keys.clear()
        self.command_log_file.write(keys + '\n')
        self.command_log_file.flush()

    def collect_handler(self, _, f, args):
        self.handler_log_file.write(f.__dict__['_description_'])
        self.handler_log_file.write('\t' + str(args) + '\n')
        self.handler_log_file.flush()
