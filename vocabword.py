import logging
import unicodedata


def strip_accents(s):
    # credit to user 'oefe'
    # taken from https://stackoverflow.com/questions/517923/ \
    #        what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
    ikrat = [i for i, ltr in enumerate(s) if ltr == 'й']
    tmp = ''.join(c for c in unicodedata.normalize('NFD', s)
                  if (unicodedata.category(c) != 'Mn'))

    str.replace(tmp, unicodedata.normalize('NFD', 'ё'), 'ё')
    for i in ikrat:
        tmp = tmp[:i - 1] + 'й' + tmp[i + 1:]

    return tmp


class VocabWord(object):
    def __init__(self, word, part_of_speech=''):
        self.logger = logging.getLogger(__name__)
        self.word = word
        self.part_of_speech = part_of_speech
        self.definitions = []
        self.base_words = []

    def add_definition(self, def_str, examples=[]):
        self.definitions.append({'text': def_str, 'examples': examples})

    def get_definition(self, idx):
        return strip_accents(self.definitions[idx]['text'])

    def found(self):
        return self.found

    @property
    def num_defs(self):
        return len(self.definitions)

    @property
    def num_base(self):
        return len(self.base_words)

    def __str__(self):
        self_str = '{}: {}\n'.format(self.word, self.part_of_speech)
        for i, d in enumerate(self.definitions):
            self_str += '\t{}. {}\n'.format(i + 1, strip_accents(d['text']))
            for ex in d['examples']:
                self_str += '\t\t-{}\n'.format(ex)

        return self_str


if __name__ == '__main__':
    pass
