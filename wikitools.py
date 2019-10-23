import os
import json
import re
import logging
import unicodedata
from wiktionaryparser import WiktionaryParser
from vocabword import VocabWord

logging.basicConfig(level=logging.INFO)

class WikiWord(VocabWord):
  def __init__(self, wiki_dat):
    super(WikiWord, self).__init__('')
    self.desc = ''
    self.word = ''
    self.audio_url = ''
    self.base_words = []
    if wiki_dat:
      self._parse(wiki_dat)
    
  def _parse_desc(self, desc):
    sp = desc.split()
    self.word = self.strip_accents(sp[0])
    
  @property
  def has_base(self):
    return len(self.base_words) > 0
    
  def _parse(self, wiki_dat):
    for d in wiki_dat.get('definitions', []):
      self.part_of_speech = d.get('partOfSpeech', '')
      for i, t in enumerate(d.get('text', [])):
        self.logger.debug('Parsing line %s', t)
        if i == 0:
          self._parse_desc(t)
        else:
          bw = self.find_base_word(t)
          if bw:
            self.base_words.append(bw)
          self.add_definition(t)
          
    urls = wiki_dat.get('pronunciations', {}).get('audio', [])
    if not urls:
      self.logger.debug('No audio URLs found for word %s', self.word)
      return
      
    if len(urls) > 1:
      self.logger.info('Multiple URLs found for word %s. Only using the first', self.word)
    
    self.audio_url = urls[0]
    
  def strip_accents(self, s):
    # credit to user 'oefe'
    # taken from https://stackoverflow.com/questions/517923/ \
    #        what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
    ikrat = [i for i, ltr in enumerate(s) if ltr == 'й']
    self.logger.debug("Stripping accents from {}".format(s))
    tmp = ''.join(c for c in unicodedata.normalize('NFD', s)
                if (unicodedata.category(c) != 'Mn'))

    str.replace(tmp, unicodedata.normalize('NFD', 'ё'), 'ё')
    for i in ikrat:
        tmp = tmp[:i - 1] + 'й' + tmp[i + 1:]

    self.logger.debug("Word without accents %s", tmp)

    return tmp
    
  def find_base_word(self, text):
    # check for base word in definition text.
    expr = re.search(r"[' ']of[' '](.+)[' ']\(.+\)", text)
    self.logger.debug("Searching for base word in line %s", text)

    if not expr:
      self.logger.debug('No base word found')
      return ''
        
    self.logger.debug('Base word %s found', self.strip_accents(expr.group(1)))

    return self.strip_accents(expr.group(1))


class WikiParser:
  parser = WiktionaryParser()
  def __init__(self, word, language='russian', opts=[]):
    self.logger = logging.getLogger(__name__)
    raw_dat = WikiParser.parser.fetch(word, language)
    self.words = []
    self.base_words = []
    self.opts = opts
    for w in raw_dat:
      ww = WikiWord(w)
      self.words.append(ww)
      self.base_words += ww.base_words

  @classmethod
  def build_from_file(cls, file_name):
    dat = ['']
    with open(file_name, 'r') as f:
      dat = json.load(f)
      
    return cls(dat)
    
  @property
  def num_base_words(self):
    return len(self.base_words)

  @property
  def num_words(self):
    return len(self.words)
    
  def to_word(self, selection):
    return self.words[selection]
    
  def to_base(self, base_selection=0):
    self.logger.info("Converting to base word %s", self.base_words[base_selection])
    return WikiParser(self.base_words[base_selection])
    
  def __str__(self):
    self_str = ''
    for w in self.words:
      self_str += w.__str__() + '\n'
      
    return self_str
    
    
class CommandLineWikiParser(WikiParser):
  def __init__(self, *args):
    super(CommandLineWikiParser, self).__init__(*args)
    
  def to_word(self, sel=None):
    # case: user did not provide a selection and there is only one choice
    if not sel and self.num_words == 1:
      print("Sel: 0")
      sel = 0
    # case: user did not provide a selection but there are multiple choices
    elif not sel:
      print("Multiple words detected {}".format(self.num_words))
      sel = self.get_selection()
    
    # case: there is a base word in the selection and it is the only def
    if len(self.words[sel].base_words) == 1 and self.words[sel].num_defs == 1:
      print("Base word!")
      base_wik = CommandLineWikiParser(self.words[sel].base_words[0])
      return base_wik.to_word()
    # there is a base word but there are multiple defs
    elif len(self.words[sel].base_words) == 1 and self.words[sel].num_defs > 1:
      print("Use base word {}?".format(self.words[sel].base_words[0]))
      res = self.get_yn()
      if res == 'y':
        base_wik = CommandLineWikiParser(self.words[sel].base_words[0])
        return base_wik.to_word()
    # there are multiple base words
    elif len(self.words[sel].base_words) > 1:
      print("Select the word you would like to use: ")
      base_wik = CommandLineWikiParser(self.words[sel].base_words[0])
      return base_wik.to_word()
    
    return super(CommandLineWikiParser, self).to_word(sel)
    
  def get_input(self, msg):
    return input(msg)
    
  def to_base(self, base_selection=0):
    self.logger.info("Converting to base word %s", self.base_words[base_selection])
    return CommandLineWikiParser(self.base_words[base_selection])
    
  def get_yn(self):
    while True:
      inp = input('Enter Selection (y/n): ')
      if inp == 'y' or inp == 'n':
        break
    return inp
    
  def get_selection(self):
    if self.num_words == 0:
      print("No words to choose from!")
      return 0

    for i, w in enumerate(self.words):
      print('{}) {}'.format(i+1, w))
      
    selection = -1
    while True:
      c = self.get_input("Select (1-{}): ".format(self.num_words))
      try:
        selection = int(c)
      except ValueError:
        selection = -1
        
      if selection > 0 and selection <= self.num_words:
        break
      else:
        print("Please input a value between 1 and {}".format(self.num_words))
        
    self.logger.debug('User selected %d', selection)
        
    return selection-1 # convert selection to an index

if __name__ == '__main__':
  words = []
  # words.append('колотить')
  words.append('пила')
  # words.append('идти')
  # words.append('пугаться')
  
  for word in words:
    wik = CommandLineWikiParser(word)
    w = wik.to_word()
    print(w)
