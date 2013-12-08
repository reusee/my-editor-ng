class CoreFolding:
    def __init__(self):
        self.connect('buffer-created', self.setup_folding)
        self.bind_command_key('z', self.cmd_fold_selection)
        self.bind_command_key('mz', self.unfold_all)

    def setup_folding(self, _, buf):
        tag = buf.create_tag('folded',
            font = 'Terminus 2',
            )
        buf.attr['folded-tag'] = tag
        buf.connect('notify::cursor-position', self.forbid_folded_area)
        buf.attr['folded-ranges'] = []

    def fold_selection(self, buf):
        hidden = False
        for sel in buf.attr['selections']:
            start_iter = buf.get_iter_at_mark(sel.start)
            end_iter = buf.get_iter_at_mark(sel.end)
            if start_iter.compare(end_iter) != 0:
                hidden = True
                buf.apply_tag_by_name('folded', start_iter, end_iter)
        start_iter = buf.get_iter_at_mark(buf.get_selection_bound())
        end_iter = buf.get_iter_at_mark(buf.get_insert())
        if start_iter.compare(end_iter) != 0:
            hidden = True
            buf.apply_tag_by_name('folded', start_iter, end_iter)
            buf.attr['folded-ranges'].append((
                buf.create_mark(None, start_iter, True),
                buf.create_mark(None, end_iter, True)))
        return hidden

    def cmd_fold_selection(self, buf):
        def func():
            if not self.fold_selection(buf):
                return False
            self.clear_selections(buf)
            return True
        if not func():
            buf.attr['delayed-selection-operation'] = func
            return self.selection_extend_handler

    def forbid_folded_area(self, buf, _):
        for start, end in buf.attr['folded-ranges']:
            it = buf.get_iter_at_mark(buf.get_insert())
            start_iter = buf.get_iter_at_mark(start)
            end_iter = buf.get_iter_at_mark(end)
            if it.in_range(start_iter, end_iter):
                distance1 = it.get_offset() - start_iter.get_offset()
                distance2 = end_iter.get_offset() - it.get_offset()
                if distance1 < distance2:
                    buf.place_cursor(end_iter)
                else:
                    if start_iter.backward_char():
                        buf.place_cursor(start_iter)
                    else:
                        buf.place_cursor(end_iter)

    def unfold_all(self, buf):
        buf.remove_tag_by_name('folded',
            buf.get_start_iter(), buf.get_end_iter())
        for start, end in buf.attr['folded-ranges']:
            buf.delete_mark(start)
            buf.delete_mark(end)
        buf.attr['folded-ranges'].clear()
