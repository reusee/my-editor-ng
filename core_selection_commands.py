class CoreSelectionCommands:
    def __init__(self):
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
