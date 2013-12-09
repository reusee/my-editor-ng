from gi.repository import GObject, Gtk, Gdk, GLib, GtkSource
import inspect

class CoreKey:

    EDIT, COMMAND = range(2)

    def __init__(self):

        self.operation_mode = self.COMMAND
        self.command_key_handler = {}
        self.edit_key_handler = {}

        self.new_signal('key-pressed', (GtkSource.View, Gdk.Event,))
        self.connect('key-pressed', lambda _, view, _event:
          self.emit('should-redraw'))
        self.key_pressed_return_value = False

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
            self.bind_command_key(str(i), self.make_number_prefix_handler(i),
                'numeric prefix')

        self.bind_command_key('i', self.enter_edit_mode, 'enter edit mode')
        self.bind_edit_key('kd', self.enter_command_mode)

        self.bind_command_key('.h', self.dump_command_keys,
            'show this message')

    def handle_key_press(self, view, ev):
        self.emit('key-pressed', view, ev.copy())
        if self.key_pressed_return_value:
            self.key_pressed_return_value = False
            return True
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
                    GLib.source_remove(self.delay_chars_timer)
                    self.delay_chars_timer = None
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
                self.delay_chars_timer = GLib.timeout_add(200,
                    lambda: self.insert_delay_chars(view))
            self.emit('key-prefix', chr(val))
        else: # no handler
            if is_edit_mode:
                if self.delay_chars_timer:
                    GLib.source_remove(self.delay_chars_timer)
                    self.delay_chars_timer = None
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
        buf.begin_user_action()
        buf.insert(buf.get_iter_at_mark(buf.get_insert()), ''.join(self.delay_chars))
        buf.end_user_action()
        self.key_handler = self.edit_key_handler
        self.delay_chars.clear()
        self.emit('key-done')
        self.delay_chars_timer = None

    def execute_key_handler(self, f, view, ev):
        if '_param_names' not in f.__dict__:
            params = inspect.getargspec(f).args
            f.__dict__['_param_names'] = params
        args = []
        for param in f.__dict__['_param_names']:
            if param.startswith('ev'): args.append(ev.copy())
            elif param.startswith('keyval'): args.append(ev.get_keyval()[1])
            elif param == 'n': args.append(self.n)
            elif param == 'view': args.append(view)
            elif param == 'buf': args.append(view.get_buffer())
            elif param == 'self': continue
            else: print('unknown param', param); handler_error
        self.emit('key-handler-execute', f, args)
        return f(*args)

    def bind_command_key(self, seq, handler, desc):
        handler.__dict__['_description_'] = desc
        self.bind_key_handler(self.command_key_handler, seq, handler)

    def bind_edit_key(self, seq, handler):
        self.bind_key_handler(self.edit_key_handler, seq, handler)

    def bind_key_handler(self, keymap, seq, handler):
        seq = [c for c in seq]
        for key in seq[:-1]:
            if key not in keymap:
                keymap[key] = {}
            if not isinstance(keymap[key], dict): # conflict
                raise Exception('command conflict %s %s' % (seq, handler))
            keymap = keymap[key]
        if seq[-1] in keymap: # conflict
            raise Exception('command conflict %s %s' % (seq, handler))
        keymap[seq[-1]] = handler

    def alias_command_key(self, dst_seq, src_seq):
        self.alias_key_handler(dst_seq, src_seq, self.command_key_handler)

    def alias_key_handler(self, dst_seq, src_seq, keymap):
        cur = keymap
        src_seq = [c for c in src_seq]
        for key in src_seq[:-1]:
            if (key not in cur) or (not isinstance(cur[key], dict)):
                raise Exception('invalid alias source')
            cur = cur[key]
        if src_seq[-1] not in cur:
            raise Exception('invalid alias source')
        src = cur[src_seq[-1]]
        self.bind_key_handler(keymap, dst_seq, src)

    def get_command_key(self, seq):
        return self.get_key_handler(seq, self.command_key_handler)

    def get_key_handler(self, seq, keymap):
        seq = [c for c in seq]
        for key in seq[:-1]:
            if (key not in keymap) or (not isinstance(keymap[key], dict)):
                raise Exception('invalid alias source')
            keymap = keymap[key]
        if seq[-1] not in keymap:
            raise Exception('invalid alias source')
        return keymap[seq[-1]]

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
        self.emit('entered-command-mode')

    def enter_edit_mode(self):
        self.operation_mode = self.EDIT
        self.key_handler = self.edit_key_handler
        self.emit('entered-edit-mode')

    def dump_keymap(self, keymap, path = None):
        if path is None: path = []
        if isinstance(keymap, dict):
            for key in sorted(keymap.keys()):
                self.dump_keymap(keymap[key], path + [key])
        else:
            if '_description_' not in keymap.__dict__:
                print('ADD DESCRIPTION TO', ''.join(path))
            print(''.join(path).rjust(8, ' '), keymap.__dict__['_description_'])

    def dump_command_keys(self):
        print('COMMAND MODE BINDINGS')
        self.dump_keymap(self.command_key_handler)
