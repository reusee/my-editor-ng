class CoreMacro:
    def __init__(self):
        self.macros = {}

        self.connect('key-pressed', self.record_key_events)
        self.connect('key-done', self.new_key_event_group)
        self.recording_macro = False
        self.recorded_key_events = []

        self.emit('bind-command-key', '. w', self.toggle_macro_recording)
        self.emit('bind-command-key', 'm w', self.replay_macro)

    def record_key_events(self, _, ev):
        if not self.recording_macro: return
        self.recorded_key_events[-1].append(ev.copy())

    def new_key_event_group(self, _):
        if not self.recording_macro: return
        self.recorded_key_events.append([])

    def toggle_macro_recording(self):
        if not self.recording_macro: # start
            self.recording_macro = True
            print('recoding macro')
        else: # stop
            def f(ev):
                self.recording_macro = False
                key = chr(ev.get_keyval()[1])
                self.macros[key] = self.recorded_key_events[:-1]
                print('macro saved', key)
                self.recorded_key_events = [[]]
            return f

    def replay_macro(self, view, n):
        if n == 0: n = 1
        def f(ev):
            key = chr(ev.get_keyval()[1])
            macro = self.macros[key]
            print('replay macro', key)
            for _ in range(n):
                for group in macro:
                    for ev in group:
                        view.emit('key-press-event', ev)
        return f
