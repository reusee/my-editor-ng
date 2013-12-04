class CoreSelectionTransformRange:
    def __init__(self):
        pass

    def sel_trans_extend_line(self, view, n, selections, backward = False):
        buf = view.get_buffer()
        for sel in selections:
            start = buf.get_iter_at_mark(sel.start)
            end = buf.get_iter_at_mark(sel.end)
            if start.compare(end) == 0:
                start.set_line_offset(0)
                end.forward_line()
            else:
                if backward: start.backward_line()
                else: end.forward_line()
            for _ in range(n):
                if backward: start.backward_line()
                else: end.forward_line()
            buf.move_mark(sel.start, start)
            buf.move_mark(sel.end, end)
