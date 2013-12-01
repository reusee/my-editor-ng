jedi = None

class Jedi:
  def __init__(self, editor):
    editor.connect('language-detected', lambda _, buf, lang:
      self.setup(buf) if lang == 'Python' else None)
    editor.connect('provide-completions', self.provide)

  def setup(self, buf):
    global jedi
    if not jedi is None: return
    jedi = __import__('jedi')
    print('jedi loaded')
    settings = jedi.settings
    settings.add_dot_after_module = True
    settings.add_bracket_after_function = True

  def provide(self, _, buf, word, candidates):
    if not word:
      it = buf.get_iter_at_mark(buf.get_insert())
      if it.backward_char():
        if not it.get_char() in {'.'}: return
      else: return
    text = buf.get_text(buf.get_start_iter(),
      buf.get_end_iter(), False)
    it = buf.get_iter_at_mark(buf.get_insert())
    line = it.get_line() + 1
    column = it.get_line_offset()
    script = jedi.Script(
      source = text,
      line = line,
      column = column,
      path = None
      )
    for c in script.completions():
      if c.name.startswith('__'): continue
      candidates.add(c.name)
