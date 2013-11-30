from gi.repository import Gtk

class Completion:
  def __init__(self):
    self.vocabulary = set()
    self.connect('found-word', lambda _, word: self.vocabulary.add(word))
    self.connect('buffer-created', lambda _, buf:
      buf.connect('changed', lambda buf: self.hint_completion(buf)))

    self.completion_view = CompletionView()
    self.completion_view.show()
    self.connect('realize', lambda _: self.completion_view.set_parent(self))
    #self.connect('realize', lambda _:
      #self.south_area.add(self.completion_view))

  def hint_completion(self, buf):
    word_start_iter = buf.get_iter_at_mark(buf.attr['word-start'])
    word_end_iter = buf.get_iter_at_mark(buf.attr['word-end'])
    word = buf.get_text(word_start_iter, word_end_iter, False)
    if not word: return
    print('current word:', word)
    candidates = self.get_completion_candidates(word)

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
        self.completion_view.store.append([w])

class CompletionView(Gtk.TreeView):
  def __init__(self):
    store = Gtk.ListStore(str)
    Gtk.TreeView.__init__(self, store)
    self.set_vexpand(True)
    self.set_hexpand(True)
    self.store = store
    self.set_headers_visible(False)

    renderer = Gtk.CellRendererText()
    renderer.set_alignment(0.5, 0.5)
    column = Gtk.TreeViewColumn('word', renderer, text = 0)
    self.append_column(column)
