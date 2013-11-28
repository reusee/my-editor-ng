from gi.repository import Gtk, Gdk, GObject

class Search:
  def __init__(self):
    self.search_entry = SearchEntry()
    self.search_entry.set_hexpand(True)
    self.connect('realize', lambda _:
      self.south_area.attach(self.search_entry, 0, -1, 1, 1))
    self.emit('bind-command-key', '/', self.search_entry.run)

    self.search_entry.connect('done', self.search_and_highlight)

  def search_and_highlight(self, entry):
    print(entry.keyword)

class SearchEntry(Gtk.Entry):

  __gsignals__ = {
    'done': (GObject.SIGNAL_RUN_FIRST, None, ()),
  }

  def __init__(self):
    super().__init__()
    self.view = None
    self.connect('key-press-event', self.on_key_press_event)

  def run(self, view):
    self.view = view
    self.show_all()
    self.grab_focus()

  def on_key_press_event(self, _, ev):
    _, val = ev.get_keyval()
    if val == Gdk.KEY_Escape:
      self.keyword = ''
      self.done()
    elif val == Gdk.KEY_Return:
      self.keyword = self.get_text()
      self.done()

  def done(self):
    self.hide()
    self.view.grab_focus()
    self.emit('done')
