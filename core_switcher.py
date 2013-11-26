class Switcher:
    def __init__(self):
        self.emit('bind-command-key', '>', self.switch_next_buffer)
        self.emit('bind-command-key', '<', self.switch_next_buffer)

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
