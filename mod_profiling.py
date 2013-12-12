import cProfile, pstats, io

class ModProfiling:
    def __init__(self, editor):
        self.editor = editor
        self.profiler = None
        self.enabled = False
        editor.bind_command_key('..p', self.toggle, 'toggle profiler')

    def toggle(self):
        if not self.enabled:
            self.profiler = cProfile.Profile()
            self.profiler.enable()
            self.enabled = True
            self.editor.show_message('start profiling')
        else:
            self.profiler.disable()
            s = io.StringIO()
            sort_by = 'cumulative'
            ps = pstats.Stats(self.profiler, stream = s).sort_stats(sort_by)
            ps.print_stats()
            print(s.getvalue())
            self.enabled = False
            self.editor.show_message('stop profiling')
