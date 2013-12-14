import subprocess
import os
import json

class ModGolang:
    def __init__(self, editor):
        self.editor = editor
        editor.connect('language-detected', lambda _, buf, lang:
            self.setup(buf) if lang == 'Go' else None)

        self.gocode_path = os.path.expanduser('~/gopath/bin/gocode')

    def setup(self, buf):
        self.editor.show_message('golang loaded')
        buf.attr.setdefault('completion-providers', [])
        buf.attr['completion-providers'].append(self.provide)
        buf.attr['gocode-provided'] = set()

    def provide(self, buf, word, candidates):
        offset = len(buf.get_text(buf.get_start_iter(),
            buf.get_iter_at_mark(buf.get_insert()), False).encode('utf8'))
        p = subprocess.Popen([self.gocode_path, '-f=json', 'autocomplete',
            buf.attr['filename'], str(offset)],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE)
        data, err = p.communicate(buf.get_text(buf.get_start_iter(),
            buf.get_end_iter(), False).encode('utf8'))
        if len(err) > 0: # error
            self.editor.show_message('gocode error')
        data = json.loads(data.decode('utf8'))
        if len(data) == 0: # no candidates, use last provided
            candidates.update(w
                for w in buf.attr['gocode-provided']
                if self.editor.completion_fuzzy_match(w, word))
            return
        buf.attr['gocode-provided'].clear()
        for entry in data[1]:
            candidates.add(entry['name'])
            buf.attr['gocode-provided'].add(entry['name'])
