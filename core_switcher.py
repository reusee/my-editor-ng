class Switcher:
    def __init__(self):
        self.emit('bind-command-key', '>', self.switch_next_buffer)
        self.emit('bind-command-key', '<', self.switch_prev_buffer)
        self.connect('view-created', self.setup_switcher)

    def setup_switcher(self, _, view):
      view.attr['buffer-position'] = {}
      view.connect('focus-in-event', self.restore_buffer_position)

    def save_buffer_position(self, view):
      buf = view.get_buffer()
      mark = buf.create_mark(None, buf.get_iter_at_mark(buf.get_insert()))
      view.attr['buffer-position'][buf] = mark

    def restore_buffer_position(self, view, ev):
      buf = view.get_buffer()
      if buf in view.attr['buffer-position']:
        mark = view.attr['buffer-position'][buf]
        buf.place_cursor(buf.get_iter_at_mark(mark))
        buf.delete_mark(mark)
        del view.attr['buffer-position'][buf]

    def switch_next_buffer(self, view):
        index = self.buffers.index(view.get_buffer())
        index += 1
        if index == len(self.buffers):
            index = 0
        view.set_buffer(self.buffers[index])

    def switch_prev_buffer(self, view):
        index = self.buffers.index(view.get_buffer())
        index -= 1
        if index < 0:
            index = len(self.buffers) - 1
        view.set_buffer(self.buffers[index])
