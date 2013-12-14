from gi.repository import GLib
import ctypes
import jedi

class Main:
    def __init__(self):
        self.line_sep = '\u2028'
        self.line_sep_encoded = self.line_sep.encode('utf8')
        self.line_sep_length = len(self.line_sep_encoded)

        stdin = GLib.IOChannel(0)
        stdin.set_encoding('UTF-8')
        stdin.set_line_term(self.line_sep, -1)
        self.stdin_id = GLib.io_add_watch(stdin, GLib.PRIORITY_HIGH,
            GLib.IO_IN | GLib.IO_HUP, self.process_stdin)

        self.stdout = GLib.IOChannel(1)
        self.stdout.set_encoding('UTF-8')
        self.stdout.set_line_term(self.line_sep, -1)

    def process_stdin(self, chan, cond):
        ret = True
        if cond & GLib.IO_IN:
            ret = True
            status, data, _, _ = chan.read_line()
            if status != GLib.IO_STATUS_NORMAL: return
            serial, path, line, column, text = data.split(':', 4)
            script = jedi.Script(
                source = text,
                line = int(line),
                column = int(column),
                path = path,
            )
            words = []
            for c in script.completions():
                if c.name.startswith('__'): continue
                words.append(c.name)
            data = (serial + ':' + ','.join(words)).encode('utf8')
            self.stdout.write_chars(data, len(data))
            self.stdout.write_chars(self.line_sep_encoded, self.line_sep_length)
            self.stdout.flush()
        if cond & GLib.IO_HUP:
            ret = False
            GLib.source_remove(self.stdin_id)
        return ret

main = Main()

main_loop = GLib.MainLoop()
main_loop.run()
