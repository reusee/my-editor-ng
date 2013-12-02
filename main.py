#!/usr/bin/env python

from gi.repository import Gtk, Gdk
import sys
import os

from editor import *

class Main(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.set_title('my editor')

        # css
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(
            open(os.path.join(os.path.dirname(__file__), 'style.css'), 'rb').read())
        Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )

        # top grid
        self.grid = Gtk.Grid()
        self.add(self.grid)

        # editor
        self.editor = Editor()
        self.grid.attach(self.editor, 0, 0, 1, 1)

        # buffers
        for filename in sys.argv[1:]:
            buf = self.editor.new_buffer(filename)
            self.editor.load_file(buf, filename)
        if len(sys.argv) == 1:
            self.editor.new_buffer()

        # view first buffer
        self.editor.views[0].set_buffer(self.editor.buffers[0])

def main():
    win = Main()
    win.connect('delete-event', Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()
