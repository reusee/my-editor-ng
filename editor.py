from gi.repository import Gtk, Pango, GtkSource, GObject
import os

from core_key import *
from core_buffer import *
from core_view import *
from core_defs import *
from core_edit import *
from core_status import *
from core_layout import *
from core_file import *
from core_message import *
from core_format import *
from core_search import *
from core_word_collector import *
from core_bookmark import *
from core_completion import *
from core_mark import *
from core_selection import *
from core_selection_transform import *
from core_selection_operation import *
from core_macro import *
from core_statistics import *
from core_pattern_match import *

from mod_minimap import *
from mod_python import *
from mod_jedi import *
from mod_vte import *

class Editor(Gtk.Grid,
    CoreKey,
    Buffer,
    View,
    Defs,
    Edit,
    Status,
    Layout,
    File,
    Message,
    CoreFormat,
    Search,
    WordCollector,
    Bookmark,
    Completion,
    CoreMark,
    CoreSelection,
    CoreSelectionTransform,
    CoreSelectionOperation,
    CoreMacro,
    CoreStatistics,
    CorePatternMatch,
    ):

    __gsignals__ = {}

    def __init__(self):
        super().__init__()
        CoreKey.__init__(self)
        Buffer.__init__(self)
        View.__init__(self)
        Defs.__init__(self)
        Edit.__init__(self)
        Status.__init__(self)
        Layout.__init__(self)
        File.__init__(self)
        Message.__init__(self)
        CoreFormat.__init__(self)
        Search.__init__(self)
        WordCollector.__init__(self)
        Bookmark.__init__(self)
        Completion.__init__(self)
        CoreMark.__init__(self)
        CoreSelection.__init__(self)
        CoreSelectionTransform.__init__(self)
        CoreSelectionOperation.__init__(self)
        CoreMacro.__init__(self)
        CoreStatistics.__init__(self)
        CorePatternMatch.__init__(self)

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
        self.south_area = Gtk.Grid(orientation = Gtk.Orientation.VERTICAL)
        self.attach(self.south_area, 0, 1, 2, 1)

        # font and style
        self.default_font = Pango.FontDescription.from_string('Terminus 13')
        self.style_scheme_manager = GtkSource.StyleSchemeManager.get_default()
        self.style_scheme_manager.append_search_path(os.path.dirname(__file__))
        self.style_scheme = self.style_scheme_manager.get_scheme('solarizeddark')

        # screen
        screen = Gdk.Screen.get_default()
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # extra modules
        #self.minimap = Minimap(self)
        self.mod_python = ModPython(self)
        #self.jedi = Jedi(self)
        self.vte_module = VteModule(self)

        # first view
        view, scroll = self.create_view()
        self.views_grid.add(scroll)
        self.connect('realize', lambda _: self.views[0].grab_focus())

    def new_signal(self, name, arg_types):
        GObject.signal_new(name, Editor, GObject.SIGNAL_RUN_FIRST, None, arg_types)

    def dump(self, obj, pattern = None):
        if pattern:
            print([e for e in dir(obj) if pattern in e.lower()])
        else:
            print(dir(obj))

    def chain(self, *funcs):
        for func in funcs:
            func()
