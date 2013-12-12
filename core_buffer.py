from gi.repository import GtkSource, Gtk
import os

class CoreBuffer:
    def __init__(self):
        self.buffers = []

        self.new_signal('buffer-created', (GtkSource.Buffer,))
        self.connect('buffer-created', lambda _, buf:
          buf.connect('changed', lambda buf:
            self.emit('should-redraw')))
        self.connect('buffer-created', lambda _, buf:
          buf.connect('notify::cursor-position', lambda buf, _:
            self.emit('should-redraw')))
        self.connect('buffer-created', lambda _, buf:
            buf.connect('notify::cursor-position', lambda buf, _:
                self.with_current_view(lambda v: v.scroll_to_mark(
                    buf.get_insert(), 0, False, 1, 0.5)
                    if v.get_buffer() == buf else None)))

        self.bind_command_key(',q', self.close_buffer, 'close current buffer')

        self.new_signal('file-loaded', (GtkSource.Buffer,))
        self.new_signal('language-detected', (GtkSource.Buffer, str))

        # buffer list
        self.buffer_list = Gtk.Label()
        self.connect('realize', lambda _: self.south_area.add(self.buffer_list))
        self.buffer_list.set_hexpand(True)
        self.buffer_list.show_all()

    def update_buffer_list(self, current_buffer):
        markup = []
        index = self.buffers.index(current_buffer)
        for buf in self.buffers[index:] + self.buffers[:index]:
            if buf == current_buffer:
                markup.append('<span foreground="lightgreen">' + os.path.basename(buf.attr['filename']) + '</span>')
            else:
                markup.append('<span>' + os.path.basename(buf.attr['filename']) + '</span>')
        self.buffer_list.set_markup('    '.join(markup))

    def create_buffer(self, filename = ''):
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
          'preferred-line-offset': 0,
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
        self.show_message('close buffer of ' + buf.attr['filename'])
        self.update_buffer_list(self.get_current_buffer())

    def get_current_buffer(self):
        for v in self.views:
            if v.is_focus(): return v.get_buffer()
        return None

    def switch_to_buffer(self, view, buf):
        self.save_current_buffer_cursor_position(view)
        view.set_buffer(buf)
        self.restore_current_buffer_cursor_position(view)
        if 'indent-width' in buf.attr:
            view.set_indent_width(buf.attr['indent-width'])
        else:
            view.set_indent_width(self.default_indent_width)
