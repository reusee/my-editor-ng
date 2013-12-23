from gi.repository import Gtk, Gdk, GObject, GtkSource
import os
import time

class CoreFile:
    def __init__(self):

        self.file_chooser = FileChooser(self)
        self.bind_command_key(',b', self.open_file_chooser, 'open file')
        self.connect('realize', lambda _: self.north_area.add(self.file_chooser))
        self.file_chooser.connect('done', self.open_file)

        self.bind_command_key(',w', self.save_to_file, 'save file')
        self.file_backup_dir = os.path.join(os.path.expanduser('~'), '.my-editor-file-backup')
        if not os.path.exists(self.file_backup_dir):
            os.mkdir(self.file_backup_dir)

        self.new_signal('before-saving', (GtkSource.Buffer,))

    def open_file_chooser(self, view):
        self.file_chooser.last_view = view
        current_filename = view.get_buffer().attr['filename']
        if current_filename:
            os.chdir(os.path.dirname(current_filename))
        self.file_chooser.update_list(self.file_chooser.entry, None)
        self.file_chooser.show_all()
        self.file_chooser.entry.set_text('')
        self.file_chooser.entry.grab_focus()

    def open_file(self, file_chooser):
        filename = file_chooser.filename
        view = file_chooser.last_view
        if not filename: return
        filename = os.path.abspath(filename)
        # create or select buffer
        buf = None
        for b in self.buffers:
            if b.attr['filename'] == filename:
                buf = b
        if buf is None:
            buf = self.create_buffer(filename)
            self.load_file(buf, filename)
        # switch to buffer
        if view.get_buffer() != buf:
            self.switch_to_buffer(view, buf)

    def save_to_file(self, view):
        buf = view.get_buffer()
        if not buf.get_modified(): return
        filename = buf.attr['filename']
        if not filename: return
        self.show_message('saving ' + buf.attr['filename'])
        tmp_filename = filename + '.' + str(time.time())
        backup_filename = self.quote_filename(filename) + '.' + str(time.time())
        backup_filename = os.path.join(self.file_backup_dir, backup_filename)
        self.emit('before-saving', buf)
        mode = os.stat(filename).st_mode
        with os.fdopen(os.open(tmp_filename, os.O_WRONLY | os.O_CREAT, mode), 'w+') as f:
            f.write(buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False))
        try: os.rename(filename, backup_filename)
        except FileNotFoundError: pass
        os.rename(tmp_filename, filename)
        buf.set_modified(False)

    def quote_filename(self, s):
        s = s.replace(r'%', r'%%')
        s = s.replace('/', r'%s')
        return s

class FileChooser(Gtk.Grid):

    __gsignals__ = {
      'done': (GObject.SIGNAL_RUN_FIRST, None, ()),
      }

    def __init__(self, editor):
        Gtk.Grid.__init__(self, orientation = Gtk.Orientation.VERTICAL)
        self.editor = editor
        self.set_vexpand(True)
        self.set_hexpand(True)
        self.connect('key-press-event', self.handle_key_press)

        self.entry = Gtk.Entry()
        self.entry.set_alignment(0)
        self.entry.set_hexpand(True)
        self.add(self.entry)
        self.entry.connect('notify::text', self.update_list)
        self.entry.connect('key-press-event', self.handle_key_press)

        store = Gtk.ListStore(str)
        self.store = store

        view = Gtk.TreeView(model = store)
        view.set_headers_visible(False)
        self.view = view
        self.add(view)
        self.view.connect('row-activated', self.handle_row_activated)

        renderer = Gtk.CellRendererText()
        renderer.set_alignment(0, 0.5)
        column = Gtk.TreeViewColumn('path', renderer, text = 0)
        view.append_column(column)

        self.filename = None
        self.last_view = None

        select = view.get_selection()
        select.set_mode(Gtk.SelectionMode.BROWSE)
        select.connect('changed', self.on_selection_changed)
        self.select = select

    def on_selection_changed(self, selection):
        store, it = selection.get_selected()
        if it != None:
            self.filename = store[it][0]

    def handle_key_press(self, _, event):
        _, val = event.get_keyval()
        if val == Gdk.KEY_Escape:
            self.filename = None
            self.done()
        elif val == Gdk.KEY_Return:
            if os.path.isdir(self.filename): # enter subdirectory
                path = self.filename + os.path.sep
                self.entry.set_text(path)
                self.entry.set_position(-1)
            else:
                self.done()

    def handle_row_activated(self, _, path, column):
        if os.path.isdir(self.filename): # enter subdirectory
            path = self.filename + os.path.sep
            self.entry.set_text(path)
            self.entry.grab_focus()
            self.entry.set_position(-1)
        else:
            self.done()

    def done(self):
        self.hide()
        self.editor.switch_to_view(self.last_view)
        self.emit('done')

    def update_list(self, entry, _):
        head, tail = os.path.split(os.path.expanduser(entry.get_text()))
        if head == '':
            head = os.path.abspath('.')
        self.store.clear()
        candidates = []
        try:
            n = 0
            for f in os.listdir(head):
                if self.fuzzy_match(tail, f):
                    candidates.append(os.path.join(head, f))
                    n += 1
                    if n > 30: break
        except FileNotFoundError:
            return
        candidates = sorted(candidates, key = lambda e: len(e))
        for c in candidates:
            self.store.append([c])
        self.select.select_path((0))

    def fuzzy_match(self, key, s):
        keyI = 0
        sI = 0
        while keyI < len(key) and sI < len(s):
            if s[sI].lower() == key[keyI].lower():
                sI += 1
                keyI += 1
            else:
                sI += 1
        return keyI == len(key)
