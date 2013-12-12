import regex
from collections import OrderedDict
from gi.repository import Gdk
import time

class CoreSnippet:
    def __init__(self):
        self.connect('buffer-created', self.setup_snippet)

        self.bind_command_key('..t', lambda buf:
            self.insert_snippet(buf, 'foo $1 bar $1 baz $2 $3 qux $2 quux$4'),
            'test snippet')

    def setup_snippet(self, _, buf):
        buf.attr['snippet-insert-points'] = OrderedDict()
        self.add_pattern(buf, [Gdk.KEY_Shift_L, Gdk.KEY_Shift_L],
            lambda buf: self.snippet_next_insert_points(buf)
                if len(buf.attr['snippet-insert-points']) > 0
                else None
            )

    def insert_snippet(self, buf, s):
        var_pattern = regex.compile('(\$[0-9]+)')
        sections = var_pattern.split(s)
        orig_mark = buf.create_mark(None, buf.get_iter_at_mark(buf.get_insert()), True)
        insert_points = buf.attr['snippet-insert-points']
        insert_points.clear()
        for section in sections:
            if var_pattern.match(section):
                mark = buf.create_mark(None, buf.get_iter_at_mark(buf.get_insert()), True)
                insert_points.setdefault(section, [])
                insert_points[section].append(mark)
            else:
                self.insert_at_selections(buf, section)
        buf.place_cursor(buf.get_iter_at_mark(orig_mark))
        buf.delete_mark(orig_mark)
        self.snippet_next_insert_points(buf)

    def snippet_next_insert_points(self, buf):
        insert_points_set = buf.attr['snippet-insert-points']
        if len(insert_points_set) == 0:
            self.enter_command_mode(buf)
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
