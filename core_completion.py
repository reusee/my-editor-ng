from gi.repository import Gtk, Gdk

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

    self.edit_key_handler[Gdk.KEY_Tab] = self.cycle_completion_candidates

    self.completion_replacing = False # changing text
    self.completion_candidates = []

  def hint_completion(self, buf):
    if self.completion_replacing: return
    self.completion_view.hide()
    self.completion_candidates.clear()
    if self.operation_mode != self.EDIT: return
    word_start_iter = buf.get_iter_at_mark(buf.attr['word-start'])
    word_end_iter = buf.get_iter_at_mark(buf.attr['word-end'])
    word = buf.get_text(word_start_iter, word_end_iter, False)
    if not word: return
    print('current word:', word)
    candidates = list(self.get_completion_candidates(word))
    if len(candidates) == 0: return
    candidates = sorted(candidates, key = lambda w: len(w))
    self.completion_candidates = candidates
    self.show_candidates()

  def show_candidates(self):
    max_length = 0
    self.completion_view.store.clear()
    for w in self.completion_candidates:
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
    self.completion_view.move(x, y + 20)
    self.completion_view.resize(1, len(self.completion_candidates) * 26)
    self.completion_view.show_all()

  def get_completion_candidates(self, word):
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

  def cycle_completion_candidates(self, view):
    if len(self.completion_candidates) == 0: return 'propagate'

    buf = view.get_buffer()
    start = buf.attr['word-start']
    end = buf.attr['word-end']

    text = buf.get_text(buf.get_iter_at_mark(start),
      buf.get_iter_at_mark(end), False)

    buf.begin_user_action()
    self.completion_replacing = True
    buf.delete(buf.get_iter_at_mark(start), buf.get_iter_at_mark(end))
    replace = self.completion_candidates[0]
    buf.insert(buf.get_iter_at_mark(start), replace, -1)
    self.completion_replacing = False
    buf.end_user_action()

    if len(self.completion_candidates) > 0:
      self.completion_candidates = self.completion_candidates[1:]
    self.completion_candidates.append(text)
    self.show_candidates()

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
