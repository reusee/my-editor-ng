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
