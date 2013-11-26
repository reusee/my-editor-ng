class TextObject:
  def __init__(self):
    pass

  def make_text_object_handler(self, func):
    handler = {
        'd': lambda view, n: self.text_object_current_line_func(view, n, func),
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
