from gi.repository import Gtk, Gdk, GObject
import os

class File:
  def __init__(self):
    self.emit('bind-command-key', ', t', self.open_file_chooser)

    self.file_chooser = FileChooser()
    self.connect('realize', lambda _: self.north_area.add(self.file_chooser))
    self.file_chooser.connect('done', self.open_file)

  def open_file_chooser(self, view):
    self.file_chooser.last_view = view
    os.chdir(os.path.dirname(view.get_buffer().attr['filename']))
    self.file_chooser.update_list(self.file_chooser.entry, None)
    self.file_chooser.show_all()
    self.file_chooser.entry.set_text('')
    self.file_chooser.entry.grab_focus()

  def open_file(self, file_chooser):
    filename = file_chooser.filename
    view = file_chooser.last_view
    if not filename: return
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

  __gsignals__ = {
    'done': (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

  def __init__(self):
    Gtk.Grid.__init__(self, orientation = Gtk.Orientation.VERTICAL)
    self.set_vexpand(True)
    self.set_hexpand(True)
    self.connect('key-press-event', self.handle_key_press)

    self.entry = Gtk.Entry()
    self.entry.set_hexpand(True)
    self.add(self.entry)
    self.entry.connect('notify::text', self.update_list)
    self.entry.connect('key-press-event', self.handle_key_press)

    store = Gtk.ListStore(str)
    self.store = store

    view = Gtk.TreeView(store)
    view.set_headers_visible(False)
    self.view = view
    self.add(view)

    renderer = Gtk.CellRendererText()
    column = Gtk.TreeViewColumn('path', renderer, text = 0)
    view.append_column(column)

    self.filename = None
    self.last_view = None

    select = view.get_selection()
    select.set_mode(Gtk.SelectionMode.BROWSE)
    select.connect('changed', self.on_selection_changed)
    self.select = select

  def on_selection_changed(self, selection):
    store, it = selection.get_selected()
    if it != None:
      self.filename = store[it][0]

  def handle_key_press(self, _, ev):
    _, val = ev.get_keyval()
    if val == Gdk.KEY_Escape:
      self.filename = None
      self.done()
    elif val == Gdk.KEY_Return:
      if os.path.isdir(self.filename): # enter subdirectory
        path = self.filename + os.path.sep
        self.entry.set_text(path)
        self.entry.set_position(-1)
      else:
        self.done()

  def done(self):
    self.hide()
    self.last_view.grab_focus()
    self.emit('done')

  def update_list(self, entry, _):
    head, tail = os.path.split(os.path.expanduser(entry.get_text()))
    if head == '':
      head = os.path.abspath('.')
    self.store.clear()
    candidates = []
    try:
      for f in os.listdir(head):
        if fuzzy_match(tail, f):
          candidates.append(os.path.join(head, f))
    except FileNotFoundError:
      return
    candidates = sorted(candidates)
    for c in candidates:
      self.store.append([c])
    self.select.select_path((0))

def fuzzy_match(key, s):
  keyI = 0
  sI = 0
  while keyI < len(key) and sI < len(s):
    if s[sI].lower() == key[keyI].lower():
      sI += 1
      keyI += 1
    else:
      sI += 1
  return keyI == len(key)
