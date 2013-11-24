from gi.repository import Gtk, Pango, GtkSource, GObject
import os

from core_buffer import *
from core_view import *
from core_modal import *
from core_move import *
from core_switcher import *

class Editor(Gtk.Box,
    Buffer,
    View,
    Modal,
    Move,
    Switcher,
    ):

  __gsignals__ = {}

  def __init__(self):
    super().__init__()
    Buffer.__init__(self)
    View.__init__(self)
    Modal.__init__(self)
    Move.__init__(self)
    Switcher.__init__(self)

    self.set_homogeneous(True)

    # font and style
    self.default_font = Pango.FontDescription.from_string('Terminus 13')
    self.style_scheme_manager = GtkSource.StyleSchemeManager.get_default()
    self.style_scheme_manager.append_search_path(os.path.dirname(__file__))
    self.style_scheme = self.style_scheme_manager.get_scheme('molokai')

  def new_signal(self, name, arg_types):
    GObject.signal_new(name, Editor, GObject.SIGNAL_RUN_FIRST, None, arg_types)

  def dump_object(self, obj, pattern = None):
    if pattern:
      print([e for e in dir(obj) if pattern in e.lower()])
    else:
      print(dir(obj))
