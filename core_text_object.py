def with_multiple_cursor(func):
    def f(self, view, *args, **kwargs):
        buf = view.get_buffer()
        for selection in buf.attr['selections']:
            func(self, view, *args,
                start_mark = selection.start,
                end_mark = selection.end,
                **kwargs)
        func(self, view, *args,
            start_mark = buf.get_selection_bound(),
            end_mark = buf.get_insert(),
            **kwargs)
    return f

class TextObject:
    def __init__(self):
        pass

    def make_text_object_handler(self, func):
        handler = {
            'w': lambda view, n: self.text_object_to_word_edge(view, n, func),
            'W': lambda view, n: self.text_object_to_word_edge(view, n, func, backward = True),
            'r': lambda view, n: self.text_object_to_line_edge(view, n, func),
            'R': lambda view, n: self.text_object_to_line_edge(view, n, func, backward = True),
            'i': {
              'w': lambda view, n: self.text_object_inside_word(view, n, func),
              },
            't': lambda view, n: self.text_object_to_char(view, n, func),
            'T': lambda view, n: self.text_object_to_two_chars(view, n, func),
            'a': {
              },
            'd': lambda view, n: self.text_object_current_line(view, n, func),
            'f': lambda view, n: self.text_object_to_char(view, n, func, to_end = True),
            'F': lambda view, n: self.text_object_to_two_chars(view, n, func, to_end = True),
            'j': lambda view, n: self.text_object_sibling_line(view, n, func),
            'k': lambda view, n: self.text_object_sibling_line(view, n, func, prev = True),
            'h': lambda view, n: self.text_object_sibling_char(view, n, func, prev = True),
            'l': lambda view, n: self.text_object_sibling_char(view, n, func),
            }

        def define(left, right):
            handler['i'][left] = lambda view, n: self.text_object_brackets(view, n, func, left, right)
            handler['i'][right] = lambda view, n: self.text_object_brackets(view, n, func, left, right)
            handler['a'][left] = lambda view, n: self.text_object_brackets(view, n, func, left, right, around = True)
            handler['a'][right] = lambda view, n: self.text_object_brackets(view, n, func, left, right, around = True)
        for left, right in self.BRACKETS.items():
            define(left, right)

        return handler

    @with_multiple_cursor
    def text_object_to_line_edge(self, view, n, func, backward = False, start_mark = None, end_mark = None):
        buf = view.get_buffer()
        if n == 0: n = 1
        buf.begin_user_action()
        for _ in range(n):
            it = buf.get_iter_at_mark(end_mark)
            if backward: it.set_line_offset(0)
            else: it.forward_to_line_end()
            buf.move_mark(start_mark, it)
            func(view, start_mark, end_mark)
        buf.end_user_action()

    @with_multiple_cursor
    def text_object_inside_word(self, view, n, func, start_mark = None, end_mark = None):
        buf = view.get_buffer()
        if n == 0: n = 1
        buf.begin_user_action()
        for _ in range(n):
            start = buf.get_iter_at_mark(end_mark)
            end = start.copy()
            self.iter_to_word_edge(start, backward = True)
            self.iter_to_word_edge(end)
            buf.move_mark(start_mark, start)
            buf.move_mark(end_mark, end)
            func(view, start_mark, end_mark)
        buf.end_user_action()

    @with_multiple_cursor
    def text_object_brackets(self, view, n ,func, left, right, around = False, start_mark = None, end_mark = None):
        buf = view.get_buffer()
        if n == 0: n = 1
        buf.begin_user_action()
        for _ in range(n):
            start = buf.get_iter_at_mark(end_mark)
            end = start.copy()

            balance = 0
            start.backward_char()
            found = False
            while True:
                c = start.get_char()
                if c == left and balance == 0: # found
                    found = True
                    break
                elif c == left:
                    balance -= 1
                elif c == right:
                    balance += 1
                if not start.backward_char(): # edge
                    break
            if not found: continue
            if not around: start.forward_char()

            balance = 0
            found = False
            while True:
                c = end.get_char()
                if c == right and balance == 0: # found
                    found = True
                    break
                elif c == right:
                    balance -= 1
                elif c == left:
                    balance += 1
                if not end.forward_char():
                    break
            if not found: continue
            if around: end.forward_char()

            buf.move_mark(start_mark, start)
            buf.move_mark(end_mark, end)
            func(view, start_mark, end_mark)
        buf.end_user_action()
