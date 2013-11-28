from gi.repository import GtkSource, Gtk, Gio
import os

class Buffer:
  def __init__(self):
    self.buffers = []

    self.new_signal('buffer-created', (Gtk.TextBuffer,))
    self.new_signal('disk-file-changed', (Gio.FileMonitor, Gtk.TextBuffer, Gio.FileMonitorEvent))

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
    with open(filename, 'r') as f:
      buf.begin_not_undoable_action()
      buf.set_text(f.read())
      buf.end_not_undoable_action()
      buf.set_modified(False)
      self.monitor_file(buf, filename)
    buf.place_cursor(buf.get_start_iter())

  def monitor_file(self, buf, filename):
    monitor = Gio.File.monitor_file(Gio.File.new_for_path(filename), Gio.FileMonitorFlags.NONE, Gio.Cancellable())
    monitor.connect('changed', lambda monitor, _f, _other_f, event_type:
                      self.emit('disk-file-changed', monitor, buf, event_type))
    buf.attr['monitor'] = monitor
    print('monitor created', filename, monitor)
