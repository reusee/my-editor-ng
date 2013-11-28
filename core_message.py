from gi.repository import Gtk, GObject
import time

class Message:
  def __init__(self):
    self.message_board = Gtk.Grid(orientation = Gtk.Orientation.VERTICAL)
    self.message_history = []

    self.connect('realize', lambda _: self.south_area.add(self.message_board))

    self.emit('bind-command-key', ', , ,', 
      lambda: self.show_message('yes, sir ' + str(time.time())))
    self.emit('bind-command-key', ', , m', self.show_message_history)
    self.emit('bind-command-key', ', , c', self.clear_messages)
  
  def show_message(self, text, **kwargs):
    self.message_history.append(text)
    self._show_message(text, **kwargs)    

  def _show_message(self, text, timeout = 3000):
    label = Gtk.Label(text)
    label.set_hexpand(True)
    self.message_board.add(label)
    GObject.timeout_add(timeout, lambda: label.destroy())
    self.message_board.show_all()

  def show_message_history(self):
    history = self.message_history[-30:]
    for msg in reversed(history):
      self._show_message(msg, timeout = 5000)

  def clear_messages(self):
    self.message_board.foreach(lambda e, _: e.destroy(), None)