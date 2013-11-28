from gi.repository import GtkSource, Gtk
import os

class Buffer:
  def __init__(self):
    self.buffers = []

    self.new_signal('buffer-created', (Gtk.TextBuffer,))

    self.emit('bind-command-key', ', q', self.close_buffer)
    self.emit('bind-command-key', ', n', self.new_buffer_then_view)

  def new_buffer(self, filename = ''):
    language_manager = GtkSource.LanguageManager.get_default()
    lang = language_manager.guess_language(filename, 'plain/text')
    if lang:
      buf = GtkSource.Buffer.new_with_language(lang)
    else:
      buf = GtkSource.Buffer()
    self.buffers.append(buf)

    buf.set_highlight_syntax(True)
    buf.set_highlight_matching_brackets(True)
    buf.set_max_undo_levels(-1)
    buf.set_style_scheme(self.style_scheme)
    buf.get_insert().set_visible(False)

    if filename: filename = os.path.abspath(filename)

    setattr(buf, 'attr', {
      'filename': filename,
      'current_offset': 0,
      })

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

  def new_buffer_then_view(self, view):
    buf = self.new_buffer()
    view.set_buffer(buf)

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
        view.set_buffer(self.buffers[index])
    self.buffers.remove(buf)
    print('closed buffer of', buf.attr['filename'])
