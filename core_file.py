from gi.repository import Gtk
import os

class File:
  def __init__(self):
    self.emit('bind-command-key', ', t', self.open_file)

    self.file_chooser = FileChooser()
    self.east_area.add(self.file_chooser)
    self.connect('realize', lambda _: self.file_chooser.hide())

  def open_file(self, view):
    self.file_chooser.show()

    filename = os.path.abspath(filename)
    # create or select buffer
    buf = None
    for b in self.buffers:
      if b.attr['filename'] == filename:
        buf = b
    if buf is None:
      buf = self.new_buffer(filename)
      self.load_file(buf, filename)
    # switch to buffer
    if view.get_buffer() != buf:
      view.set_buffer(buf)

class FileChooser(Gtk.Grid):
  def __init__(self):
    Gtk.Grid.__init__(self, orientation = Gtk.Orientation.VERTICAL)

    store = Gtk.ListStore(str)
    store.append(['foo'])
    store.append(['bar'])
    store.append(['baz'])
    it = store.get_iter((0))
    print(store[it][0])
    self.store = store

    view = Gtk.TreeView(store)
    view.set_headers_visible(False)
    self.view = view
    self.add(view)

    renderer = Gtk.CellRendererText()
    column = Gtk.TreeViewColumn('path', renderer, text = 0)
    view.append_column(column)

    self.filename = None

    select = view.get_selection()
    select.connect('changed', self.on_selection_changed)

  def on_selection_changed(self, selection):
    store, it = selection.get_selected()
    if it != None:
      print(store[it][0])
      self.filename = store[it][0]
