class TextObject:
  def __init__(self):
    pass

  def make_text_object_handler(self, func):
    handler = {
        'd': lambda view, n: self.text_object_current_line(view, n, func),
        't': lambda view, n: self.text_object_to_char(view, n, func),
        'T': lambda view, n: self.text_object_to_two_chars(view, n, func),
        'f': lambda view, n: self.text_object_to_char(view, n, func, to_end = True),
        'F': lambda view, n: self.text_object_to_two_chars(view, n, func, to_end = True),
        'j': lambda view, n: self.text_object_sibling_line(view, n, func),
        'k': lambda view, n: self.text_object_sibling_line(view, n, func, prev = True),
        'h': lambda view, n: self.text_object_prev_char(view, n, func),
        'l': lambda view, n: self.text_object_prev_char(view, n, func),
        }
    return handler

  def text_object_current_line(self, view, n, func):
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

  def text_object_to_char(self, view, n, func, to_end = False):
    def wait_key(ev):
      c = chr(ev.get_keyval()[1])
      buf = view.get_buffer()
      count = n
      if count == 0: count = 1
      buf.begin_user_action()
      for _ in range(count):
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

  def text_object_to_two_chars(self, view, n, func, to_end = False):
    def wait_first(ev):
      c = chr(ev.get_keyval()[1])
      def wait_second(ev):
        s = c + chr(ev.get_keyval()[1])
        buf = view.get_buffer()
        count = n
        if count == 0: count = 1
        buf.begin_user_action()
        for _ in range(count):
          it = buf.get_iter_at_mark(buf.get_insert())
          line_end_iter = it.copy()
          line_end_iter.forward_to_line_end()
          it = it.forward_search(s, 0, line_end_iter)
          if it:
            if to_end: it = it[1]
            else: it = it[0]
            buf.move_mark(buf.get_selection_bound(), it)
            func(view)
        buf.end_user_action()
      return wait_second
    return wait_first

  def text_object_sibling_line(self, view, n, func, prev = False):
    buf = view.get_buffer()
    if n == 0: n = 1
    buf.begin_user_action()
    for _ in range(n):
      start = buf.get_iter_at_mark(buf.get_insert())
      cur = buf.create_mark(None, start)
      if prev:
        start.set_line_offset(0)
        end = start.copy()
        end.backward_line()
      else:
        start.forward_line()
        end = start.copy()
        end.forward_line()
      buf.move_mark(buf.get_selection_bound(), start)
      buf.move_mark(buf.get_insert(), end)
      func(view)
      buf.place_cursor(buf.get_iter_at_mark(cur)) # restore position
    buf.end_user_action()
