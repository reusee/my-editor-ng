class CoreSelectionTransform:
    def __init__(self):

        self.emit('bind-command-key', ';', self.redo_transform)

        # cursor moves
        self.emit('bind-command-key', 'j', lambda view, n:
            self.view_get_cursor(view).transform(
                (self.mark_jump_relative_line_with_preferred_offset,
                    view, n if n != 0 else 1),
                'iter'))
        self.emit('bind-command-key', 'k', lambda view, n:
            self.view_get_cursor(view).transform(
                (self.mark_jump_relative_line_with_preferred_offset,
                    view, n if n != 0 else 1, True),
                'iter'))
        self.emit('bind-command-key', 'l', lambda view, n:
            self.view_get_cursor(view).transform(
                (self.mark_jump_relative_char,
                    view, n if n != 0 else 1),
                'iter'))
        self.emit('bind-command-key', 'h', lambda view, n:
            self.view_get_cursor(view).transform(
                (self.mark_jump_relative_char,
                    view, n if n != 0 else 1, True),
                'iter'))
        self.emit('bind-command-key', 'f', lambda view, n: lambda ev:
            self.view_get_cursor(view).transform(
                (self.mark_jump_to_string,
                    view, n if n != 0 else 1, chr(ev.get_keyval()[1])),
                'iter'))
        self.emit('bind-command-key', 'F', lambda view, n: lambda ev:
            self.view_get_cursor(view).transform(
                (self.mark_jump_to_string,
                    view, n if n != 0 else 1, chr(ev.get_keyval()[1]),
                    True),
                'iter'))
        self.emit('bind-command-key', 's', lambda view, n:
            lambda ev1: lambda ev2:
                self.view_get_cursor(view).transform(
                    (self.mark_jump_to_string,
                        view, n if n != 0 else 1,
                        chr(ev1.get_keyval()[1]) +
                        chr(ev2.get_keyval()[1])),
                    'iter'))
        self.emit('bind-command-key', 'S', lambda view, n:
            lambda ev1: lambda ev2:
                self.view_get_cursor(view).transform(
                    (self.mark_jump_to_string,
                        view, n if n != 0 else 1,
                        chr(ev1.get_keyval()[1]) +
                        chr(ev2.get_keyval()[1]), True),
                    'iter'))
        self.emit('bind-command-key', 'g g', lambda view, n:
            self.view_get_cursor(view).transform(
                (self.mark_jump_to_line_n,
                    view, n if n != 0 else 1),
                'iter'))
        self.emit('bind-command-key', 'G', lambda view, n:
            self.view_get_cursor(view).transform(
                (self.mark_jump_to_line_n,
                    view, view.get_buffer().get_line_count()),
                'iter'))
        self.emit('bind-command-key', 'R', lambda view, n:
            self.view_get_cursor(view).transform(
                (self.mark_jump_to_line_start_or_nonspace_char,
                    view, n if n != 0 else 1),
                'iter'))
        self.emit('bind-command-key', 'r', lambda view, n:
            self.view_get_cursor(view).transform(
                (self.mark_jump_to_line_end,
                    view, 0),
                'iter'))
        self.emit('bind-command-key', '[', lambda view, n:
            self.view_get_cursor(view).transform(
                (self.mark_jump_to_empty_line,
                    view, n if n != 0 else 1, True),
                'iter'))
        self.emit('bind-command-key', ']', lambda view, n:
            self.view_get_cursor(view).transform(
                (self.mark_jump_to_empty_line,
                    view, n if n != 0 else 1),
                'iter'))
        self.emit('bind-command-key', '%', lambda view, n:
            self.view_get_cursor(view).transform(
                (self.mark_jump_to_matching_bracket,
                    view, 0),
                'iter'))

        # selection moves
        self.emit('bind-command-key', ', j', lambda view, n:
            self.view_transform_all_selections(view,
                (self.mark_jump_relative_line_with_preferred_offset,
                    view, n if n != 0 else 1),
                'func'))
        self.emit('bind-command-key', ', k', lambda view, n:
            self.view_transform_all_selections(view,
                (self.mark_jump_relative_line_with_preferred_offset,
                    view, n if n != 0 else 1, True),
                'func'))
        self.emit('bind-command-key', ', h', lambda view, n:
            self.view_transform_all_selections(view,
                (self.mark_jump_relative_char,
                    view, n if n != 0 else 1, True),
                'func'))
        self.emit('bind-command-key', ', l', lambda view, n:
            self.view_transform_all_selections(view,
                (self.mark_jump_relative_char,
                    view, n if n != 0 else 1),
                'func'))

        # extends
        self.emit('bind-command-key', '. j', lambda view, n:
            self.view_transform_all_selections(view,
                (self.mark_jump_to_line_start, view, 1),
                (self.mark_jump_to_line_start, view,
                    n + 1 if n != 0 else 2)))
        self.command_key_handler['.']['d'], = (
            self.command_key_handler['.']['j'],)
        self.command_key_handler['.']['y'], = (
            self.command_key_handler['.']['j'],)
        self.emit('bind-command-key', '. k', lambda view, n:
            self.view_transform_all_selections(view,
                (self.mark_jump_to_line_start, view,
                    n if n != 0 else 1, True),
                (self.mark_jump_to_line_start, view, 2)))
        self.emit('bind-command-key', '. h', lambda view, n:
            self.view_transform_all_selections(view,
                (self.mark_jump_relative_char, view,
                    n if n != 0 else 1, True),
                None))
        self.emit('bind-command-key', '. l', lambda view, n:
            self.view_transform_all_selections(view,
                None,
                (self.mark_jump_relative_char, view,
                    n if n != 0 else 1)))
        self.emit('bind-command-key', '. f', lambda view, n: lambda ev:
            self.view_transform_all_selections(view,
                None,
                (self.mark_jump_to_string, view,
                    n if n != 0 else 1, chr(ev.get_keyval()[1]))))
        self.command_key_handler['.']['t'], = (
            self.command_key_handler['.']['f'],)
        self.emit('bind-command-key', '. F', lambda view, n: lambda ev:
            self.view_transform_all_selections(view,
                (self.mark_jump_to_string, view,
                    n if n != 0 else 1, chr(ev.get_keyval()[1]), True),
                None))
        self.emit('bind-command-key', '. s', lambda view, n:
            lambda ev1: lambda ev2:
                self.view_transform_all_selections(view,
                    None,
                    (self.mark_jump_to_string, view,
                        n if n != 0 else 1,
                        chr(ev1.get_keyval()[1])
                        + chr(ev2.get_keyval()[1]))))
        self.emit('bind-command-key', '. S', lambda view, n:
            lambda ev1: lambda ev2:
                self.view_transform_all_selections(view,
                    (self.mark_jump_to_string, view,
                        n if n != 0 else 1,
                        chr(ev1.get_keyval()[1])
                        + chr(ev2.get_keyval()[1]),
                        True),
                    None))
        self.emit('bind-command-key', '. w', lambda view, n:
            self.view_transform_all_selections(view,
                None,
                (self.mark_jump_to_word_edge, view, 0)))
        self.emit('bind-command-key', '. W', lambda view, n:
            self.view_transform_all_selections(view,
                (self.mark_jump_to_word_edge, view, 0, True),
                None))
        self.emit('bind-command-key', '. r', lambda view, n:
            self.view_transform_all_selections(view,
                None,
                (self.mark_jump_to_line_end, view, 0)))
        self.emit('bind-command-key', '. R', lambda view, n:
            self.view_transform_all_selections(view,
                (self.mark_jump_to_line_start_or_nonspace_char,
                    view, n if n != 0 else 1),
                None))
        self.emit('bind-command-key', '. [', lambda view, n:
            self.view_transform_all_selections(view,
                (self.mark_jump_to_empty_line, view,
                    n if n != 0 else 1, True),
                None))
        self.emit('bind-command-key', '. ]', lambda view, n:
            self.view_transform_all_selections(view,
                None,
                (self.mark_jump_to_empty_line, view,
                    n if n != 0 else 1)))
        self.emit('bind-command-key', '. i w', lambda view, n:
            self.view_transform_all_selections(view,
                (self.mark_jump_to_word_edge, view, 0, True),
                (self.mark_jump_to_word_edge, view, 0)))

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
            def f(view):
                self.view_transform_all_selections(view,
                    (self.selection_brackets_expand,
                        view.get_buffer(), left, right),
                    'single')
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

    def view_get_cursor(self, view):
        return view.get_buffer().attr['cursor']

    def view_transform_all_selections(self, view, start_func, end_func):
        buf = view.get_buffer()
        for sel in buf.attr['selections']:
            sel.transform(start_func, end_func)
        buf.attr['cursor'].transform(start_func, end_func)
        if buf.attr['delayed-selection-operation'] is not None:
            buf.attr['delayed-selection-operation']()
            buf.attr['delayed-selection-operation'] = None

    def redo_transform(self, view):
        buf = view.get_buffer()
        last_transform = buf.attr['last-transform']
        self.view_transform_all_selections(view, *last_transform)

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
