import regex
from collections import OrderedDict
from gi.repository import Gdk
import time

class CoreSnippet:
    def __init__(self):
        self.connect('buffer-created', self.setup_snippet)

        self.bind_command_key('..t', lambda buf:
            #self.insert_snippet(buf, ['foo $1 bar $1 baz $2 $3 qux $2 quux$4']),
            self.insert_snippet(buf, [
                'foo$1$>',
                '$1bar$<',
                'baz$1',
            ]),
            'test snippet')

    def setup_snippet(self, _, buf):
        buf.attr['snippet-insert-points'] = OrderedDict()
        self.add_pattern(buf, [Gdk.KEY_Shift_L, Gdk.KEY_Shift_L],
            self.snippet_next_insert_points,
            drop_key_event = True, clear_matched_text = False)

    def insert_snippet(self, buf, lines):
        control_pattern = regex.compile('(\$[0-9><]+)')
        orig_mark = buf.create_mark(None, buf.get_iter_at_mark(buf.get_insert()), True)

        it = buf.get_iter_at_mark(buf.get_insert())
        it.set_line_offset(0)
        while not it.ends_line() and it.get_char().isspace():
            it.forward_char()
        indent_str = ' ' * it.get_line_offset()

        insert_points = buf.attr['snippet-insert-points']
        insert_points.clear()
        for i, line in enumerate(lines):
            if i > 0:
                self.insert_at_selections(buf, '\n')
                self.insert_at_selections(buf, indent_str)
            sections = control_pattern.split(line)
            for section in sections:
                if control_pattern.match(section):
                    control = section[1:]
                    if all(c.isdigit() for c in control): # insert point
                        mark = buf.create_mark(None, buf.get_iter_at_mark(buf.get_insert()), True)
                        insert_points.setdefault(section, [])
                        insert_points[section].append(mark)
                    elif control == '>': # indent
                        width = self.default_indent_width
                        if 'indent-width' in buf.attr:
                            width = buf.attr['indent-width']
                        indent_str += ' ' * width
                    elif control == '<': # dedent
                        width = self.default_indent_width
                        if 'indent-width' in buf.attr:
                            width = buf.attr['indent-width']
                        indent_str = indent_str[:-width]
                else:
                    self.insert_at_selections(buf, section)

        buf.place_cursor(buf.get_iter_at_mark(orig_mark))
        buf.delete_mark(orig_mark)
        if len(insert_points) > 0:
            self.snippet_next_insert_points(buf)

    def snippet_next_insert_points(self, buf):
        insert_points_set = buf.attr['snippet-insert-points']
        if len(insert_points_set) == 0:
            self.show_message('no snippet insert point')
            return
        key = list(insert_points_set.keys())[0]
        self.clear_selections(buf)
        points = insert_points_set[key]
        buf.place_cursor(buf.get_iter_at_mark(points[0]))
        for mark in points[1:]:
            self.toggle_selection_mark(buf,
                buf.get_iter_at_mark(mark))
            buf.delete_mark(mark)
        del insert_points_set[key]
        self.enter_edit_mode(buf)
