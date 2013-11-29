from gi.repository import Gtk, Gdk, GObject

class Search:
  def __init__(self):
    self.search_entry = SearchEntry()
    self.search_entry.set_hexpand(True)
    self.connect('realize', lambda _:
      self.south_area.attach(self.search_entry, 0, -1, 1, 1))
    self.emit('bind-command-key', '/',
      lambda view: self.search_entry.run(view, is_backward = False))
    self.emit('bind-command-key', '?',
      lambda view: self.search_entry.run(view, is_backward = True))

    self.connect('buffer-created', self.setup_searcher)

    self.search_entry.connect('notify::text', lambda entry, _:
      entry.view.get_buffer().attr['searcher']
        .set_property('pattern', entry.get_text()))
    self.search_entry.connect('done', lambda entry:
      self.next_search_result(entry.view)
      if not entry.is_backward else
      self.prev_search_result(entry.view))

    self.emit('bind-command-key', 'n', self.next_search_result)
    self.emit('bind-command-key', 'N', self.prev_search_result)

  def setup_searcher(self, _, buf):
    buf.attr['searcher'] = Searcher(buf)
    tag = buf.create_tag('search-result',
      background = '#0099CC', foreground = '#000000')
    buf.attr['search-result-tag'] = tag

  def next_search_result(self, view):
    buf = view.get_buffer()
    it = buf.get_iter_at_mark(buf.get_insert())
    tag = buf.attr['search-result-tag']
    if it.forward_to_tag_toggle(tag):
      if it.ends_tag(tag):
        if it.forward_to_tag_toggle(tag):
          self.move_mark(buf, it)
      else:
        self.move_mark(buf, it)
    view.scroll_mark_onscreen(buf.get_insert())

  def prev_search_result(self, view):
    buf = view.get_buffer()
    it = buf.get_iter_at_mark(buf.get_insert())
    tag = buf.attr['search-result-tag']
    if it.backward_to_tag_toggle(tag):
      if it.ends_tag(tag):
        if it.backward_to_tag_toggle(tag):
          self.move_mark(buf, it)
      else:
        self.move_mark(buf, it)
    view.scroll_mark_onscreen(buf.get_insert())

class Searcher(GObject.GObject):
  __gsignals__ = {
  }
  pattern = GObject.property(type = str, default = '')
  def __init__(self, buf):
    GObject.GObject.__init__(self)
    self.buf = buf
    self.connect('notify::pattern', self.update)

  def update(self, _self, _):
    self.buf.remove_tag_by_name('search-result',
      self.buf.get_start_iter(), self.buf.get_end_iter())
    pattern = self.pattern
    buffer_end = self.buf.get_end_iter()
    it = self.buf.get_start_iter()
    res = it.forward_search(pattern, 0, buffer_end)
    while res:
      start, end = res
      self.buf.apply_tag_by_name('search-result', start, end)
      it = end
      res = it.forward_search(pattern, 0, buffer_end)

class SearchEntry(Gtk.Entry):

  __gsignals__ = {
    'done': (GObject.SIGNAL_RUN_FIRST, None, ()),
  }

  def __init__(self):
    super().__init__()
    self.view = None
    self.connect('key-press-event', self.on_key_press_event)
    self.is_backward = False

  def run(self, view, is_backward = False):
    self.view = view
    self.is_backward = is_backward
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
