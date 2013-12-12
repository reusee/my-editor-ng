from gi.repository import Gtk, GObject, cairo, Gdk

class CoreLayout:
    def __init__(self):
        self.bind_command_key(',v', lambda view: self.split_view(view, Gtk.Orientation.VERTICAL),
            'vertical split current view')
        self.bind_command_key(',f', lambda view: self.split_view(view, Gtk.Orientation.HORIZONTAL),
            'horizontal split current view')
        self.bind_command_key(',s', self.sibling_view, 'sibling split current view')

        self.bind_command_key('J', self.south_view, 'switch to view on the south')
        self.bind_command_key('K', self.north_view, 'switch to view on the north')
        self.bind_command_key('H', self.west_view, 'switch to view on the west')
        self.bind_command_key('L', self.east_view, 'switch to view on the east')

    def split_view(self, view, orientation):
        wrapper = view.attr['wrapper']
        grid = wrapper.get_parent()
        new_view = self.create_view()
        self.switch_to_buffer(new_view, view.get_buffer())

        left = GObject.Value()
        left.init(GObject.TYPE_INT)
        grid.child_get_property(wrapper, 'left-attach', left)
        left = left.get_int()
        top = GObject.Value()
        top.init(GObject.TYPE_INT)
        grid.child_get_property(wrapper, 'top-attach', top)
        top = top.get_int()

        grid.remove(wrapper)
        new_grid = Gtk.Grid()
        new_grid.set_property('orientation', orientation)
        new_grid.add(wrapper)
        new_grid.add(new_view.attr['wrapper'])
        new_grid.show_all()
        grid.attach(new_grid, left, top, 1, 1)
        view.grab_focus() # restore focus

        self.switch_to_view(new_view)

    def sibling_view(self, view):
        grid = view.attr['wrapper'].get_parent()
        new_view = self.create_view()
        self.switch_to_buffer(new_view, view.get_buffer())
        wrapper = new_view.attr['wrapper']
        wrapper.show_all()
        grid.add(wrapper)
        self.switch_to_view(new_view)

    def switch_to_view_at_pos(self, x, y):
        for view in self.views:
            alloc = view.get_allocation()
            win = view.get_window(Gtk.TextWindowType.WIDGET)
            _, left, top = win.get_origin()
            right = left + alloc.width
            bottom = top + alloc.height
            if x >= left and x <= right and y >= top and y <= bottom: # found
                self.switch_to_view(view)
                break

    def north_view(self, view):
        alloc = view.get_allocation()
        win = view.get_window(Gtk.TextWindowType.WIDGET)
        _, x, y = win.get_origin()
        self.switch_to_view_at_pos(x + alloc.width / 3, y - 30)

    def south_view(self, view):
        alloc = view.get_allocation()
        win = view.get_window(Gtk.TextWindowType.WIDGET)
        _, x, y = win.get_origin()
        self.switch_to_view_at_pos(x + alloc.width / 3, y + 30 + alloc.height)

    def west_view(self, view):
        alloc = view.get_allocation()
        win = view.get_window(Gtk.TextWindowType.WIDGET)
        _, x, y = win.get_origin()
        self.switch_to_view_at_pos(x - 30, y + alloc.height / 3)

    def east_view(self, view):
        alloc = view.get_allocation()
        win = view.get_window(Gtk.TextWindowType.WIDGET)
        _, x, y = win.get_origin()
        self.switch_to_view_at_pos(x + 20 + alloc.width, y + alloc.height / 3)
