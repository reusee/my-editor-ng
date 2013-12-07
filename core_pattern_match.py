class CorePatternMatch:
    def __init__(self):
        self.connect('buffer-created', self.setup_pattern_matcher)

    def setup_pattern_matcher(self, _, buf):
        buf.attr['patterns'] = {}
        buf.attr['pattern-matcher-states'] = []
        buf.connect_after('insert-text', self.update_matcher_state_on_insert)
        buf.connect_after('delete-range', self.update_matcher_state_on_delete)

        self.add_pattern(buf, 'foobar', lambda buf: print('foobar'))

    def update_matcher_state_on_insert(self, buf, it, text, length):
        new_states = []
        states = buf.attr['pattern-matcher-states']
        for state in states:
            if text in state:
                state = state[text]
                if callable(state):
                    m = buf.create_mark(None, it, True)
                    state(buf)
                    buf.attr['pattern-matcher-states'].clear()
                    it.assign(buf.get_iter_at_mark(m))
                    buf.delete_mark(m)
                    return
                else:
                    new_states.append(state)

        patterns = buf.attr['patterns']
        if text in patterns:
            new_states.append(patterns[text])

        buf.attr['pattern-matcher-states'] = new_states

    def update_matcher_state_on_delete(self, buf, start, end):
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
