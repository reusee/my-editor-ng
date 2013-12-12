from gi.repository import Gtk

class CoreMacro:
    def __init__(self):
        self.macros = {}

        self.connect('key-pressed', self.record_key_events)
        self.connect('key-done', self.new_key_event_group)
        self.recording_macro = False
        self.recorded_key_events = []

        self.bind_command_key('.w', self.toggle_macro_recording, 'toggle macro recording')
        self.bind_command_key('mw', self.replay_macro, 'replay macro')

        self.macro_recording_state = self.create_overlay_label(
            valign = Gtk.Align.START, halign = Gtk.Align.END, margin_right = 150)
        self.macro_recording_state.set_markup('<span foreground="yellow">RECORDING</span>')

    def record_key_events(self, _, view, ev):
        if not self.recording_macro: return
        self.recorded_key_events[-1].append(ev.copy())

    def new_key_event_group(self, _):
        if not self.recording_macro: return
        self.recorded_key_events.append([])

    def toggle_macro_recording(self):
        if not self.recording_macro: # start
            self.recording_macro = True
            self.macro_recording_state.show()
        else: # stop
            def f(keyval):
                self.recording_macro = False
                key = chr(keyval)
                self.macros[key] = self.recorded_key_events[:-1]
                self.macro_recording_state.hide()
                self.show_message('macro saved ' + key)
                self.recorded_key_events = [[]]
            return f

    def replay_macro(self, view, n):
        if n == 0: n = 1
        def f(keyval):
            key = chr(keyval)
            macro = self.macros[key]
            self.show_message('replay macro ' + key)
            for _ in range(n):
                for group in macro:
                    for event in group:
                        view.emit('key-press-event', event)
        return f
