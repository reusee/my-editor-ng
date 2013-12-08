class CorePatternMatch:
    def __init__(self):
        self.connect('buffer-created', self.setup_pattern_matcher)

        self.connect('key-pressed', self.update_pattern_matcher_state)
        self.connect('entered-command-mode',
            self.clear_pattern_matcher_state)

    def setup_pattern_matcher(self, _, buf):
        buf.attr['patterns'] = {}
        buf.attr['pattern-matcher-states'] = []

        self.add_pattern(buf, 'foobar', lambda buf: buf.insert(
            buf.get_iter_at_mark(buf.get_insert()), 'foobar', -1)
            or True)

    def update_pattern_matcher_state(self, _, view, ev):
        if self.operation_mode != self.EDIT: return
        buf = view.get_buffer()
        c = chr(ev.get_keyval()[1])
        new_states = []
        states = buf.attr['pattern-matcher-states']
        for state, start_mark in states:
            if c in state:
                state = state[c]
                if callable(state):
                    buf.begin_user_action()
                    buf.delete(buf.get_iter_at_mark(start_mark),
                        buf.get_iter_at_mark(buf.get_insert()))
                    buf.end_user_action()
                    buf.delete_mark(start_mark)
                    self.key_pressed_return_value = state(buf)
                    buf.attr['pattern-matcher-states'].clear()
                    return
                else:
                    new_states.append((state, start_mark))
        patterns = buf.attr['patterns']
        if c in patterns:
            new_states.append((patterns[c],
                buf.create_mark(None, buf.get_iter_at_mark(buf.get_insert()),
                    True)))
        buf.attr['pattern-matcher-states'] = new_states

    def clear_pattern_matcher_state(self, _):
        buf = self.get_current_buffer()
        buf.attr['pattern-matcher-states'].clear()

    def add_pattern(self, buf, pattern, callback):
        path = [c for c in pattern]
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
        cur[key] = callback
