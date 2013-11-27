#!/usr/bin/env python

from gi.repository import Gtk, Gdk
import sys

from editor import *

class Main(Gtk.Window):
    def __init__(self):
        super().__init__()

        # css
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(open('style.css', 'rb').read())
        Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )

        # top box
        self.box = Gtk.Box(spacing = 0)
        self.add(self.box)

        # editor
        self.editor = Editor()
        self.box.pack_end(self.editor, True, True, 0)

        # buffers
        for filename in sys.argv[1:]:
            buf = self.editor.new_buffer(filename)
            self.editor.load_file(buf, filename)
        if len(sys.argv) == 1:
            self.editor.new_buffer()

        # view first buffer
        self.editor.views[0].set_buffer(self.editor.buffers[0])

win = Main()
win.connect('delete-event', Gtk.main_quit)
win.show_all()
Gtk.main()
