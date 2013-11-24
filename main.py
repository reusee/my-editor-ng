#!/usr/bin/env python

from gi.repository import Gtk, Gdk
import sys

from editor import *

class Main(Gtk.Window):
    def __init__(self):
        super().__init__()

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(open('style.css', 'rb').read())
        Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )

        self.box = Gtk.Box(spacing = 0)
        self.add(self.box)

        self.editor = Editor()
        self.box.pack_end(self.editor, True, True, 0)

        for filename in sys.argv[1:]:
            buf = self.editor.new_buffer(filename)
            self.editor.new_view(buf)
            with open(filename, 'r') as f:
                buf.set_text(f.read())
        if len(sys.argv) == 1:
            buf = self.editor.new_buffer()
            self.editor.new_view(buf)
            v2 = self.editor.new_view(buf)
            v2.modify_font(Pango.FontDescription.from_string('Terminus 28'))

win = Main()
win.connect('delete-event', Gtk.main_quit)
win.show_all()
Gtk.main()
