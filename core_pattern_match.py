class PatternHandler:
    def __init__(self, pattern, callback, drop_key_event, clear_matched_text):
        self.pattern = pattern
        self.callback = callback
        self.drop_key_event = drop_key_event
        self.clear_matched_text = clear_matched_text

class CorePatternMatch:
    def __init__(self):
        self.connect('buffer-created', self.setup_pattern_matcher)

        self.connect('key-pressed', self.update_pattern_matcher_state)
        self.connect('entered-command-mode',
            self.clear_pattern_matcher_state)

    def setup_pattern_matcher(self, _, buf):
        buf.attr['patterns'] = {}
        buf.attr['pattern-matcher-states'] = []
        self.add_pattern(buf, 'foobar',
            lambda buf: self.show_message('foobar'),
            drop_key_event = False, clear_matched_text = False)

    def update_pattern_matcher_state(self, _, view, event):
        if self.operation_mode != self.EDIT: return
        buf = view.get_buffer()
        c = event.get_keyval()[1]
        new_states = []
        states = buf.attr['pattern-matcher-states']
        for state in states:
            if c in state:
                state = state[c]
                if isinstance(state, PatternHandler): # matched
                    if state.clear_matched_text:
                        it = buf.get_iter_at_mark(buf.get_insert())
                        end = it.copy()
                        for _ in range(len(state.pattern) - 1):
                            it.backward_char()
                        buf.begin_not_undoable_action()
                        buf.delete(it, end)
                        buf.end_not_undoable_action()
                    state.callback(buf)
                    if state.drop_key_event:
                        self.key_pressed_return_value = True
                    buf.attr['pattern-matcher-states'].clear()
                    return
                else:
                    new_states.append(state)
        patterns = buf.attr['patterns']
        if c in patterns:
            new_states.append(patterns[c])
        buf.attr['pattern-matcher-states'] = new_states

    def clear_pattern_matcher_state(self, _):
        buf = self.get_current_buffer()
        buf.attr['pattern-matcher-states'].clear()

    def add_pattern(self, buf, pattern, callback, drop_key_event, clear_matched_text):
        if isinstance(pattern, str):
            path = [ord(c) for c in pattern]
        else:
            path = pattern
        cur = buf.attr['patterns']
        for c in path[:-1]:
            if c not in cur: # create a path
                cur[c] = {}
                cur = cur[c]
            elif not isinstance(cur[c], dict): # conflict
                raise Exception('pattern conflict', pattern)
            else: # path
                cur = cur[c]
        key = path[-1]
        if key in cur: # conflict
            raise Exception('pattern conflict', pattern)
        cur[key] = PatternHandler(pattern, callback, drop_key_event, clear_matched_text)
