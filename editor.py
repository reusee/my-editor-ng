from gi.repository import Gtk, Pango, GtkSource, GObject, Gdk
import os

from core_key import CoreKey
from core_buffer import Buffer
from core_view import View
from core_defs import Defs
from core_edit import Edit
from core_status import Status
from core_layout import Layout
from core_file import File
from core_message import Message
from core_format import CoreFormat
from core_search import Search
from core_word_collector import WordCollector
from core_bookmark import Bookmark
from core_completion import Completion
from core_mark import CoreMark
from core_selection import CoreSelection
from core_selection_transform import CoreSelectionTransform
from core_selection_operation import CoreSelectionOperation
from core_macro import CoreMacro
from core_pattern_match import CorePatternMatch
from core_terminal import CoreTerminal
from core_folding import CoreFolding

from mod_minimap import Minimap
from mod_python import ModPython
from mod_jedi import Jedi
from mod_statistics import ModStatistics
from mod_profiling import ModProfiling

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
    CorePatternMatch,
    CoreTerminal,
    CoreFolding,
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
        CorePatternMatch.__init__(self)
        CoreTerminal.__init__(self)
        CoreFolding.__init__(self)

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
        self.mod_stat = ModStatistics(self)
        self.mod_profiling = ModProfiling(self)

        # first view
        view, scroll = self.create_view()
        self.views_grid.add(scroll)
        self.connect('realize', lambda _: self.switch_to_view(self.views[0]))

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
