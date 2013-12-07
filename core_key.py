from gi.repository import GObject, Gtk, Gdk
import inspect

class CoreKey:

    EDIT, COMMAND = range(2)

    def __init__(self):

        self.operation_mode = self.COMMAND
        self.command_key_handler = {}
        self.edit_key_handler = {}

        self.new_signal('key-pressed', (Gdk.Event,))
        self.connect('key-pressed', lambda _, ev:
          self.emit('should-redraw'))

        self.new_signal('bind-command-key', (str, object))
        self.new_signal('bind-edit-key', (str, object))
        self.connect('bind-command-key',
            lambda _, seq, handler: self.bind_key_handler(self.command_key_handler, seq, handler))
        self.connect('bind-edit-key',
            lambda _, seq, handler: self.bind_key_handler(self.edit_key_handler, seq, handler))

        self.new_signal('key-done', ())
        self.new_signal('key-prefix', (str,))
        self.new_signal('key-handler-execute', (object, object))

        self.new_signal('entered-edit-mode', ())
        self.new_signal('entered-command-mode', ())

        self.key_handler = self.command_key_handler
        self.n = 0
        self.delay_chars = []
        self.delay_chars_timer = None

        for i in range(0, 10):
            self.emit('bind-command-key', str(i), self.make_number_prefix_handler(i))

    def handle_key_press(self, view, ev):
        self.emit('key-pressed', ev.copy())
        _, val = ev.get_keyval()
        if val == Gdk.KEY_Shift_L or val == Gdk.KEY_Shift_R:
            return False
        if val == Gdk.KEY_Escape: # cancel command
            self.enter_command_mode()
            return True
        is_edit_mode = self.operation_mode == self.EDIT
        handler = None
        if isinstance(self.key_handler, dict): # dict handler
            key = chr(val) if val >= 0x20 and val <= 0x7e else val
            handler = self.key_handler.get(key, None)
        elif callable(self.key_handler): # function handler
            handler = self.key_handler
        if callable(handler): # trigger a command or call handler function
            if is_edit_mode: # not a char to insert
                if self.delay_chars_timer:
                    GObject.source_remove(self.delay_chars_timer)
                self.key_handler = self.edit_key_handler
                self.delay_chars.clear()
            else:
                self.key_handler = self.command_key_handler
            ret = self.execute_key_handler(handler, view, ev)
            if callable(ret): # another function handler
                self.key_handler = ret
                self.emit('key-prefix', chr(val))
            elif isinstance(ret, dict): # another dict handler
                self.key_handler = ret
                self.emit('key-prefix', chr(val))
            elif ret == 'is_number_prefix': # a number prefix
                pass
            elif ret == 'propagate': # pass to system handler
                return False
            else: # handler executed
                self.emit('key-done')
                self.n = 0
        elif isinstance(handler, dict): # sub dict handler
            self.key_handler = handler
            if is_edit_mode:
                self.delay_chars.append(chr(val))
                self.delay_chars_timer = GObject.timeout_add(200,
                    lambda: self.insert_delay_chars(view))
            self.emit('key-prefix', chr(val))
        else: # no handler
            if is_edit_mode:
                if self.delay_chars_timer:
                    GObject.source_remove(self.delay_chars_timer)
                self.insert_delay_chars(view)
                self.key_handler = self.edit_key_handler
                return False
            else:
                print('no handler')
                self.key_handler = self.command_key_handler
            self.emit('key-done')
        return True

    def insert_delay_chars(self, view):
        buf = view.get_buffer()
        buf.insert(buf.get_iter_at_mark(buf.get_insert()), ''.join(self.delay_chars))
        self.key_handler = self.edit_key_handler
        self.delay_chars.clear()
        self.emit('key-done')

    def execute_key_handler(self, f, view, ev):
        if '_param_names' not in f.__dict__:
            params = inspect.getargspec(f).args
            f.__dict__['_param_names'] = params
        args = []
        for param in f.__dict__['_param_names']:
            if param.startswith('ev'): args.append(ev.copy())
            elif param == 'n': args.append(self.n)
            elif param == 'view': args.append(view)
            elif param == 'buf': args.append(view.get_buffer())
            elif param == 'self': continue
            else: print('unknown param', param); handler_error
        self.emit('key-handler-execute', f, args)
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
        self.key_handler = self.command_key_handler
        self.n = 0
        self.emit('key-done')
        self.emt('entered-command-mode')

    def enter_edit_mode(self):
        self.operation_mode = self.EDIT
        self.key_handler = self.edit_key_handler
        self.emit('entered-edit-mode')
