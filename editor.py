from gi.repository import Gtk, Pango, GtkSource, GObject
import os

from core_modal import *
from core_buffer import *
from core_view import *
from core_defs import *
from core_text_object import *
from core_move import *
from core_switcher import *
from core_edit import *
from core_status import *
from core_selection import *
from core_scroll import *
from core_layout import *
from core_file import *
from core_message import *
from core_formatter import *

from mod_minimap import *

class Editor(Gtk.Grid,
    Modal,
    Buffer,
    View,
    Defs,
    TextObject,
    Move,
    Switcher,
    Edit,
    Status,
    Selection,
    Scroll,
    Layout,
    File,
    Message,
    Formatter,
    ):

  __gsignals__ = {}

  def __init__(self):
    super().__init__()
    Modal.__init__(self)
    Buffer.__init__(self)
    View.__init__(self)
    Defs.__init__(self)
    TextObject.__init__(self)
    Move.__init__(self)
    Switcher.__init__(self)
    Edit.__init__(self)
    Status.__init__(self)
    Selection.__init__(self)
    Scroll.__init__(self)
    Layout.__init__(self)
    File.__init__(self)
    Message.__init__(self)
    Formatter.__init__(self)

    # views
    self.views_grid = Gtk.Grid()
    self.views_grid.set_row_homogeneous(True)
    self.views_grid.set_column_homogeneous(True)
    self.attach(self.views_grid, 0, 0, 1, 1)

    # areas
    self.east_area = Gtk.Grid()
    self.attach(self.east_area, 1, 0, 1, 1)
    self.north_area = Gtk.Grid()
    self.attach(self.north_area, 0, -1, 2, 1)
    self.south_area = Gtk.Grid()
    self.attach(self.south_area, 0, 1, 2, 1)

    # font and style
    self.default_font = Pango.FontDescription.from_string('Terminus 13')
    self.style_scheme_manager = GtkSource.StyleSchemeManager.get_default()
    self.style_scheme_manager.append_search_path(os.path.dirname(__file__))
    self.style_scheme = self.style_scheme_manager.get_scheme('molokai')

    # extra modules
    #self.minimap = Minimap(self)

    # first view
    view, scroll = self.new_view()
    self.views_grid.add(scroll)

  def new_signal(self, name, arg_types):
    GObject.signal_new(name, Editor, GObject.SIGNAL_RUN_FIRST, None, arg_types)

  def dump(self, obj, pattern = None):
    if pattern:
      print([e for e in dir(obj) if pattern in e.lower()])
    else:
      print(dir(obj))
