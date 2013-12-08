from gi.repository import Vte, Gdk, GLib, Pango
import os

class CoreTerminal:
    def __init__(self):
        self.new_south_terminal(',e', '/usr/bin/env', 'fish')
        self.new_south_terminal('.e', '/usr/bin/env', 'fish')
        self.new_south_terminal('me', '/usr/bin/env', 'fish')
        self.new_south_terminal('.p', '/usr/bin/env', 'python')

    def new_south_terminal(self, key, *argv):
        terminal = Terminal(self, *argv)
        self.connect('realize', lambda _: self.south_area.add(terminal))
        self.connect('realize', lambda _: terminal.hide())
        self.bind_command_key(key, terminal.open)

class Terminal(Vte.Terminal):
    def __init__(self, editor, *argv):
        Vte.Terminal.__init__(self)
        self.editor = editor
        self.argv = argv
        self.connect('key-press-event', self.handle_key)
        self.view = None
        self.set_size(80, 25)
        self.set_cursor_blink_mode(Vte.TerminalCursorBlinkMode.OFF)
        self.set_font(Pango.FontDescription.from_string('Terminus 13'))
        self.set_scrollback_lines(-1)
        self.connect('child-exited', lambda _: self.run_shell())
        self.run_shell()

    def run_shell(self):
        _, pid = self.fork_command_full(
          Vte.PtyFlags.DEFAULT,
          os.environ['HOME'],
          self.argv,
          [],
          0,
          None,
          None)

    def handle_key(self, _, ev):
        _, val = ev.get_keyval()
        if val == Gdk.KEY_Escape:
            self.hide()
            self.editor.switch_to_view(self.view)
            self.view = None

    def open(self, view):
        self.view = view
        self.show()
        self.grab_focus()
