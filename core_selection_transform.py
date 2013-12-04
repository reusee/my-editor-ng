class CoreSelectionTransform:
    def __init__(self):
        self.emit('bind-command-key', 'j', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_relative_line_with_preferred_offset(
                    m, view, n if n != 0 else 1),
                True))
        self.emit('bind-command-key', 'k', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_relative_line_with_preferred_offset(
                    m, view, n if n != 0 else 1, backward = True),
                True))
        self.emit('bind-command-key', 'l', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_relative_char(
                    m, view, n if n != 0 else 1),
                True))
        self.emit('bind-command-key', 'h', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_relative_char(
                    m, view, n if n != 0 else 1, backward = True),
                True))
        self.emit('bind-command-key', 'f', lambda view, n: lambda ev:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_to_string(
                    m, view, n if n != 0 else 1, chr(ev.get_keyval()[1])),
                True))
        self.emit('bind-command-key', 'F', lambda view, n: lambda ev:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_to_string(
                    m, view, n if n != 0 else 1, chr(ev.get_keyval()[1]),
                    backward = True),
                True))
        self.emit('bind-command-key', 's', lambda view, n:
            lambda ev1: lambda ev2:
                self.view_get_cursor(view).transform(lambda m:
                    self.mark_jump_to_string(m, view, n if n != 0 else 1,
                        chr(ev1.get_keyval()[1]) +
                        chr(ev2.get_keyval()[1])),
                    True))
        self.emit('bind-command-key', 'S', lambda view, n:
            lambda ev1: lambda ev2:
                self.view_get_cursor(view).transform(lambda m:
                    self.mark_jump_to_string(m, view, n if n != 0 else 1,
                        chr(ev1.get_keyval()[1]) +
                        chr(ev2.get_keyval()[1]), backward = True),
                    True))
        self.emit('bind-command-key', 'g g', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_to_line_n(
                    m, view, n if n != 0 else 1),
                True))
        self.emit('bind-command-key', 'G', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_to_line_n(
                    m, view, view.get_buffer().get_line_count()),
                True))
        self.emit('bind-command-key', 'R', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_to_line_start(
                    m, view, n if n != 0 else 1),
                True))
        self.emit('bind-command-key', 'r', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_to_line_end(
                    m, view, 0),
                True))
        self.emit('bind-command-key', '[', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_to_empty_line(
                    m, view, n if n != 0 else 1, backward = True),
                True))
        self.emit('bind-command-key', ']', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_to_empty_line(
                    m, view, n if n != 0 else 1),
                True))
        self.emit('bind-command-key', '%', lambda view, n:
            self.view_get_cursor(view).transform(lambda m:
                self.mark_jump_to_matching_bracket(
                    m, view, 0),
                True))

    def view_get_cursor(self, view):
        return view.get_buffer().attr['cursor']
