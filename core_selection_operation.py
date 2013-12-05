class CoreSelectionOperation:
    def __init__(self):
        pass

    def delete_selection(self, buf):
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

    def copy_selection(self, buf):
        #TODO multiple clipboard
        if buf.get_has_selection():
            buf.copy_clipboard(self.clipboard)
            return True
        return False

    #TODO selection indent / dedent
