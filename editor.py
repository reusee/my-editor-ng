from gi.repository import Gtk, Pango, GtkSource
import os

class Editor(Gtk.Box):
  def __init__(self):
    super().__init__()

    self.buffers = []
    self.views = []
    self.set_homogeneous(True)

    self.default_font = Pango.FontDescription.from_string('Terminus 13')
    self.style_scheme_manager = GtkSource.StyleSchemeManager.get_default()
    self.style_scheme_manager.append_search_path(os.path.dirname(__file__))
    self.style_scheme = self.style_scheme_manager.get_scheme('molokai')

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

  def new_view(self, buf):
    view = GtkSource.View.new_with_buffer(buf)
    self.views.append(view)
    scroll = Gtk.ScrolledWindow()
    scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    scroll.add(view)

    view.modify_font(self.default_font)
    view.set_auto_indent(True)
    view.set_indent_on_tab(True)
    view.set_indent_width(2)
    view.set_insert_spaces_instead_of_tabs(True)
    view.set_smart_home_end(GtkSource.SmartHomeEndType.BEFORE)
    view.set_highlight_current_line(True)
    view.set_show_line_marks(False)
    view.set_show_line_numbers(True)
    view.set_tab_width(2)

    self.pack_start(scroll, True, True, 0)

    return view
