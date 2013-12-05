class CoreSelectionOperation:
    def __init__(self):
        self.emit('bind-command-key', 'd', self.delete_selection)
        self.emit('bind-command-key', 'c', self.change_selection)
        self.emit('bind-command-key', 'y', self.copy_selection)

    def delete_selection(self, view):
        buf = view.get_buffer()
        if self._delete_selection(buf):
            self.enter_none_selection_mode(view)
            self.clear_selections(buf)
        else:
            buf.attr['delayed-selection-operation'], = (lambda:
                self._delete_selection(buf),)
            return self.selection_extend_handler

    def _delete_selection(self, buf):
        self._copy_selection(buf)
        deleted = False
        buf.begin_user_action()
        for sel in buf.attr['selections']:
            start_iter = buf.get_iter_at_mark(sel.start)
            end_iter = buf.get_iter_at_mark(sel.end)
            if start_iter.compare(end_iter) != 0: deleted = True
            buf.delete(start_iter, end_iter)
        deleted = buf.delete_selection(True, True)
        buf.end_user_action()
        return deleted

    def change_selection(self, view):
        buf = view.get_buffer()
        if self._delete_selection(buf):
            self.enter_none_selection_mode(view)
            self.enter_edit_mode()
        else:
            buf.attr['delayed-selection-operation'], = (lambda:
                self._change_selection(buf, view),)
            return self.selection_extend_handler

    def _change_selection(self, buf, view):
        self._delete_selection(buf)
        self.enter_none_selection_mode(view)
        self.enter_edit_mode()

    def copy_selection(self, view):
        buf = view.get_buffer()
        if self._copy_selection(buf):
            self.enter_none_selection_mode(view)
            self.clear_selections(buf)
        else:
            def f():
                self._copy_selection(buf)
                self.enter_none_selection_mode(view)
                self.clear_selections(buf)
            buf.attr['delayed-selection-operation'] = f
            return self.selection_extend_handler

    def _copy_selection(self, buf):
        #TODO multiple clipboard
        if buf.get_has_selection():
            buf.copy_clipboard(self.clipboard)
            return True
