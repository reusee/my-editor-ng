class CoreSelectionCommands:
    def __init__(self):

        # move
        self.emit('bind-command-key', 'j', lambda view, n:
            self.sel_trans_jump_line_with_preferred_offset(view,
                n if n != 0 else 1,
                [view.get_buffer().attr['cursor']], backward = False))
        self.emit('bind-command-key', 'k', lambda view, n:
            self.sel_trans_jump_line_with_preferred_offset(view,
                n if n != 0 else 1,
                [view.get_buffer().attr['cursor']], backward = True))
        self.emit('bind-command-key', 'h', lambda view, n:
            self.sel_trans_jump_char(view,
                n if n != 0 else 1,
                [view.get_buffer().attr['cursor']], backward = True))
        self.emit('bind-command-key', 'l', lambda view, n:
            self.sel_trans_jump_char(view,
                n if n != 0 else 1,
                [view.get_buffer().attr['cursor']], backward = False))
        self.emit('bind-command-key', 'f', lambda view, n:
            lambda ev:
                self.sel_trans_jump_search(view,
                    n if n != 0 else 1,
                    [view.get_buffer().attr['cursor']],
                    chr(ev.get_keyval()[1]),
                    backward = False))
        self.emit('bind-command-key', 'F', lambda view, n:
            lambda ev:
                self.sel_trans_jump_search(view,
                    n if n != 0 else 1,
                    [view.get_buffer().attr['cursor']],
                    chr(ev.get_keyval()[1]),
                    backward = True))
        self.emit('bind-command-key', 's', lambda view, n:
            lambda ev1: lambda ev2:
                self.sel_trans_jump_search(view,
                    n if n != 0 else 1,
                    [view.get_buffer().attr['cursor']],
                    chr(ev1.get_keyval()[1]) + chr(ev2.get_keyval()[1]),
                    backward = False))
        self.emit('bind-command-key', 'S', lambda view, n:
            lambda ev1: lambda ev2:
                self.sel_trans_jump_search(view,
                    n if n != 0 else 1,
                    [view.get_buffer().attr['cursor']],
                    chr(ev1.get_keyval()[1]) + chr(ev2.get_keyval()[1]),
                    backward = True))
        self.emit('bind-command-key', 'g g', lambda view, n:
            self.sel_trans_jump_to_line_n(view,
                n if n != 0 else 1,
                [view.get_buffer().attr['cursor']]))
        self.emit('bind-command-key', 'G', lambda view, n:
            self.sel_trans_jump_to_buffer_end(view,
                n if n != 0 else 1,
                [view.get_buffer().attr['cursor']]))
