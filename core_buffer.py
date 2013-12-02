from gi.repository import GtkSource, Gtk
import os

class Buffer:
    def __init__(self):
        self.buffers = []

        self.new_signal('buffer-created', (GtkSource.Buffer,))
        self.connect('buffer-created', lambda _, buf:
          buf.connect('changed', lambda buf:
            self.emit('should-redraw')))
        self.connect('buffer-created', lambda _, buf:
          buf.connect('notify::cursor-position', lambda buf, _:
            self.emit('should-redraw')))

        self.emit('bind-command-key', ', q', self.close_buffer)
        self.emit('bind-command-key', ', n', self.new_buffer_then_view)

        self.new_signal('file-loaded', (GtkSource.Buffer,))
        self.new_signal('language-detected', (GtkSource.Buffer, str))

    def new_buffer(self, filename = ''):
        if filename: filename = os.path.abspath(filename)

        language_manager = GtkSource.LanguageManager.get_default()
        lang = language_manager.guess_language(filename, 'plain/text')
        if lang:
            buf = GtkSource.Buffer.new_with_language(lang)
        else:
            buf = GtkSource.Buffer()
        self.buffers.append(buf)

        setattr(buf, 'attr', {
          'filename': filename,
          'current_offset': 0,
          })

        if lang:
            self.emit('language-detected', buf, lang.get_name())

        buf.set_highlight_syntax(True)
        buf.set_highlight_matching_brackets(True)
        buf.set_max_undo_levels(-1)
        buf.set_style_scheme(self.style_scheme)
        buf.get_insert().set_visible(False)

        self.emit('buffer-created', buf)

        return buf

    def load_file(self, buf, filename):
        try:
            with open(filename, 'r') as f:
                buf.begin_not_undoable_action()
                buf.set_text(f.read())
                buf.end_not_undoable_action()
        except FileNotFoundError:
            pass
        buf.place_cursor(buf.get_start_iter())
        buf.set_modified(False)
        self.emit('file-loaded', buf)

    def new_buffer_then_view(self, view):
        buf = self.new_buffer()
        self.switch_to_buffer(view, buf)

    def close_buffer(self, view):
        buf = view.get_buffer()
        if buf.get_modified():
            self.emit('show-message', 'cannot close modified buffer ' + buf.attr['filename'])
            return
        if not buf.attr['filename']: return
        if len(self.buffers) == 1: return
        index = self.buffers.index(buf)
        index += 1
        if index == len(self.buffers): index = 0
        for view in self.views:
            if view.get_buffer() == buf:
                self.switch_to_buffer(view, self.buffers[index])
        self.buffers.remove(buf)
        print('closed buffer of', buf.attr['filename'])

    def get_current_buffer(self):
        for v in self.views:
            if v.is_focus(): return v.get_buffer()
        return None

    def switch_to_buffer(self, view, buf):
        view.set_buffer(buf)
        if 'indent-width' in buf.attr:
            view.set_indent_width(buf.attr['indent-width'])
        else:
            view.set_indent_width(self.default_indent_width)
