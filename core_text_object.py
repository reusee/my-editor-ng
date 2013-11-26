class TextObject:
  def __init__(self):
    pass

  def make_text_object_handler(self, func):
    handler = {
        'd': lambda view, n: self.text_object_current_line_func(view, n, func),
        't': lambda view: self.text_object_to_char(view, func),
        'f': lambda view: self.text_object_to_char(view, func, to_end = True),
        }
    return handler

  def text_object_current_line_func(self, view, n, func):
    buf = view.get_buffer()
    if n == 0: n = 1
    buf.begin_user_action()
    for _ in range(n):
      start = buf.get_iter_at_mark(buf.get_insert())
      end = start.copy()
      start.set_line_offset(0)
      end.forward_line()
      buf.move_mark(buf.get_selection_bound(), start)
      buf.move_mark(buf.get_insert(), end)
      func(view)
    buf.end_user_action()

  def text_object_to_char(self, view, func, to_end = False):
    def wait_key(ev):
      c = chr(ev.get_keyval()[1])
      buf = view.get_buffer()
      buf.begin_user_action()
      it = buf.get_iter_at_mark(buf.get_insert())
      line_end_iter = it.copy()
      line_end_iter.forward_to_line_end()
      it = it.forward_search(c, 0, line_end_iter)
      if it:
        if to_end: it = it[1]
        else: it = it[0]
        buf.move_mark(buf.get_selection_bound(), it)
        func(view)
      buf.end_user_action()
    return wait_key
