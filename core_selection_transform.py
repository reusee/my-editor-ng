class Transform:
    def __init__(self, start_func, end_func, target):
        self.start_func = start_func[0]
        self.start_args = start_func[1:]
        self.end_func = end_func[0]
        self.end_args = end_func[1:]
        self.target = target

    def apply(self, buf):
        buf.attr['current-transform'] = self
        targets = [buf.attr['cursor']]
        if self.target == 'all':
            targets += buf.attr['selections']
        for sel in targets:
            if self.end_func == 'single': # single param of Selection
                self.start_func(sel, buf, *self.start_args)
            else:
                if self.start_func is not None:
                    it = self.start_func(sel.start, buf, *self.start_args)
                if self.end_func == 'func':
                    self.start_func(sel.end, buf, *self.start_args)
                elif self.end_func == 'iter':
                    buf.move_mark(sel.end, it)
                elif self.end_func is not None:
                    self.end_func(sel.end, buf, *self.end_args)
        if buf.attr['delayed-selection-operation'] is not None:
            buf.begin_user_action()
            buf.attr['delayed-selection-operation']()
            buf.end_user_action()
            buf.attr['delayed-selection-operation'] = None
        buf.attr['last-transform'] = self

class CoreSelectionTransform:
    def __init__(self):

        self.bind_command_key(';', lambda buf:
            buf.attr['last-transform'].apply(buf))

        # cursor moves
        self.bind_command_key('j', lambda buf, n: Transform(
            (self.mark_jump_relative_line_with_preferred_offset,
                n if n != 0 else 1),
            ('iter',), 'cursor').apply(buf))
        self.bind_command_key('k', lambda buf, n: Transform(
            (self.mark_jump_relative_line_with_preferred_offset,
                n if n != 0 else 1, True),
            ('iter',), 'cursor').apply(buf))
        self.bind_command_key('l', lambda buf, n: Transform(
            (self.mark_jump_relative_char,
                n if n != 0 else 1),
            ('iter',), 'cursor').apply(buf))
        self.bind_command_key('h', lambda buf, n: Transform(
            (self.mark_jump_relative_char,
                n if n != 0 else 1, True),
            ('iter',), 'cursor').apply(buf))
        self.bind_command_key('f', lambda buf, n: lambda ev:
            Transform(
                (self.mark_jump_to_string,
                    n if n != 0 else 1, chr(ev.get_keyval()[1])),
                ('iter',), 'cursor').apply(buf))
        self.bind_command_key('mf', lambda buf, n: lambda ev:
            Transform(
                (self.mark_jump_to_string,
                    n if n != 0 else 1, chr(ev.get_keyval()[1]),
                    True),
                ('iter',), 'cursor').apply(buf))
        self.bind_command_key('s', lambda buf, n:
            lambda ev1: lambda ev2: Transform(
                (self.mark_jump_to_string,
                    n if n != 0 else 1,
                    chr(ev1.get_keyval()[1]) +
                    chr(ev2.get_keyval()[1])),
                ('iter',), 'cursor').apply(buf))
        self.bind_command_key('ms', lambda buf, n:
            lambda ev1: lambda ev2: Transform(
                (self.mark_jump_to_string,
                    n if n != 0 else 1,
                    chr(ev1.get_keyval()[1]) +
                    chr(ev2.get_keyval()[1]), True),
                ('iter',), 'cursor').apply(buf))
        self.bind_command_key('gg', lambda buf, n: Transform(
            (self.mark_jump_to_line_n,
                n if n != 0 else 1),
            ('iter',), 'cursor').apply(buf))
        self.bind_command_key('G', lambda buf, n: Transform(
            (self.mark_jump_to_line_n,
                buf.get_line_count()),
            ('iter',), 'cursor').apply(buf))
        self.bind_command_key('mr', lambda buf, n: Transform(
            (self.mark_jump_to_line_start_or_nonspace_char,
                n if n != 0 else 1),
            ('iter',), 'cursor').apply(buf))
        self.bind_command_key('r', lambda buf, n: Transform(
            (self.mark_jump_to_line_end, 0),
            ('iter',), 'cursor').apply(buf))
        self.bind_command_key('[', lambda buf, n: Transform(
            (self.mark_jump_to_empty_line,
                n if n != 0 else 1, True),
            ('iter',), 'cursor').apply(buf))
        self.bind_command_key(']', lambda buf, n: Transform(
            (self.mark_jump_to_empty_line,
                n if n != 0 else 1),
            ('iter',), 'cursor').apply(buf))
        self.bind_command_key('%', lambda buf, n: Transform(
            (self.mark_jump_to_matching_bracket, 0),
            ('iter',), 'cursor').apply(buf))

        # selection moves
        self.bind_command_key(',j', lambda buf, n: Transform(
            (self.mark_jump_relative_line_with_preferred_offset,
                n if n != 0 else 1),
            ('func',), 'all').apply(buf))
        self.bind_command_key(',k', lambda buf, n: Transform(
            (self.mark_jump_relative_line_with_preferred_offset,
                n if n != 0 else 1, True),
            ('func',), 'all').apply(buf))
        self.bind_command_key(',h', lambda buf, n: Transform(
            (self.mark_jump_relative_char,
                n if n != 0 else 1, True),
            ('func',), 'all').apply(buf))
        self.bind_command_key(',l', lambda buf, n: Transform(
            (self.mark_jump_relative_char,
                n if n != 0 else 1),
            ('func',), 'all').apply(buf))

        # extends
        self.bind_command_key('vj', lambda buf, n: Transform(
            (self.mark_jump_to_line_start, 1),
            (self.mark_jump_to_line_start,
                n + 1 if n != 0 else 2), 'all').apply(buf))
        self.command_key_handler['v']['d'], = (
            self.command_key_handler['v']['j'],)
        self.command_key_handler['v']['y'], = (
            self.command_key_handler['v']['j'],)
        self.bind_command_key('vk', lambda buf, n: Transform(
            (self.mark_jump_to_line_start,
                n if n != 0 else 1, True),
            (self.mark_jump_to_line_start, 2), 'all').apply(buf))
        self.bind_command_key('vh', lambda buf, n: Transform(
            (self.mark_jump_relative_char,
                n if n != 0 else 1, True),
            (None,), 'all').apply(buf))
        self.bind_command_key('vl', lambda buf, n: Transform(
            (None,),
            (self.mark_jump_relative_char,
                n if n != 0 else 1), 'all').apply(buf))
        self.bind_command_key('vf', lambda buf, n: lambda ev:
            Transform(
                (None,),
                (self.mark_jump_to_string,
                    n if n != 0 else 1, chr(ev.get_keyval()[1])),
                'all').apply(buf))
        self.command_key_handler['v']['t'], = (
            self.command_key_handler['v']['f'],)
        self.bind_command_key('vmf', lambda buf, n: lambda ev:
            Transform(
                (self.mark_jump_to_string,
                    n if n != 0 else 1, chr(ev.get_keyval()[1]), True),
                (None,), 'all').apply(buf))
        self.bind_command_key('vs', lambda buf, n:
            lambda ev1: lambda ev2: Transform(
                (None,),
                (self.mark_jump_to_string,
                    n if n != 0 else 1,
                    chr(ev1.get_keyval()[1])
                    + chr(ev2.get_keyval()[1])),
                'all').apply(buf))
        self.bind_command_key('vms', lambda buf, n:
            lambda ev1: lambda ev2: Transform(
                (self.mark_jump_to_string,
                    n if n != 0 else 1,
                    chr(ev1.get_keyval()[1])
                    + chr(ev2.get_keyval()[1]),
                    True),
                (None,), 'all').apply(buf))
        self.bind_command_key('vw', lambda buf, n: Transform(
            (None,),
            (self.mark_jump_to_word_edge, 0), 'all').apply(buf))
        self.bind_command_key('vmw', lambda buf, n: Transform(
            (self.mark_jump_to_word_edge, 0, True),
            (None,), 'all').apply(buf))
        self.bind_command_key('vr', lambda buf, n: Transform(
            (None,),
            (self.mark_jump_to_line_end, 0), 'all').apply(buf))
        self.bind_command_key('vmr', lambda buf, n: Transform(
            (self.mark_jump_to_line_start_or_nonspace_char,
                n if n != 0 else 1),
            (None,), 'all').apply(buf))
        self.bind_command_key('v[', lambda buf, n: Transform(
            (self.mark_jump_to_empty_line,
                n if n != 0 else 1, True),
            (None,), 'all').apply(buf))
        self.bind_command_key('v]', lambda buf, n: Transform(
            (None,),
            (self.mark_jump_to_empty_line,
                n if n != 0 else 1), 'all').apply(buf))
        self.bind_command_key('viw', lambda buf, n: Transform(
            (self.mark_jump_to_word_edge, 0, True),
            (self.mark_jump_to_word_edge, 0), 'all').apply(buf))

        self.selection_extend_handler = self.command_key_handler['v']

        # numeric prefix in selection extend
        def make_prefix_handler(i):
            def f():
                self.n = self.n * 10 + i
                return self.selection_extend_handler
            return f
        for i in range(0, 10):
            self.selection_extend_handler[str(i)] = make_prefix_handler(i)

        # brackets in selection extend
        def make_expander(left, right, around):
            def f(buf):
                Transform(
                    (self.selection_brackets_expand, left, right, around),
                    ('single',), 'all').apply(buf)
            return f
        for left, right in self.BRACKETS.items():
            self.bind_command_key('vi' + left,
                make_expander(left, right, False))
            self.bind_command_key('va' + left,
                make_expander(left, right, True))
            if right == left: continue
            self.bind_command_key('vi' + right,
                make_expander(left, right, False))
            self.bind_command_key('va' + right,
                make_expander(left, right, True))

    def selection_brackets_expand(self, sel, buf, left, right,
        around = False):
        start = buf.get_iter_at_mark(sel.end)
        end = start.copy()

        balance = 0
        start.backward_char()
        found = False
        while True:
            c = start.get_char()
            if c == left and balance == 0:
                found = True
                break
            elif c == left:
                balance -= 1
            elif c == right:
                balance += 1
            if not start.backward_char():
                break
        if not found: return
        if not around: start.forward_char()

        balance = 0
        found = False
        while True:
            c = end.get_char()
            if c == right and balance == 0:
                found = True
                break
            elif c == right:
                balance -= 1
            elif c == left:
                balance += 1
            if not end.forward_char():
                break
        if not found: return
        if around: end.forward_char()

        buf.move_mark(sel.start, start)
        buf.move_mark(sel.end, end)
