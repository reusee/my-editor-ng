class CoreSelectionTransform:
    def __init__(self):
        self.emit('bind-command-key', 'j', lambda view, n:
            view.get_buffer().attr['cursor'].transform(
                lambda m: self.mark_jump_relative_line_with_preferred_offset(
                    m, view, n if n != 0 else 1),
                True))
        self.emit('bind-command-key', 'k', lambda view, n:
            view.get_buffer().attr['cursor'].transform(
                lambda m: self.mark_jump_relative_line_with_preferred_offset(
                    m, view, n if n != 0 else 1, backward = True),
                True))
