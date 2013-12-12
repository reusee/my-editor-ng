from gi.repository import Gtk, Gdk, GtkSource
from collections import OrderedDict

class CoreCompletion:
    def __init__(self):
        self.vocabulary = OrderedDict()
        self.connect('found-word', lambda _, word: self.vocabulary.setdefault(word, True))
        self.connect('buffer-created', lambda _, buf:
          buf.connect('changed', lambda buf: self.hint_completion(buf)))
        self.connect('entered-command-mode', lambda _:
          self.hint_completion(None))
        self.connect('entered-edit-mode', lambda _:
          self.hint_completion(self.get_current_buffer()))

        self.completion_view = CompletionView()
        self.completion_view.show_all()
        self.add_overlay(self.completion_view)

        self.bind_edit_key([Gdk.KEY_Tab], self.cycle_completion_candidates, 'next completion')

        self.completion_replacing = False # changing text
        self.completion_candidates = []

        self.new_signal('provide-completions', (GtkSource.Buffer, str, object))

    def hint_completion(self, buf):
        if self.completion_replacing: return
        self.completion_view.hide()
        self.completion_candidates.clear()
        if self.operation_mode != self.EDIT: return

        candidates = set()
        # word completions
        word_start_iter = buf.get_iter_at_mark(buf.attr['word-start'])
        word_end_iter = buf.get_iter_at_mark(buf.attr['word-end'])
        word = buf.get_text(word_start_iter, word_end_iter, False)
        if word:
            words = self.get_completion_candidates(word)
            candidates.update(words)
        # extra providers
        self.emit('provide-completions', buf, word, candidates)

        self.completion_candidates = sorted(candidates, key = lambda w: len(w))
        if len(self.completion_candidates) > 0:
            self.show_candidates()

    def show_candidates(self):
        self.completion_view.store.clear()
        for w in self.completion_candidates:
            self.completion_view.store.append([w])
        self.completion_view.show_all()
        self.completion_view.view.columns_autosize()
        # set position
        view = self.get_current_view()
        buf = view.get_buffer()
        iter_rect = view.get_iter_location(buf.get_iter_at_mark(buf.get_insert()))
        x, y = view.buffer_to_window_coords(Gtk.TextWindowType.WIDGET, iter_rect.x, iter_rect.y)
        y += iter_rect.height + 1
        x += 8
        win_rect = self.get_allocation()
        _, editor_x, editor_y = self.get_window().get_origin()
        _, view_x, view_y = view.get_window(Gtk.TextWindowType.WIDGET).get_origin()
        x += view_x - editor_x
        y += view_y - editor_y
        if y + 100 > win_rect.height:
            y -= 100
        if x + 100 > win_rect.width:
            x -= 200
        self.completion_view.set_margin_left(x)
        self.completion_view.set_margin_top(y)

    def get_completion_candidates(self, word):
        res = []
        n = 0
        for w in reversed(self.vocabulary):
            if w == word: continue
            #if w[0].lower() != word[0].lower(): continue
            i = 0 # for w
            j = 0 # for word
            while i < len(w) and j < len(word):
                if w[i] == word[j]:
                    i += 1
                    j += 1
                else:
                    i += 1
            if j == len(word): # match
                res.append(w)
                n += 1
                if n == 30:
                    return res
        return res

    def cycle_completion_candidates(self, view):
        if len(self.completion_candidates) == 0: return 'propagate'

        buf = view.get_buffer()
        start = buf.attr['word-start']
        end = buf.attr['word-end']

        text = buf.get_text(buf.get_iter_at_mark(start),
          buf.get_iter_at_mark(end), False)

        self.completion_replacing = True
        buf.begin_user_action()
        buf.delete(buf.get_iter_at_mark(start), buf.get_iter_at_mark(end))
        replace = self.completion_candidates[0]
        buf.insert(buf.get_iter_at_mark(start), replace, -1)
        buf.end_user_action()
        self.completion_replacing = False

        if len(self.completion_candidates) > 0:
            self.completion_candidates = self.completion_candidates[1:]
        self.completion_candidates.append(text)
        self.show_candidates()

class CompletionView(Gtk.Grid):
    def __init__(self):
        Gtk.Grid.__init__(self,
            halign = Gtk.Align.START,
            valign = Gtk.Align.START,
        )
        self.store = Gtk.ListStore(str)
        self.view = Gtk.TreeView(model = self.store)
        self.add(self.view)
        self.view.set_headers_visible(False)
        renderer = Gtk.CellRendererText()
        renderer.set_alignment(0, 0.5)
        column = Gtk.TreeViewColumn('word', renderer, text = 0)
        self.view.append_column(column)
