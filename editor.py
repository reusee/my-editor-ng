from gi.repository import Gtk, Pango, GtkSource, GObject
import os

from core_buffer import *
from core_view import *
from core_modal import *

class Editor(Gtk.Box,
    Buffer,
    View,
    Modal,
    ):

  __gsignals__ = {}

  def __init__(self):
    super().__init__()
    Buffer.__init__(self)
    View.__init__(self)
    Modal.__init__(self)

    self.set_homogeneous(True)

    # font and style
    self.default_font = Pango.FontDescription.from_string('Terminus 13')
    self.style_scheme_manager = GtkSource.StyleSchemeManager.get_default()
    self.style_scheme_manager.append_search_path(os.path.dirname(__file__))
    self.style_scheme = self.style_scheme_manager.get_scheme('molokai')

  def new_signal(self, name, *args):
    GObject.signal_new(name, Editor, *args)
