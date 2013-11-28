from gi.repository import GtkSource, Gtk, GObject

class View:
  def __init__(self):
    self.views = []

    self.new_signal('view-created', (GtkSource.View,))
    self.connect('view-created', lambda editor, view:
        view.connect('key-press-event', self.handle_key_press))

    self.current_view = None

    self.emit('bind-command-key', ', z', self.close_view)

  def new_view(self, buf = None):
    if buf:
      view = GtkSource.View.new_with_buffer(buf)
    else:
      view = GtkSource.View()
    self.views.append(view)
    scroll = Gtk.ScrolledWindow()
    scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    scroll.set_placement(Gtk.CornerType.TOP_RIGHT)
    scroll.set_property('expand', True)
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

    self.emit('view-created', view)
    self.current_view = view

    return view, scroll

  def switch_to_view(self, view):
    self.current_view = view
    view.grab_focus()

  def close_view(self, view):
    if len(self.views) == 1: return
    scroll = view.get_parent()
    index = self.views.index(view)
    self.views.remove(view)
    index -= 1
    if index < 0: index = 0
    next_view = self.views[index]
    scroll.destroy()
    self.switch_to_view(next_view)
