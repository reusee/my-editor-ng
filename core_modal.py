from gi.repository import GObject, Gtk, Gdk
import inspect

class Modal:

  EDIT, COMMAND = range(2)
  NONE, CHAR, LINE, RECT = range(4)

  def __init__(self):

    self.operation_mode = self.COMMAND
    self.selection_mode = self.NONE
    self.command_key_handler = {}
    self.edit_key_handler = {}

    self.connect('view-created', lambda editor, view:
        view.connect('key-press-event', self.handle_key_press))

    self.new_signal('bind-command-key', (str, object))
    self.new_signal('bind-edit-key', (str, object))
    self.connect('bind-command-key', 
        lambda _, seq, handler: self.bind_key_handler(self.command_key_handler, seq, handler))
    self.connect('bind-edit-key',
        lambda _, seq, handler: self.bind_key_handler(self.edit_key_handler, seq, handler))

    self.new_signal('edit-mode-entered', ())
    self.new_signal('command-mode-entered', ())

    self.key_handler = self.command_key_handler
    self.n = 0
    self.delay_chars = []
    self.delay_chars_timer = None

    for i in range(0, 10):
      self.emit('bind-command-key', str(i), self.make_number_prefix_handler(i))

  def handle_key_press(self, view, ev):
    _, val = ev.get_keyval()
    if val == Gdk.KEY_Shift_L or val == Gdk.KEY_Shift_R: return False
    if val == Gdk.KEY_Escape: # cancel command
      self.enter_command_mode()
      return True
    is_command_mode = self.operation_mode == self.COMMAND
    is_edit_mode = self.operation_mode == self.EDIT
    handler = None
    if isinstance(self.key_handler, dict): # dict handler
      key = chr(val) if val > 0x20 and val <= 0x7e else val
      handler = self.key_handler.get(key, None)
      if isinstance(handler, tuple): # tuple handler
        handler = handler[self.selection_mode]
    elif callable(self.key_handler): # function handler
      handler = self.key_handler
    if callable(handler): # trigger a command or call handler function
      if is_command_mode:
        self.reset_key_handler(self.command_key_handler)
      else:
        if self.delay_chars_timer:
          GObject.source_remove(self.delay_chars_timer)
        self.reset_key_handler(self.edit_key_handler)
      ret = self.execute_key_handler(handler, view, ev)
      if callable(ret): # another function handler
        self.key_handler = ret
      elif ret != 'is_number_prefix':
        self.n = 0
      else: # trigger command
        pass
    elif isinstance(handler, dict): # sub dict handler
      self.key_handler = handler
      if is_edit_mode:
        self.delay_chars.append(chr(val))
        self.delay_chars_timer = GObject.timeout_add(200,
            lambda: self.insert_delay_chars(view))
    else: # no handler
      if is_command_mode:
        self.reset_key_handler(self.command_key_handler)
      else:
        if self.delay_chars_timer:
          GObject.source_remove(self.delay_chars_timer)
        self.insert_delay_chars(view)
        self.reset_key_handler(self.edit_key_handler)
        return False
    return True

  def insert_delay_chars(self, view):
    buf = view.get_buffer()
    buf.insert(buf.get_iter_at_mark(buf.get_insert()), ''.join(self.delay_chars))
    self.reset_key_handler(self.edit_key_handler)

  def reset_key_handler(self, handler):
    self.key_handler = handler
    self.delay_chars.clear()

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

  def bind_key_handler(self, cur, seq, handler):
    seq = seq.split(' ')
    for key in seq[:len(seq) - 1]:
      if key not in cur:
        cur[key] = {}
      if not isinstance(cur[key], dict): # conflict
        raise Exception('command conflict %s %s' % (seq, handler))
      cur = cur[key]
    if seq[-1] in cur: # conflict
      raise Exception('command conflict %s %s' % (seq, handler))
    cur[seq[-1]] = handler

  def make_number_prefix_handler(self, i):
    def f():
      self.n = self.n * 10 + i
      return 'is_number_prefix'
    return f

  def enter_command_mode(self):
    self.operation_mode = self.COMMAND
    self.reset_key_handler(self.command_key_handler)
    self.emit('command-mode-entered')

  def enter_edit_mode(self):
    self.operation_mode = self.EDIT
    self.reset_key_handler(self.edit_key_handler)
    self.emit('edit-mode-entered')
