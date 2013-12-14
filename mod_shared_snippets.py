class ModSharedSnippets:
    def __init__(self, editor):
        self.editor = editor

        # curly braces
        editor.connect('language-detected', lambda _, buf, lang:
            self.setup_curly_braces(buf) if lang in {
                'Rust',
                'Go',
            } else None)

        # c-like function call
        editor.connect('language-detected', lambda _, buf, lang:
            self.setup_c_like_function(buf) if lang in {
                'Rust',
                'Go',
                'Python',
            } else None)

    def setup_curly_braces(self, buf):
        self.editor.add_pattern(buf, '{{', lambda buf:
            self.editor.insert_snippet(buf, [
                '{$>',
                '$1$<',
                '}$2',
            ]),
            drop_key_event = True, clear_matched_text = True)

    def setup_c_like_function(self, buf):
        self.editor.bind_key_handler(buf.command_key_handler, '.fv', lambda view:
            self.editor.feed_keys(view, 'vmwvt(v%vl'),
            'select current function call')
        self.editor.bind_key_handler(buf.command_key_handler, '.fi', lambda view, buf: [
            self.editor.feed_keys(view, 'f(%i'),
            buf.begin_user_action(),
            buf.insert(buf.get_iter_at_mark(buf.get_insert()),
                ', ', -1),
            buf.end_user_action(),
            ], 'insert argument to current function')
