class CoreSelectionOperation:
    def __init__(self):
        self.emit('bind-command-key', 'd', self.delete_selection)
        self.emit('bind-command-key', 'c', self.change_selection)

    def delete_selection(self, view):
        buf = view.get_buffer()
        if self._delete_selection(buf):
            self.enter_none_selection_mode(view)
            self.clear_selections(buf)
        else:
            buf.attr['queue-operation'] = lambda: self._delete_selection(buf)
            return self.command_key_handler['.']

    def _delete_selection(self, buf):
        #TODO copy
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
            buf.attr['queue-operation'] = lambda: self._change_selection(buf, view)
            return self.command_key_handler['.']
            
    def _change_selection(self, buf, view):
        self._delete_selection(buf)
        self.enter_none_selection_mode(view)
        self.enter_edit_mode()

