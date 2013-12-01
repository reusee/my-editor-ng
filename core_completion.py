from gi.repository import Gtk

class Completion:
  def __init__(self):
    self.vocabulary = set()
    self.connect('found-word', lambda _, word: self.vocabulary.add(word))
    self.connect('buffer-created', lambda _, buf:
      buf.connect('changed', lambda buf: self.hint_completion(buf)))
    self.connect('entered-command-mode', lambda _:
      self.hint_completion(None))
    self.connect('entered-edit-mode', lambda _:
      self.hint_completion(self.get_current_buffer()))

    self.completion_view = CompletionView(self)

  def hint_completion(self, buf):
    self.completion_view.hide()
    if self.operation_mode != self.EDIT: return
    word_start_iter = buf.get_iter_at_mark(buf.attr['word-start'])
    word_end_iter = buf.get_iter_at_mark(buf.attr['word-end'])
    word = buf.get_text(word_start_iter, word_end_iter, False)
    if not word: return
    print('current word:', word)
    candidates = list(self.get_completion_candidates(word))
    if len(candidates) == 0: return
    max_length = 0
    candidates = sorted(candidates, key = lambda w: len(w))
    for w in candidates:
      self.completion_view.store.append([w])
      if len(w) > max_length: max_length = len(w)
    view = self.get_current_view()
    win = view.get_window(Gtk.TextWindowType.WIDGET)
    _, x, y = win.get_origin()
    buf = view.get_buffer()
    iter_rect = view.get_iter_location(buf.get_iter_at_mark(buf.get_insert()))
    win_x, win_y = view.buffer_to_window_coords(Gtk.TextWindowType.WIDGET,
      iter_rect.x, iter_rect.y)
    x += win_x
    y += win_y
    self.completion_view.move(x, y)
    self.completion_view.resize(1, len(candidates) * 26)
    self.completion_view.show_all()

  def get_completion_candidates(self, word):
    self.completion_view.store.clear()
    for w in self.vocabulary:
      if w == word: continue
      if w[0].lower() != word[0].lower(): continue
      i = 1 # for w
      j = 1 # for word
      while i < len(w) and j < len(word):
        if w[i] == word[j]:
          i += 1
          j += 1
        else:
          i += 1
      if j == len(word): # match
        print('->', w)
        yield w

class CompletionView(Gtk.Window):
  def __init__(self, parent):
    Gtk.Window.__init__(self, Gtk.WindowType.POPUP)
    self.set_attached_to(parent)
    self.set_name('completion_view')

    self.store = Gtk.ListStore(str)
    self.view = Gtk.TreeView(self.store)
    self.add(self.view)
    self.view.set_headers_visible(False)
    renderer = Gtk.CellRendererText()
    renderer.set_alignment(0, 0.5)
    column = Gtk.TreeViewColumn('word', renderer, text = 0)
    self.view.append_column(column)
