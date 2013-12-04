class CoreSelectionCommands:
    def __init__(self):
        self.emit('bind-command-key', 'g g', lambda view, n:
            self.sel_trans_jump_to_line_n(view,
                n if n != 0 else 1,
                [view.get_buffer().attr['cursor']]))
        self.emit('bind-command-key', 'G', lambda view, n:
            self.sel_trans_jump_to_buffer_end(view,
                n if n != 0 else 1,
                [view.get_buffer().attr['cursor']]))
        self.emit('bind-command-key', 'R', lambda view, n:
            self.sel_trans_jump_to_line_start(view,
                n if n != 0 else 1,
                [view.get_buffer().attr['cursor']]))
        self.emit('bind-command-key', 'r', lambda view, n:
            self.sel_trans_jump_to_line_end(view,
                n if n != 0 else 1,
                [view.get_buffer().attr['cursor']]))
        self.emit('bind-command-key', '[', lambda view, n:
            self.sel_trans_jump_to_empty_line(view,
                n if n != 0 else 1,
                [view.get_buffer().attr['cursor']],
                backward = True))
        self.emit('bind-command-key', ']', lambda view, n:
            self.sel_trans_jump_to_empty_line(view,
                n if n != 0 else 1,
                [view.get_buffer().attr['cursor']],
                backward = False))
        self.emit('bind-command-key', '%', lambda view, n:
            self.sel_trans_jump_matching_bracket(view,
                n if n != 0 else 1,
                [view.get_buffer().attr['cursor']]))

        # selection
        self.emit('bind-command-key', '. j', lambda view, n:
            self.sel_trans_extend_line(view, n,
                self.view_get_all_selections(view),
                backward = False))
        self.emit('bind-command-key', '. k', lambda view, n:
            self.sel_trans_extend_line(view, n,
                self.view_get_all_selections(view),
                backward = True))

    def view_get_all_selections(self, view):
        buf = view.get_buffer()
        return buf.attr['selections'] + [buf.attr['cursor']]
