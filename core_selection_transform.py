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
            buf.attr['last-transform'].apply(buf),
            'redo last transform')

        # cursor moves
        self.bind_command_key('j', lambda buf, n: Transform(
            (self.mark_jump_relative_line_with_preferred_offset,
                n if n != 0 else 1),
            ('iter',), 'cursor').apply(buf),
            'relative forward line jump')
        self.bind_command_key('k', lambda buf, n: Transform(
            (self.mark_jump_relative_line_with_preferred_offset,
                n if n != 0 else 1, True),
            ('iter',), 'cursor').apply(buf),
            'relative backward line jump')
        self.bind_command_key('l', lambda buf, n: Transform(
            (self.mark_jump_relative_char,
                n if n != 0 else 1),
            ('iter',), 'cursor').apply(buf),
            'relative forward char jump')
        self.bind_command_key('h', lambda buf, n: Transform(
            (self.mark_jump_relative_char,
                n if n != 0 else 1, True),
            ('iter',), 'cursor').apply(buf),
            'relative backward char jump')
        self.bind_command_key('f', lambda buf, n: lambda keyval:
            Transform(
                (self.mark_jump_to_string,
                    n if n != 0 else 1, chr(keyval)),
                ('iter',), 'cursor').apply(buf),
            'specified forward char jump')
        self.bind_command_key('mf', lambda buf, n: lambda keyval:
            Transform(
                (self.mark_jump_to_string,
                    n if n != 0 else 1, chr(keyval),
                    True),
                ('iter',), 'cursor').apply(buf),
            'specified backward char jump')
        self.bind_command_key('s', lambda buf, n:
            lambda keyval1: lambda keyval2: Transform(
                (self.mark_jump_to_string,
                    n if n != 0 else 1,
                    chr(keyval1) +
                    chr(keyval2)),
                ('iter',), 'cursor').apply(buf),
            'specified forward two-chars jump')
        self.bind_command_key('ms', lambda buf, n:
            lambda keyval1: lambda keyval2: Transform(
                (self.mark_jump_to_string,
                    n if n != 0 else 1,
                    chr(keyval1) +
                    chr(keyval2), True),
                ('iter',), 'cursor').apply(buf),
            'specified backward two-chars jump')
        self.bind_command_key('gg', lambda buf, n: Transform(
            (self.mark_jump_to_line_n,
                n if n != 0 else 1),
            ('iter',), 'cursor').apply(buf),
            'specified line jump')
        self.bind_command_key('G', lambda buf, n: Transform(
            (self.mark_jump_to_line_n,
                buf.get_line_count()),
            ('iter',), 'cursor').apply(buf),
            'jump to end of buffer')
        self.bind_command_key('mr', lambda buf, n: Transform(
            (self.mark_jump_to_line_start_or_nonspace_char,
                n if n != 0 else 1),
            ('iter',), 'cursor').apply(buf),
            'jump to line start of first non-space char')
        self.bind_command_key('r', lambda buf, n: Transform(
            (self.mark_jump_to_line_end, 0),
            ('iter',), 'cursor').apply(buf),
            'jump to line end')
        self.bind_command_key('[', lambda buf, n: Transform(
            (self.mark_jump_to_empty_line,
                n if n != 0 else 1, True),
            ('iter',), 'cursor').apply(buf),
            'jump to previous empty line')
        self.bind_command_key(']', lambda buf, n: Transform(
            (self.mark_jump_to_empty_line,
                n if n != 0 else 1),
            ('iter',), 'cursor').apply(buf),
            'jump to next empty line')
        self.bind_command_key('%', lambda buf, n: Transform(
            (self.mark_jump_to_matching_bracket, 0),
            ('iter',), 'cursor').apply(buf),
            'jump to matching bracket')

        # selection moves
        self.bind_command_key(',j', lambda buf, n: Transform(
            (self.mark_jump_relative_line_with_preferred_offset,
                n if n != 0 else 1),
            ('func',), 'all').apply(buf),
            'relative forward line jump of all selections')
        self.bind_command_key(',k', lambda buf, n: Transform(
            (self.mark_jump_relative_line_with_preferred_offset,
                n if n != 0 else 1, True),
            ('func',), 'all').apply(buf),
            'relative backward line jump of all selections')
        self.bind_command_key(',h', lambda buf, n: Transform(
            (self.mark_jump_relative_char,
                n if n != 0 else 1, True),
            ('func',), 'all').apply(buf),
            'relative backward char jump of all selections')
        self.bind_command_key(',l', lambda buf, n: Transform(
            (self.mark_jump_relative_char,
                n if n != 0 else 1),
            ('func',), 'all').apply(buf),
            'relative forward char jump of all selections')
        self.bind_command_key(',r', lambda buf, n: Transform(
            (self.mark_jump_to_line_end, 0),
            ('func',), 'all').apply(buf),
            'all selection cursors jump to line end')
        self.bind_command_key(',mr', lambda buf, n: Transform(
            (self.mark_jump_to_line_start_or_nonspace_char,
                n if n != 0 else 1),
            ('func',), 'all').apply(buf),
            'all selection cursors jump to line start of first non-space char')

        # extends
        self.bind_command_key('vj', lambda buf, n: Transform(
            (self.mark_jump_to_line_start, 1),
            (self.mark_jump_to_line_start,
                n + 1 if n != 0 else 2), 'all').apply(buf),
            'relative forward line extend')
        self.alias_command_key('vd', 'vj')
        self.alias_command_key('vy', 'vj')
        self.bind_command_key('vk', lambda buf, n: Transform(
            (self.mark_jump_to_line_start,
                n if n != 0 else 1, True),
            (self.mark_jump_to_line_start, 2), 'all').apply(buf),
            'relative backward line extend')
        self.bind_command_key('vh', lambda buf, n: Transform(
            (self.mark_jump_relative_char,
                n if n != 0 else 1, True),
            (None,), 'all').apply(buf),
            'relative backward char extend')
        self.bind_command_key('vl', lambda buf, n: Transform(
            (None,),
            (self.mark_jump_relative_char,
                n if n != 0 else 1), 'all').apply(buf),
            'relative forward char extend')
        self.bind_command_key('vf', lambda buf, n: lambda keyval:
            Transform(
                (None,),
                (self.mark_jump_to_string,
                    n if n != 0 else 1, chr(keyval)),
                'all').apply(buf),
            'specified forward char extend')
        self.alias_command_key('vt', 'vf')
        self.bind_command_key('vmf', lambda buf, n: lambda keyval:
            Transform(
                (self.mark_jump_to_string,
                    n if n != 0 else 1, chr(keyval), True),
                (None,), 'all').apply(buf),
            'specified backward char extend')
        self.bind_command_key('vs', lambda buf, n:
            lambda keyval1: lambda keyval2: Transform(
                (None,),
                (self.mark_jump_to_string,
                    n if n != 0 else 1,
                    chr(keyval1)
                    + chr(keyval2)),
                'all').apply(buf),
            'specified forward two-chars extend')
        self.bind_command_key('vms', lambda buf, n:
            lambda keyval1: lambda keyval2: Transform(
                (self.mark_jump_to_string,
                    n if n != 0 else 1,
                    chr(keyval1)
                    + chr(keyval2),
                    True),
                (None,), 'all').apply(buf),
            'specified backward two-chars extend')
        self.bind_command_key('vw', lambda buf, n: Transform(
            (None,),
            (self.mark_jump_to_word_edge, 0), 'all').apply(buf),
            'relative forward word extend')
        self.bind_command_key('vmw', lambda buf, n: Transform(
            (self.mark_jump_to_word_edge, 0, True),
            (None,), 'all').apply(buf),
            'relative backward word extend')
        self.bind_command_key('vr', lambda buf, n: Transform(
            (None,),
            (self.mark_jump_to_line_end, 0), 'all').apply(buf),
            'extend to line end')
        self.bind_command_key('vmr', lambda buf, n: Transform(
            (self.mark_jump_to_line_start_or_nonspace_char,
                n if n != 0 else 1),
            (None,), 'all').apply(buf),
            'extend to line start or first non-space char')
        self.bind_command_key('v[', lambda buf, n: Transform(
            (self.mark_jump_to_empty_line,
                n if n != 0 else 1, True),
            (None,), 'all').apply(buf),
            'extend to previous empty line')
        self.bind_command_key('v]', lambda buf, n: Transform(
            (None,),
            (self.mark_jump_to_empty_line,
                n if n != 0 else 1), 'all').apply(buf),
            'extend to next empty line')
        self.bind_command_key('viw', lambda buf, n: Transform(
            (self.mark_jump_to_word_edge, 0, True),
            (self.mark_jump_to_word_edge, 0), 'all').apply(buf),
            'extend inside current word')
        self.bind_command_key('vb', lambda buf, n: Transform(
            (None,),
            (self.mark_jump_to_indent_block_edge, 0),
            'all').apply(buf),
            'extend to end of indentation block')
        self.bind_command_key('vmb', lambda buf, n: Transform(
            (self.mark_jump_to_indent_block_edge, 0, True),
            (None,),
            'all').apply(buf),
            'extend to start of indentation block')
        self.bind_command_key('vib', lambda buf, n: Transform(
            (self.mark_jump_to_indent_block_edge, 0, True),
            (self.mark_jump_to_indent_block_edge, 0),
            'all').apply(buf),
            'extend inside indentation block')
        self.bind_command_key('v%', lambda buf, n: Transform(
            (None,),
            (self.mark_jump_to_matching_bracket, 0),
            'all').apply(buf),
            'forward extend to matching bracket')

        self.selection_extend_handler = self.get_command_key('v')

        # numeric prefix in selection extend
        def make_prefix_handler(i):
            def f():
                self.n = self.n * 10 + i
                return self.selection_extend_handler
            return f
        for i in range(0, 10):
            self.bind_command_key('v' + str(i), make_prefix_handler(i),
                'numeric prefix')

        # brackets in selection extend
        def make_expander(left, right, around):
            def f(buf):
                Transform(
                    (self.selection_brackets_expand, left, right, around),
                    ('single',), 'all').apply(buf)
            return f
        for left, right in self.BRACKETS.items():
            self.bind_command_key('vi' + left,
                make_expander(left, right, False), 'extend inside ' + left + right)
            self.bind_command_key('va' + left,
                make_expander(left, right, True), 'extend around ' + left + right)
            if right == left: continue
            self.bind_command_key('vi' + right,
                make_expander(left, right, False), 'extend inside ' + left + right)
            self.bind_command_key('va' + right,
                make_expander(left, right, True), 'extend around ' + left + right)

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
