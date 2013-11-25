from gi.repository import GtkSource, Gtk, GObject

class View:
  def __init__(self):
    self.views = []

    self.new_signal('view-created', (GtkSource.View,))

    self.current_view = None

  def new_view(self, buf = None):
    if buf:
      view = GtkSource.View.new_with_buffer(buf)
    else:
      view = GtkSource.View()
    self.views.append(view)
    scroll = Gtk.ScrolledWindow()
    scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    scroll.add(view)

    setattr(view, 'attr', {})

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
    view.set_wrap_mode(Gtk.WrapMode.NONE)

    self.views_box.pack_start(scroll, True, True, 0)
    self.emit('view-created', view)
    self.current_view = view

    return view
