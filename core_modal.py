from gi.repository import GObject, Gtk, Gdk
import inspect

class Modal:

  EDIT, COMMAND = range(2)
  NONE, CHAR, LINE, RECT = range(4)

  def __init__(self):
    self.connect('view-created', lambda editor, view:
        view.connect('key-press-event', self.handle_key_press))

    self.new_signal('bind-command-key', (str, object))
    self.connect('bind-command-key', self.bind_command_key)

    self.operation_mode = self.COMMAND
    self.selection_mode = self.NONE
    self.command_key_handler = {}
    self.edit_key_handler = {}

    self.key_handler = self.command_key_handler
    self.delay_events = []

  def handle_key_press(self, view, ev):
    if self.operation_mode == self.COMMAND:
      self.handle_command_key(view, ev)
    elif self.operation_mode == self.EDIT:
      self.handle_edit_key(view, ev)
    return True

  def handle_command_key(self, view, ev):
    _, val = ev.get_keyval()
    if val == Gdk.KEY_Shift_L or val == Gdk.KEY_Shift_R: return False
    if val == Gdk.KEY_Escape: # cancel command
      self.reset_key_handler(self.command_key_handler)
      return True
    handler = None
    if isinstance(self.key_handler, dict): # dict handler
      key = chr(val) if val > 0x20 and val <= 0x7e else val
      handler = self.key_handler.get(key, None)
      if isinstance(handler, tuple): # tuple handler
        handler = handler[self.selection_mode]
    elif callable(self.key_handler): # function handler
      handler = self.key_handler
    if callable(handler): # trigger a command or call handler function
      self.reset_key_handler(self.command_key_handler)
      ret = self.execute_key_handler(handler, view, ev)
      if callable(ret): # another function handler
        self.key_handler = ret
      else: # trigger command
        pass
    elif isinstance(handler, dict): # sub dict handler
      self.key_handler = handler
    else: # no handler
      self.reset_key_handler(self.command_key_handler)
      print('no command for', chr(val))

  def handle_edit_key(self, view, key):
    pass

  def reset_key_handler(self, handler):
    self.delay_events.clear()
    self.key_handler = handler

  def execute_key_handler(self, f, view, ev):
    if '_param_names' not in f.__dict__:
      params = inspect.getargspec(f).args
      f.__dict__['_param_names'] = params
    args = []
    for param in f.__dict__['_param_names']:
      if param == 'ev': args.append(ev)
      elif param == 'n': args.append(self.n)
      elif param == 'view': args.append(view)
      elif param == 'self': continue
      else: print(param); handler_error
    return f(*args)

  def bind_command_key(self, editor, seq, handler): #TODO list dict
    seq = seq.split(' ')
    cur = self.command_key_handler
    for key in seq[:len(seq) - 1]:
      if key not in cur:
        cur[key] = {}
      if not isinstance(cur[key], dict): # conflict
        raise Exception('command conflict %s %s' % (seq, handler))
      cur = cur[key]
    if seq[-1] in cur: # conflict
      raise Exception('command conflict %s %s' % (seq, handler))
    cur[seq[-1]] = handler
