from gi.repository import GtkSource, Gdk

class CoreMacro:
    def __init__(self):
        self.macros = {}

        self.recorded_operations = []
        self.connect('key-handler-execute', self.record_key_handler)

        self.emit('bind-command-key', '. w', self.record_macro)
        self.recording_macro = False

        self.emit('bind-command-key', 'm w', lambda view, buf:
            lambda ev: self.call_macro(view, buf, ev))

    def record_key_handler(self, _, func, args):
        if not self.recording_macro: return
        if func == self.record_macro: return
        if func == self.save_macro: return
        self.recorded_operations.append(('key-handler', func, args))

    def record_macro(self):
        if not self.recording_macro: # start record
            self.recording_macro = True
            print('macro recording started')
        else: # ask for a key
            return self.save_macro

    def save_macro(self, ev):
        key = chr(ev.get_keyval()[1])
        self.macros[key] = self.recorded_operations
        self.recorded_operations = []
        self.recording_macro = False
        print('macro saved', key)

    def call_macro(self, view, buf, ev):
        key = chr(ev.get_keyval()[1])
        macro = self.macros.get(key, None)
        if not macro: return
        print('calling macro', key)
        for op in macro:
            if op[0] == 'key-handler':
                func = op[1]
                args = op[2]
                call_args = []
                for arg in args:
                    if isinstance(arg, GtkSource.View):
                        call_args.append(view)
                    elif isinstance(arg, GtkSource.Buffer):
                        call_args.append(buf)
                    elif isinstance(arg, Gdk.Event):
                        call_args.append(arg.copy())
                    elif isinstance(arg, int):
                        call_args.append(arg)
                    else:
                        print('unknown arg', arg)
                func(*call_args)
            else:
                print('unknown operation', op)
