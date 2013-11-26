from gi.repository import Gtk, Pango, GtkSource, GObject
import os

from core_buffer import *
from core_view import *
from core_defs import *
from core_modal import *
from core_text_object import *
from core_move import *
from core_switcher import *
from core_edit import *
from core_status import *
from core_selection import *

from mod_minimap import *

class Editor(Gtk.Box,
    Buffer,
    View,
    Defs,
    Modal,
    TextObject,
    Move,
    Switcher,
    Edit,
    Status,
    Selection,
    ):

  __gsignals__ = {}

  def __init__(self):
    super().__init__()
    Buffer.__init__(self)
    View.__init__(self)
    Defs.__init__(self)
    Modal.__init__(self)
    TextObject.__init__(self)
    Move.__init__(self)
    Switcher.__init__(self)
    Edit.__init__(self)
    Status.__init__(self)
    Selection.__init__(self)

    # views
    self.views_box = Gtk.Box()
    self.views_box.set_homogeneous(True)
    self.pack_start(self.views_box, True, True, 0)

    # areas
    self.east_area = Gtk.VBox()
    self.pack_start(self.east_area, False, False, 0)

    # font and style
    self.default_font = Pango.FontDescription.from_string('Terminus 13')
    self.style_scheme_manager = GtkSource.StyleSchemeManager.get_default()
    self.style_scheme_manager.append_search_path(os.path.dirname(__file__))
    self.style_scheme = self.style_scheme_manager.get_scheme('molokai')

    # extra modules
    #self.minimap = Minimap(self)

  def new_signal(self, name, arg_types):
    GObject.signal_new(name, Editor, GObject.SIGNAL_RUN_FIRST, None, arg_types)

  def dump(self, obj, pattern = None):
    if pattern:
      print([e for e in dir(obj) if pattern in e.lower()])
    else:
      print(dir(obj))
