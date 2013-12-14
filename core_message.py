from gi.repository import Gtk, GLib
import xml.sax.saxutils
import time

class CoreMessage:
    def __init__(self):
        self.message_board = Gtk.Grid(
            orientation = Gtk.Orientation.VERTICAL,
            valign = Gtk.Align.START,
            halign = Gtk.Align.CENTER,
            )
        self.message_history = []

        self.connect('realize', lambda _: self.add_overlay(self.message_board))

        self.bind_command_key(',,,',
          lambda: self.show_message('yes, sir ' + str(time.time())),
          'test message')
        self.bind_command_key(',,m', self.show_message_history,
            'show history message')
        self.bind_command_key(',,c', self.clear_messages,
            'clear showing message')

        self.new_signal('show-message', (str,))
        self.connect('show-message', lambda _, text: self.show_message(text))

    def show_message(self, text, **kwargs):
        text = xml.sax.saxutils.escape(text.strip())
        self.message_history.append(text)
        self._show_message(text, **kwargs)

    def _show_message(self, text, timeout = 3000):
        label = Gtk.Label()
        label.set_markup('<span foreground="lightgreen">' + text + '</span>')
        label.set_hexpand(True)
        self.message_board.add(label)
        GLib.timeout_add(timeout, lambda: label.destroy())
        self.message_board.show_all()

    def show_message_history(self):
        history = self.message_history[-30:]
        for msg in reversed(history):
            self._show_message(msg, timeout = 5000)

    def clear_messages(self):
        self.message_board.foreach(lambda e, _: e.destroy(), None)
