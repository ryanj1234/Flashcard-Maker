import logging

class VocabWord(object):
  def __init__(self, word, part_of_speech=''):
    self.logger = logging.getLogger(__name__)
    self.word = word
    self.part_of_speech = part_of_speech
    self.definitions = []
    
  def add_definition(self, def_str, examples=[]):
    self.definitions.append({'text': def_str, 'examples': examples})
  
  @property
  def num_defs(self):
    return len(self.definitions)
    
  def __str__(self):
    self_str = '{}: {}\n'.format(self.word, self.part_of_speech)
    for i, d in enumerate(self.definitions):
      self_str += '\t{}. {}\n'.format(i+1, d['text'])
      for ex in d['examples']:
        self_str += '\t\t-{}\n'.format(ex)
        
    return self_str

if __name__ == '__main__':
  pass