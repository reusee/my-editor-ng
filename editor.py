from gi.repository import Gtk, GtkSource, GObject, Gdk
import os

core_modules = [
    'buffer',
    'view',
    'key',
    'defs',
    'edit',
    'status',
    'layout',
    'file',
    'message',
    'format',
    'search',
    'word_collector',
    'bookmark',
    'completion',
    'mark',
    'selection',
    'selection_transform',
    'selection_operation',
    'macro',
    'pattern_match',
    'terminal',
    'folding',
    'snippet',
    ]

classes = [
    getattr(__import__('core_' + module_name),
        'Core' + ''.join(e.capitalize()
            for e in module_name.split('_')))
    for module_name in core_modules]

extra_modules = [
    #'minimap',
    'python',
    #'jedi',
    'statistics',
    'profiling',
    'rust',
    ]

extra_classes = [
    getattr(__import__('mod_' + module_name),
        'Mod' + ''.join(e.capitalize()
            for e in module_name.split('_')))
    for module_name in extra_modules]

class Editor(Gtk.Overlay, *classes):

    __gsignals__ = {}

    def __init__(self):
        super().__init__()
        for cls in classes:
            cls.__init__(self)

        # root grid
        self.root_grid = Gtk.Grid()
        self.add(self.root_grid)

        # views
        self.views_grid = Gtk.Grid()
        self.views_grid.set_row_homogeneous(True)
        self.views_grid.set_column_homogeneous(True)
        self.root_grid.attach(self.views_grid, 0, 0, 1, 1)

        # areas
        self.east_area = Gtk.Grid()
        self.root_grid.attach(self.east_area, 1, 0, 1, 1)
        self.west_area = Gtk.Grid()
        self.root_grid.attach(self.west_area, -1, 0, 1, 1)
        self.north_area = Gtk.Grid()
        self.root_grid.attach(self.north_area, 0, -1, 2, 1)
        self.south_area = Gtk.Grid(orientation = Gtk.Orientation.VERTICAL)
        self.root_grid.attach(self.south_area, 0, 1, 2, 1)

        # font and style
        self.style_scheme_manager = GtkSource.StyleSchemeManager.get_default()
        self.style_scheme_manager.append_search_path(os.path.dirname(__file__))
        self.style_scheme = self.style_scheme_manager.get_scheme('solarizeddark')

        # extra classes
        for cls in extra_classes:
            cls(self)

        # first view
        view = self.create_view()
        self.views_grid.add(view.attr['wrapper'])
        self.connect('realize', lambda _: self.switch_to_view(self.views[0]))

    def new_signal(self, name, arg_types):
        GObject.signal_new(name, Editor, GObject.SIGNAL_RUN_FIRST, None, arg_types)

    def dump(self, obj, pattern = None):
        if pattern:
            print([e for e in dir(obj) if pattern in e.lower()])
        else:
            print(dir(obj))

    def create_overlay_label(self, **kwargs):
        label = Gtk.Label(**kwargs)
        self.add_overlay(label)
        self.connect('realize', lambda _: label.hide())
        return label
