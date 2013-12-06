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

        self.emit('bind-command-key', ';', lambda buf:
            buf.attr['last-transform'].apply(buf))

        # cursor moves
        self.emit('bind-command-key', 'j', lambda buf, n: Transform(
            (self.mark_jump_relative_line_with_preferred_offset,
                n if n != 0 else 1),
            ('iter',), 'cursor').apply(buf))
        self.emit('bind-command-key', 'k', lambda buf, n: Transform(
            (self.mark_jump_relative_line_with_preferred_offset,
                n if n != 0 else 1, True),
            ('iter',), 'cursor').apply(buf))
        self.emit('bind-command-key', 'l', lambda buf, n: Transform(
            (self.mark_jump_relative_char,
                n if n != 0 else 1),
            ('iter',), 'cursor').apply(buf))
        self.emit('bind-command-key', 'h', lambda buf, n: Transform(
            (self.mark_jump_relative_char,
                n if n != 0 else 1, True),
            ('iter',), 'cursor').apply(buf))
        self.emit('bind-command-key', 'f', lambda buf, n: lambda ev:
            Transform(
                (self.mark_jump_to_string,
                    n if n != 0 else 1, chr(ev.get_keyval()[1])),
                ('iter',), 'cursor').apply(buf))
        self.emit('bind-command-key', 'F', lambda buf, n: lambda ev:
            Transform(
                (self.mark_jump_to_string,
                    n if n != 0 else 1, chr(ev.get_keyval()[1]),
                    True),
                ('iter',), 'cursor').apply(buf))
        self.emit('bind-command-key', 's', lambda buf, n:
            lambda ev1: lambda ev2: Transform(
                (self.mark_jump_to_string,
                    n if n != 0 else 1,
                    chr(ev1.get_keyval()[1]) +
                    chr(ev2.get_keyval()[1])),
                ('iter',), 'cursor').apply(buf))
        self.emit('bind-command-key', 'S', lambda buf, n:
            lambda ev1: lambda ev2: Transform(
                (self.mark_jump_to_string,
                    n if n != 0 else 1,
                    chr(ev1.get_keyval()[1]) +
                    chr(ev2.get_keyval()[1]), True),
                ('iter',), 'cursor').apply(buf))
        self.emit('bind-command-key', 'g g', lambda buf, n: Transform(
            (self.mark_jump_to_line_n,
                n if n != 0 else 1),
            ('iter',), 'cursor').apply(buf))
        self.emit('bind-command-key', 'G', lambda buf, n: Transform(
            (self.mark_jump_to_line_n,
                buf.get_line_count()),
            ('iter',), 'cursor').apply(buf))
        self.emit('bind-command-key', 'R', lambda buf, n: Transform(
            (self.mark_jump_to_line_start_or_nonspace_char,
                n if n != 0 else 1),
            ('iter',), 'cursor').apply(buf))
        self.emit('bind-command-key', 'r', lambda buf, n: Transform(
            (self.mark_jump_to_line_end, 0),
            ('iter',), 'cursor').apply(buf))
        self.emit('bind-command-key', '[', lambda buf, n: Transform(
            (self.mark_jump_to_empty_line,
                n if n != 0 else 1, True),
            ('iter',), 'cursor').apply(buf))
        self.emit('bind-command-key', ']', lambda buf, n: Transform(
            (self.mark_jump_to_empty_line,
                n if n != 0 else 1),
            ('iter',), 'cursor').apply(buf))
        self.emit('bind-command-key', '%', lambda buf, n: Transform(
            (self.mark_jump_to_matching_bracket, 0),
            ('iter',), 'cursor').apply(buf))

        # selection moves
        self.emit('bind-command-key', ', j', lambda buf, n: Transform(
            (self.mark_jump_relative_line_with_preferred_offset,
                n if n != 0 else 1),
            ('func',), 'all').apply(buf))
        self.emit('bind-command-key', ', k', lambda buf, n: Transform(
            (self.mark_jump_relative_line_with_preferred_offset,
                n if n != 0 else 1, True),
            ('func',), 'all').apply(buf))
        self.emit('bind-command-key', ', h', lambda buf, n: Transform(
            (self.mark_jump_relative_char,
                n if n != 0 else 1, True),
            ('func',), 'all').apply(buf))
        self.emit('bind-command-key', ', l', lambda buf, n: Transform(
            (self.mark_jump_relative_char,
                n if n != 0 else 1),
            ('func',), 'all').apply(buf))

        # extends
        self.emit('bind-command-key', '. j', lambda buf, n: Transform(
            (self.mark_jump_to_line_start, 1),
            (self.mark_jump_to_line_start,
                n + 1 if n != 0 else 2), 'all').apply(buf))
        self.command_key_handler['.']['d'], = (
            self.command_key_handler['.']['j'],)
        self.command_key_handler['.']['y'], = (
            self.command_key_handler['.']['j'],)
        self.emit('bind-command-key', '. k', lambda buf, n: Transform(
            (self.mark_jump_to_line_start,
                n if n != 0 else 1, True),
            (self.mark_jump_to_line_start, 2), 'all').apply(buf))
        self.emit('bind-command-key', '. h', lambda buf, n: Transform(
            (self.mark_jump_relative_char,
                n if n != 0 else 1, True),
            (None,), 'all').apply(buf))
        self.emit('bind-command-key', '. l', lambda buf, n: Transform(
            (None,),
            (self.mark_jump_relative_char,
                n if n != 0 else 1), 'all').apply(buf))
        self.emit('bind-command-key', '. f', lambda buf, n: lambda ev:
            Transform(
                (None,),
                (self.mark_jump_to_string,
                    n if n != 0 else 1, chr(ev.get_keyval()[1])),
                'all').apply(buf))
        self.command_key_handler['.']['t'], = (
            self.command_key_handler['.']['f'],)
        self.emit('bind-command-key', '. F', lambda buf, n: lambda ev:
            Transform(
                (self.mark_jump_to_string,
                    n if n != 0 else 1, chr(ev.get_keyval()[1]), True),
                (None,), 'all').apply(buf))
        self.emit('bind-command-key', '. s', lambda buf, n:
            lambda ev1: lambda ev2: Transform(
                (None,),
                (self.mark_jump_to_string,
                    n if n != 0 else 1,
                    chr(ev1.get_keyval()[1])
                    + chr(ev2.get_keyval()[1])),
                'all').apply(buf))
        self.emit('bind-command-key', '. S', lambda buf, n:
            lambda ev1: lambda ev2: Transform(
                (self.mark_jump_to_string,
                    n if n != 0 else 1,
                    chr(ev1.get_keyval()[1])
                    + chr(ev2.get_keyval()[1]),
                    True),
                (None,), 'all').apply(buf))
        self.emit('bind-command-key', '. w', lambda buf, n: Transform(
            (None,),
            (self.mark_jump_to_word_edge, 0), 'all').apply(buf))
        self.emit('bind-command-key', '. W', lambda buf, n: Transform(
            (self.mark_jump_to_word_edge, 0, True),
            (None,), 'all').apply(buf))
        self.emit('bind-command-key', '. r', lambda buf, n: Transform(
            (None,),
            (self.mark_jump_to_line_end, 0), 'all').apply(buf))
        self.emit('bind-command-key', '. R', lambda buf, n: Transform(
            (self.mark_jump_to_line_start_or_nonspace_char,
                n if n != 0 else 1),
            (None,), 'all').apply(buf))
        self.emit('bind-command-key', '. [', lambda buf, n: Transform(
            (self.mark_jump_to_empty_line,
                n if n != 0 else 1, True),
            (None,), 'all').apply(buf))
        self.emit('bind-command-key', '. ]', lambda buf, n: Transform(
            (None,),
            (self.mark_jump_to_empty_line,
                n if n != 0 else 1), 'all').apply(buf))
        self.emit('bind-command-key', '. i w', lambda buf, n: Transform(
            (self.mark_jump_to_word_edge, 0, True),
            (self.mark_jump_to_word_edge, 0), 'all').apply(buf))

        self.selection_extend_handler = self.command_key_handler['.']

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
            self.emit('bind-command-key', '. i ' + left,
                make_expander(left, right, False))
            self.emit('bind-command-key', '. a ' + left,
                make_expander(left, right, True))
            if right == left: continue
            self.emit('bind-command-key', '. i ' + right,
                make_expander(left, right, False))
            self.emit('bind-command-key', '. a ' + right,
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
