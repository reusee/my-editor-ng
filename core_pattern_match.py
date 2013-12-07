class CorePatternMatch:
    def __init__(self):
        self.connect('buffer-created', self.setup_pattern_matcher)

    def setup_pattern_matcher(self, _, buf):
        buf.attr['patterns'] = {}
        buf.attr['pattern-matcher-states'] = []
        buf.connect('insert-text', self.update_matcher_state_on_insert)
        buf.connect('delete-range', self.update_matcher_state_on_delete)

        self.add_pattern(buf, 'foo', lambda _: True, lambda _: print('here'))

    def update_matcher_state_on_insert(self, buf, it, text, length):
        new_states = []
        # update current state
        # new state
        states = buf.attr['pattern-matcher-states']
        for state in states:
            if text in state:
                state = state[text]
                if isinstance(state, tuple): # stop state
                    predict, callback = state
                    if predict(buf): callback(buf)
                else:
                    new_states.append(state)

        patterns = buf.attr['patterns']
        if text in patterns:
            new_states.append(patterns[text])

        buf.attr['pattern-matcher-states'] = new_states
        print(new_states)

    def update_matcher_state_on_delete(self, buf, start, end):
        buf.attr['pattern-matcher-states'].clear()

    def add_pattern(self, buf, pattern, predict, callback):
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
        cur[key] = (predict, callback)
