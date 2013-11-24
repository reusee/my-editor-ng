from gi.repository import GtkSource, Gtk

class Buffer:
  def __init__(self):
    self.buffers = []

  def new_buffer(self, filename = '<untitle>'):
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

    return buf

  def load_file(self, buf, filename):
    with open(filename, 'r') as f:
      buf.set_text(f.read())
    buf.place_cursor(buf.get_start_iter())
