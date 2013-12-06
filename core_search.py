from gi.repository import Gtk, Gdk, GObject, GtkSource
import regex
from core_selection_transform import Transform

class Search:
    def __init__(self):
        self.search_entry = SearchEntry(self)
        self.connect('realize', lambda _:
          self.south_area.attach(self.search_entry, 0, -1, 1, 1))

        self.connect('buffer-created', self.setup_search)

        self.search_entry.connect('update', self.on_search_entry_update)
        self.search_entry.connect('done', lambda entry:
          self.next_search_result(entry.view, entry.is_backward))

        self.emit('bind-command-key', '/',
          lambda view: self.search_entry.run(view))
        self.emit('bind-command-key', '?',
          lambda view: self.search_entry.run(view, is_backward = True))
        self.emit('bind-command-key', 'n', lambda view:
          self.next_search_result(view))
        self.emit('bind-command-key', 'm', lambda view:
          self.next_search_result(view, backward = True))
        self.emit('bind-command-key', '*', self.search_current_word)

    def setup_search(self, _, buf):
        tag = buf.create_tag('search-result', foreground = '#FFFF00')
          #background = '#84bf96', foreground = '#000000')
        buf.attr['search-result-tag'] = tag
        buf.attr['search-pattern'] = ''
        buf.connect('changed', self.update_search_result)
        buf.attr['search-range-start'] = buf.create_mark(None, buf.get_start_iter())
        buf.attr['search-range-end'] = buf.create_mark(None, buf.get_end_iter())

    def update_search_result(self, buf):
        buf.remove_tag_by_name('search-result',
          buf.get_start_iter(), buf.get_end_iter())
        pattern = buf.attr['search-pattern']
        if not pattern: return
        content = buf.get_slice(buf.get_start_iter(), buf.get_end_iter(), False)
        try:
            pattern = regex.compile(pattern)
        except:
            return
        start = buf.get_start_iter()
        end = start.copy()
        range_start = buf.get_iter_at_mark(buf.attr['search-range-start'])
        range_end = buf.get_iter_at_mark(buf.attr['search-range-end'])
        for m in pattern.finditer(content):
            start.set_offset(m.start())
            end.set_offset(m.end())
            if not start.in_range(range_start, range_end): continue
            buf.apply_tag_by_name('search-result', start, end)

    def on_search_entry_update(self, entry, buf):
        self.update_search_result(buf)
        it = buf.get_iter_at_mark(buf.get_insert())
        tag = buf.attr['search-result-tag']
        func = it.forward_to_tag_toggle
        if entry.is_backward: func = it.backward_to_tag_toggle
        if func(tag):
            entry.view.scroll_to_iter(it, 0, True, 1, 0.5)

    def next_search_result(self, view, backward = False):
        buf = view.get_buffer()
        it = buf.get_iter_at_mark(buf.get_insert())
        tag = buf.attr['search-result-tag']
        func = it.forward_to_tag_toggle
        if backward: func = it.backward_to_tag_toggle
        if func(tag):
            if it.ends_tag(tag):
                if func(tag): buf.place_cursor(it)
            else:
                buf.place_cursor(it)
        view.scroll_to_mark(buf.get_insert(), 0, True, 1, 0.5)

    def search_current_word(self, buf):
        Transform(
                (self.mark_jump_to_word_edge, 0, True),
                (self.mark_jump_to_word_edge, 0),
                'cursor').apply(buf)
        buf.attr['search-pattern'] = buf.attr['cursor'].get_text()
        buf.move_mark(buf.attr['search-range-start'], buf.get_start_iter())
        buf.move_mark(buf.attr['search-range-end'], buf.get_end_iter())
        self.clear_selections(buf)
        self.update_search_result(buf)

class SearchEntry(Gtk.Entry):

    __gsignals__ = {
      'update': (GObject.SIGNAL_RUN_FIRST, None, (GtkSource.Buffer,)),
      'done': (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self, editor):
        Gtk.Entry.__init__(self)
        self.editor = editor
        self.set_hexpand(True)
        self.set_alignment(0.5)
        self.connect('key-press-event', self.on_key_press_event)
        self.connect('notify::text', self.update)

        self.is_backward = False
        self.view = None

    def update(self, _self, _):
        self.view.get_buffer().attr['search-pattern'] = self.get_text()
        self.emit('update', self.view.get_buffer())

    def run(self, view, is_backward = False):
        buf = view.get_buffer()
        if buf.get_has_selection():
            start, end = buf.get_selection_bounds()
            buf.move_mark(buf.attr['search-range-start'], start)
            buf.move_mark(buf.attr['search-range-end'], end)
            self.editor.clear_selections(buf)
        else:
            buf.move_mark(buf.attr['search-range-start'], buf.get_start_iter())
            buf.move_mark(buf.attr['search-range-end'], buf.get_end_iter())
        self.view = view
        self.is_backward = is_backward
        self.show_all()
        self.grab_focus()

    def on_key_press_event(self, _, ev):
        _, val = ev.get_keyval()
        if val == Gdk.KEY_Escape or val == Gdk.KEY_Return: # cancel
            if val == Gdk.KEY_Escape:
                self.view.scroll_to_mark(self.view.get_buffer().get_insert(), 0, True, 1, 0.5)
            else:
                self.update(None, None)
                self.emit('done')
            self.hide()
            self.view.grab_focus()
