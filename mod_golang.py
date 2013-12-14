import subprocess
import os
import json
from core_selection_transform import Transform

class ModGolang:
    def __init__(self, editor):
        self.editor = editor
        editor.connect('language-detected', lambda _, buf, lang:
            self.setup(buf) if lang == 'Go' else None)

        self.gocode_path = os.path.expanduser('~/gopath/bin/gocode')
        editor.connect('before-saving', lambda _, buf:
            self.gofmt(buf)
            if buf.attr['lang'] and buf.attr['lang'].get_name() == 'Go'
            else None)

    def setup(self, buf):
        self.editor.show_message('golang loaded')
        buf.attr.setdefault('completion-providers', [])
        buf.attr['completion-providers'].append(self.provide)
        buf.attr['gocode-provided'] = set()

        # oracle
        self.editor.bind_key_handler(buf.command_key_handler, '.od',
            lambda buf: self.oracle(buf, 'describe'),
            'golang oracle: describe')
        self.editor.bind_key_handler(buf.command_key_handler, '.oe',
            lambda buf: self.oracle(buf, 'callees'),
            'golang oracle: callees')
        self.editor.bind_key_handler(buf.command_key_handler, '.or',
            lambda buf: self.oracle(buf, 'callers'),
            'golang oracle: callers')
        self.editor.bind_key_handler(buf.command_key_handler, '.og',
            lambda buf: self.oracle(buf, 'callgraph'),
            'golang oracle: callgraph')
        self.editor.bind_key_handler(buf.command_key_handler, '.os',
            lambda buf: self.oracle(buf, 'callstack'),
            'golang oracle: callstack')
        self.editor.bind_key_handler(buf.command_key_handler, '.of',
            lambda buf: self.oracle(buf, 'freevars'),
            'golang oracle: freevars')
        self.editor.bind_key_handler(buf.command_key_handler, '.oi',
            lambda buf: self.oracle(buf, 'implements'),
            'golang oracle: implements')
        self.editor.bind_key_handler(buf.command_key_handler, '.op',
            lambda buf: self.oracle(buf, 'peers'),
            'golang oracle: peers')
        self.editor.bind_key_handler(buf.command_key_handler, '.ot',
            lambda buf: self.oracle(buf, 'referrers'),
            'golang oracle: referrers')

    def provide(self, buf, word, candidates):
        if not word:
            it = buf.get_iter_at_mark(buf.get_insert())
            if it.backward_char():
                if not it.get_char() in {'.'}: return
            else: return
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

    def gofmt(self, buf):
        p = subprocess.Popen(['/usr/bin/env', 'gofmt', '-s'],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE)
        data, err = p.communicate(buf.get_text(buf.get_start_iter(),
            buf.get_end_iter(), False).encode('utf8'))
        if len(err) > 0: # error
            self.editor.show_message(err.decode('utf8'), timeout = 3600000)
            return
        offset = buf.get_iter_at_mark(buf.get_insert()).get_offset()
        buf.set_text(data.decode('utf8'))
        it = buf.get_start_iter()
        it.set_offset(offset)
        buf.place_cursor(it)

    def oracle(self, buf, mode, scope = None):
        if not buf.get_has_selection(): # select current word
            Transform(
                (self.editor.mark_jump_to_word_edge, 0, True),
                (self.editor.mark_jump_to_word_edge, 0),
                'cursor').apply(buf)
        start = len(buf.get_text(buf.get_start_iter(),
            buf.get_iter_at_mark(buf.get_selection_bound()), False).encode('utf8'))
        end = len(buf.get_text(buf.get_start_iter(),
            buf.get_iter_at_mark(buf.get_insert()), False).encode('utf8'))
        pos = buf.attr['filename'] + ':' + '#' + str(start) + ',#' + str(end)
        if scope is None:
            scope = buf.attr['filename']
        output = subprocess.check_output(['/usr/bin/env', 'oracle',
            '-pos=' + pos,
            '-format=plain',
            mode,
            scope])
        self.editor.show_message(output.decode('utf8'), timeout = 600000)
