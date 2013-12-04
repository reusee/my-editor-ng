class CoreSelectionTransform:
    def __init__(self):

        # moves
        self.emit('bind-command-key', 'j', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_relative_line_with_preferred_offset(
                    m, view, n if n != 0 else 1),
                'iter'))
        self.emit('bind-command-key', 'k', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_relative_line_with_preferred_offset(
                    m, view, n if n != 0 else 1, backward = True),
                'iter'))
        self.emit('bind-command-key', 'l', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_relative_char(
                    m, view, n if n != 0 else 1),
                'iter'))
        self.emit('bind-command-key', 'h', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_relative_char(
                    m, view, n if n != 0 else 1, backward = True),
                'iter'))
        self.emit('bind-command-key', 'f', lambda view, n: lambda ev:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_to_string(
                    m, view, n if n != 0 else 1, chr(ev.get_keyval()[1])),
                'iter'))
        self.emit('bind-command-key', 'F', lambda view, n: lambda ev:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_to_string(
                    m, view, n if n != 0 else 1, chr(ev.get_keyval()[1]),
                    backward = True),
                'iter'))
        self.emit('bind-command-key', 's', lambda view, n:
            lambda ev1: lambda ev2:
                self.view_get_cursor(view).transform(lambda m:
                    self.mark_jump_to_string(m, view, n if n != 0 else 1,
                        chr(ev1.get_keyval()[1]) +
                        chr(ev2.get_keyval()[1])),
                    'iter'))
        self.emit('bind-command-key', 'S', lambda view, n:
            lambda ev1: lambda ev2:
                self.view_get_cursor(view).transform(lambda m:
                    self.mark_jump_to_string(m, view, n if n != 0 else 1,
                        chr(ev1.get_keyval()[1]) +
                        chr(ev2.get_keyval()[1]), backward = True),
                    'iter'))
        self.emit('bind-command-key', 'g g', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_to_line_n(
                    m, view, n if n != 0 else 1),
                'iter'))
        self.emit('bind-command-key', 'G', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_to_line_n(
                    m, view, view.get_buffer().get_line_count()),
                'iter'))
        self.emit('bind-command-key', 'R', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_to_line_start_or_nonspace_char(
                    m, view, n if n != 0 else 1),
                'iter'))
        self.emit('bind-command-key', 'r', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_to_line_end(
                    m, view, 0),
                'iter'))
        self.emit('bind-command-key', '[', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_to_empty_line(
                    m, view, n if n != 0 else 1, backward = True),
                'iter'))
        self.emit('bind-command-key', ']', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_to_empty_line(
                    m, view, n if n != 0 else 1),
                'iter'))
        self.emit('bind-command-key', '%', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_to_matching_bracket(
                    m, view, 0),
                'iter'))

        # extends
        self.emit('bind-command-key', '. j', lambda view, n:
            self.view_transform_all_selections(view,
                lambda m: self.mark_jump_to_line_start(m, view, 1),
                lambda m: self.mark_jump_to_line_start(m, view,
                    n + 1 if n != 0 else 2)))
        self.emit('bind-command-key', '. k', lambda view, n:
            self.view_transform_all_selections(view,
                lambda m: self.mark_jump_to_line_start(m, view,
                    n if n != 0 else 1, backward = True),
                lambda m: self.mark_jump_to_line_start(m, view, 2)))
        self.emit('bind-command-key', '. h', lambda view, n:
            self.view_transform_all_selections(view,
                lambda m: self.mark_jump_relative_char(m, view,
                    n if n != 0 else 1, backward = True),
                None))
        self.emit('bind-command-key', '. l', lambda view, n:
            self.view_transform_all_selections(view,
                None,
                lambda m: self.mark_jump_relative_char(m, view,
                    n if n != 0 else 1)))
        self.emit('bind-command-key', '. f', lambda view, n: lambda ev:
            self.view_transform_all_selections(view,
                None,
                lambda m: self.mark_jump_to_string(m, view,
                    n if n != 0 else 1, chr(ev.get_keyval()[1]))))
        self.command_key_handler['.']['t'] = self.command_key_handler['.']['f']
        self.emit('bind-command-key', '. F', lambda view, n: lambda ev:
            self.view_transform_all_selections(view,
                lambda m: self.mark_jump_to_string(m, view,
                    n if n != 0 else 1, chr(ev.get_keyval()[1]),
                    backward = True),
                None))
        self.emit('bind-command-key', '. s', lambda view, n:
            lambda ev1: lambda ev2:
                self.view_transform_all_selections(view,
                    None,
                    lambda m: self.mark_jump_to_string(m, view,
                        n if n != 0 else 1,
                        chr(ev1.get_keyval()[1])
                        + chr(ev2.get_keyval()[1]))))
        self.emit('bind-command-key', '. S', lambda view, n:
            lambda ev1: lambda ev2:
                self.view_transform_all_selections(view,
                    lambda m: self.mark_jump_to_string(m, view,
                        n if n != 0 else 1,
                        chr(ev1.get_keyval()[1])
                        + chr(ev2.get_keyval()[1]),
                        backward = True),
                    None))
        self.emit('bind-command-key', '. w', lambda view, n:
            self.view_transform_all_selections(view,
                None,
                lambda m: self.mark_jump_to_word_edge(m, view, 0)))
        self.emit('bind-command-key', '. W', lambda view, n:
            self.view_transform_all_selections(view,
                lambda m: self.mark_jump_to_word_edge(m, view, 0,
                    backward = True),
                None))
        self.emit('bind-command-key', '. r', lambda view, n:
            self.view_transform_all_selections(view,
                None,
                lambda m: self.mark_jump_to_line_end(m, view, 0)))
        self.emit('bind-command-key', '. R', lambda view, n:
            self.view_transform_all_selections(view,
                lambda m: self.mark_jump_to_line_start_or_nonspace_char(
                    m, view, n if n != 0 else 1),
                None))
        self.emit('bind-command-key', '. i w', lambda view, n:
            self.view_transform_all_selections(view,
                lambda m: self.mark_jump_to_word_edge(m, view, 0,
                    backward = True),
                lambda m: self.mark_jump_to_word_edge(m, view, 0)))

        self.selection_extend_handler = self.command_key_handler['.']

        def make_prefix_handler(i):
            def f():
                self.n = self.n * 10 + i
                return self.selection_extend_handler
            return f

        for i in range(0, 10):
            self.selection_extend_handler[str(i)] = make_prefix_handler(i)

    def view_get_cursor(self, view):
        return view.get_buffer().attr['cursor']

    def view_transform_all_selections(self, view, start_func, end_func):
        buf = view.get_buffer()
        for sel in buf.attr['selections']:
            sel.transform(start_func, end_func)
        buf.attr['cursor'].transform(start_func, end_func)
        if buf.attr['queue-operation'] is not None:
            buf.attr['queue-operation']()
            buf.attr['queue-operation'] = None
