import time
from gi.repository import GLib
import os

class ModJedi:
    def __init__(self, editor):
        self.editor = editor
        editor.connect('language-detected', lambda _, buf, lang:
          self.setup(buf) if lang == 'Python' else None)

        self.line_sep = '\u2028'
        self.line_sep_encoded = self.line_sep.encode('utf8')
        self.line_sep_length = len(self.line_sep_encoded)

        _, stdin, stdout, stderr = GLib.spawn_async(
            ['/usr/bin/env', 'python',
                os.path.join(os.path.dirname(__file__), 'mod_jedi_server.py'),],
            flags = GLib.SpawnFlags.DEFAULT,
            standard_output = True,
            standard_input = True,
            standard_error = True)

        self.stdin = GLib.IOChannel(stdin)
        self.stdin.set_encoding('UTF-8')
        self.stdin.set_line_term(self.line_sep, -1)

        stdout = GLib.IOChannel(stdout)
        stdout.set_encoding('UTF-8')
        stdout.set_line_term(self.line_sep, -1)
        self.stdout_id = GLib.io_add_watch(stdout, GLib.PRIORITY_HIGH,
            GLib.IO_IN | GLib.IO_HUP, self.process_output)

        stderr = GLib.IOChannel(stderr)
        stderr.set_encoding('UTF-8')
        stderr.set_line_term(self.line_sep, -1)
        self.stderr_id = GLib.io_add_watch(stderr, GLib.PRIORITY_HIGH,
            GLib.IO_IN | GLib.IO_HUP, self.process_error)

    def process_output(self, chan, cond):
        ret = True
        if cond & GLib.IO_IN:
            status, data, _, _ = chan.read_line()
            if status != GLib.IO_STATUS_NORMAL: return
            print(data) #TODO add to candidates
            ret = True
        if cond & GLib.IO_HUP:
            GLib.source_remove(self.stdout_id)
            ret = False
        return ret

    def process_error(self, chan, cond):
        self.editor.show_message('failed to load jedi')
        self.editor.show_message(chan.read().decode('utf8'))
        GLib.source_remove(self.stderr_id)
        return False

    def setup(self, buf):
        self.editor.show_message('jedi loaded')
        buf.attr.setdefault('completion-providers', [])
        buf.attr['completion-providers'].append(self.provide)

    def provide(self, buf, word, candidates):
        if not word:
            it = buf.get_iter_at_mark(buf.get_insert())
            if it.backward_char():
                if not it.get_char() in {'.'}: return
            else: return
        text = buf.get_text(buf.get_start_iter(),
          buf.get_end_iter(), False)
        it = buf.get_iter_at_mark(buf.get_insert())
        line = it.get_line() + 1
        column = it.get_line_offset()
        data = buf.attr['filename'] + ':' + str(line) + ':' + str(column) + ':' + text
        data = data.encode('utf8')
        self.stdin.write_chars(data, len(data))
        self.stdin.write_chars(self.line_sep_encoded, self.line_sep_length)
        self.stdin.flush()
