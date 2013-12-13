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
        self.new_signal('numeric-prefix', (int,))
        self.new_signal('key-handler-execute', (object, object))

        self.new_signal('entered-edit-mode', ())
        self.new_signal('entered-command-mode', ())

        self.n = 0
        self.delay_chars = []
        self.delay_chars_timer = None

        for i in range(0, 10):
            self.bind_command_key(str(i), self.make_number_prefix_handler(i),
                'numeric prefix')

        self.bind_command_key('i', lambda buf:
            self.enter_edit_mode(buf), 'enter edit mode')
        self.bind_edit_key('kd', lambda buf:
            self.enter_command_mode(buf), 'enter command mode')

        self.bind_command_key('.h', self.dump_keys,
            'show this message')

        # mode indicator
        self.edit_mode_indicator = self.create_overlay_label(
            halign = Gtk.Align.END, valign = Gtk.Align.CENTER)
        self.edit_mode_indicator.set_markup('<span font="24" foreground="lightgreen">EDITING</span>')
        self.connect('entered-edit-mode', lambda _: self.edit_mode_indicator.show())
        self.connect('entered-command-mode', lambda _: self.edit_mode_indicator.hide())

        # command prefix indicator
        self.command_prefix = []
        self.connect('key-done', lambda w: [
            self.command_prefix.clear(),
            self.update_command_prefix_indicator()])
        self.connect('key-prefix', lambda w, c: [
            self.command_prefix.append(c),
            self.update_command_prefix_indicator()])
        self.connect('numeric-prefix', lambda _, _n:
            self.update_command_prefix_indicator())
        self.command_prefix_indicator = self.create_overlay_label(
            halign = Gtk.Align.END, valign = Gtk.Align.END)

    def handle_key(self, view, ev_or_keyval):
        if isinstance(ev_or_keyval, Gdk.EventKey): # gdk key event
            self.emit('key-pressed', view, ev_or_keyval.copy())
            if self.key_pressed_return_value:
                self.key_pressed_return_value = False
                return True
            _, val = ev_or_keyval.get_keyval()
        else: # by feed_keys
            val = ev_or_keyval
        if val in ( # ignore these keys
            Gdk.KEY_Shift_L, Gdk.KEY_Shift_R,
            Gdk.KEY_Alt_L, Gdk.KEY_Alt_R,
            Gdk.KEY_Control_L, Gdk.KEY_Control_R,
            ):
            return False
        buf = view.get_buffer()
        if val == Gdk.KEY_Escape: # cancel command
            self.enter_command_mode(buf)
            return True
        is_edit_mode = self.operation_mode == self.EDIT
        # find handler
        handler = None
        if isinstance(buf.key_handler, dict): # dict handler
            key = chr(val) if val >= 0x20 and val <= 0x7e else val
            handler = buf.key_handler.get(key, None)
        elif callable(buf.key_handler): # function handler
            handler = buf.key_handler
        # handle it
        if callable(handler): # trigger a command or call handler function
            if is_edit_mode: # not a char to insert
                if self.delay_chars_timer:
                    GLib.source_remove(self.delay_chars_timer)
                    self.delay_chars_timer = None
                buf.key_handler = buf.edit_key_handler
                self.delay_chars.clear()
            else:
                buf.key_handler = buf.command_key_handler
            ret = self.execute_key_handler(handler, view, val)
            if callable(ret): # another function handler
                buf.key_handler = ret
                self.emit('key-prefix', chr(val))
            elif isinstance(ret, dict): # another dict handler
                buf.key_handler = ret
                self.emit('key-prefix', chr(val))
            elif ret == 'is_number_prefix': # a number prefix
                self.emit('numeric-prefix', int(chr(val)))
            elif ret == 'propagate': # pass to system handler
                return False
            else: # handler executed
                self.n = 0
                self.emit('key-done')
        elif isinstance(handler, dict): # sub dict handler
            buf.key_handler = handler
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
                buf.key_handler = buf.edit_key_handler
                return False
            else:
                self.show_message('no handler')
                buf.key_handler = buf.command_key_handler
            self.emit('key-done')
        return True

    def insert_delay_chars(self, view):
        buf = view.get_buffer()
        buf.begin_user_action()
        buf.insert(buf.get_iter_at_mark(buf.get_insert()), ''.join(self.delay_chars))
        buf.end_user_action()
        buf.key_handler = buf.edit_key_handler
        self.delay_chars.clear()
        self.emit('key-done')
        self.delay_chars_timer = None

    def execute_key_handler(self, f, view, keyval):
        if '_param_names' not in f.__dict__:
            params = inspect.getargspec(f).args
            f.__dict__['_param_names'] = params
        args = []
        for param in f.__dict__['_param_names']:
            if param.startswith('keyval'): args.append(keyval)
            elif param == 'n': args.append(self.n)
            elif param == 'view': args.append(view)
            elif param == 'buf': args.append(view.get_buffer())
            elif param == 'self': continue
            else: print('unknown param', param); handler_error
        self.emit('key-handler-execute', f, args)
        return f(*args)

    def bind_command_key(self, seq, handler, desc):
        self.bind_key_handler(self.command_key_handler, seq, handler, desc)
        for buf in self.buffers: # set to all buffers
            self.bind_key_handler(buf.command_key_handler, seq, handler, desc)

    def bind_edit_key(self, seq, handler, desc):
        self.bind_key_handler(self.edit_key_handler, seq, handler, desc)
        for buf in self.buffers:
            self.bind_key_handler(buf.edit_key_handler, seq, handler, desc)

    def bind_key_handler(self, keymap, seq, handler, desc = None):
        if desc:
            handler.__dict__['_description_'] = desc
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
        for buf in self.buffers:
            self.alias_key_handler(dst_seq, src_seq, buf.command_key_handler)

    def alias_edit_key(self, dst_seq, src_seq):
        self.alias_key_handler(dst_seq, src_seq, self.edit_key_handler)
        for buf in self.buffers:
            self.alias_key_handler(dst_seq, src_seq, buf.edit_key_handler)

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

    def enter_command_mode(self, buf):
        self.operation_mode = self.COMMAND
        buf.key_handler = buf.command_key_handler
        self.n = 0
        self.emit('key-done')
        self.emit('entered-command-mode')

    def enter_edit_mode(self, buf):
        self.operation_mode = self.EDIT
        buf.key_handler = buf.edit_key_handler
        self.emit('entered-edit-mode')

    def dump_keymap(self, keymap, path = None):
        if path is None: path = []
        if isinstance(keymap, dict):
            for key in sorted(keymap.keys(), key = lambda e: str(e)):
                self.dump_keymap(keymap[key], path + [str(key)])
        else:
            if '_description_' not in keymap.__dict__:
                print('ADD DESCRIPTION TO', ''.join(path))
            print(''.join(path).rjust(8, ' '), keymap.__dict__['_description_'])

    def dump_keys(self):
        print('COMMAND MODE BINDINGS')
        self.dump_keymap(self.command_key_handler)
        print('EDIT MODE BINDINGS')
        self.dump_keymap(self.edit_key_handler)

    def feed_keys(self, view, seq):
        for c in seq:
            self.handle_key(view, ord(c))

    def update_command_prefix_indicator(self):
        if not self.command_prefix and self.n == 0:
            self.command_prefix_indicator.hide()
            return
        t = ''.join(self.command_prefix)
        if self.n != 0: t = str(self.n) + t
        self.command_prefix_indicator.set_markup(
            '<span font="24" foreground="lightgreen">' + t + '</span>')
        self.command_prefix_indicator.show()
