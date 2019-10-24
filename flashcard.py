import wikitools

class Flashcard():
  def __init__(self, word, language='russian', opts=[]):
    self.word = word
    self.language = language
    self.opts = opts
    self.defs = []
    
    self._parsers = []
    
    self.has_def = False
    self.has_audio = False
    
    if 'no_cmd_line' in opts:
      self._parsers.append(wikitools.WikiParser)
    else:
      self._parsers.append(wikitools.CommandLineWikiParser)
      
    self._parse()
    
  def _parse(self):
    for p in self._parsers:
      parser = p(self.word, self.language, self.opts)
      w = parser.to_word()
      if w.found():
        self.has_def = True
        for d in w.definitions:
          self.defs.append(d)
        return

  def get_def(self, idx):
    return self.defs[idx]['text']
    
if __name__ == '__main__':
  card = Flashcard('коотить')
  print(card.get_def(0))