from gi.repository import Vte, Gdk, GLib, Pango
import os

class VteModule:
    def __init__(self, editor):
        self.terminal = Terminal()
        editor.south_area.add(self.terminal)
        editor.connect('realize', lambda _: self.terminal.hide())
        editor.bind_command_key(',e', self.terminal.open)

class Terminal(Vte.Terminal):
    def __init__(self):
        super().__init__()
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
          ['/usr/bin/fish'],
          [],
          0,
          None,
          None)

    def handle_key(self, _, ev):
        _, val = ev.get_keyval()
        if val == Gdk.KEY_Escape:
            self.hide()
            self.view.grab_focus()
            self.view = None

    def open(self, view):
        self.view = view
        self.show()
        self.grab_focus()
