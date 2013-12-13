#!/usr/bin/env python

from gi.repository import Gtk, Gdk
import sys
import os
import traceback

from editor import Editor

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

        # top container
        self.root_container = Gtk.Overlay()
        self.add(self.root_container)

        # editor
        self.editor = Editor()
        self.root_container.add(self.editor)

        # buffers
        for filename in sys.argv[1:]:
            buf = self.editor.create_buffer(filename)
            self.editor.load_file(buf, filename)
        if len(sys.argv) == 1:
            self.editor.create_buffer()

        # view first buffer
        self.editor.switch_to_buffer(
            self.editor.views[0],
            self.editor.buffers[0])

        # exception board
        self.exception_board = ExceptionBoard()
        self.root_container.add_overlay(self.exception_board)
        self.connect('realize', lambda _: self.exception_board.hide())

        sys.excepthook = self.excepthook

    def excepthook(self, type, value, tback):
        self.exception_board.label.set_text('\n'.join(traceback.format_exception(type, value, tback)))
        self.exception_board.show()
        sys.__excepthook__(type, value, tback)

class ExceptionBoard(Gtk.Overlay):
    def __init__(self):
        Gtk.Overlay.__init__(self)
        self.label = Gtk.Label()
        self.add(self.label)
        self.button = Gtk.Button(
            valign = Gtk.Align.END,
            halign = Gtk.Align.END,
            label = "X")
        self.add_overlay(self.button)
        self.button.connect('clicked', lambda _: self.hide())

def main():
    win = Main()
    win.connect('delete-event', Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()
