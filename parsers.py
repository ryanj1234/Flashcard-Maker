from abc import ABC, abstractmethod
import logging
from vocabword import VocabWord


class ParserBase(ABC):
    @abstractmethod
    def to_word(self, selection):
        pass


class AudioParser(ABC):
    @abstractmethod
    def get_file(self):
        pass


class SelfParse(ParserBase):
    def __init__(self, word, language='russian', opts=None):
        self.logger = logging.getLogger(__name__)
        self.found = False
        self.words = []
        self._parse(word)

    def _parse(self, dat):
        if ':' not in dat:
            self.logger.error("No delimiter found in word")
            return

        tmp = dat.split(':')
        word = ''
        part_of_speech = ''
        definition = []

        if len(tmp) == 2:
            word = tmp[0]
            definition = [tmp[1]]
        elif len(tmp) > 2:
            word = tmp[0]
            part_of_speech = tmp[1]
            definition = tmp[2:]

        w = VocabWord(word, part_of_speech)

        for d in definition:
            w.add_definition(d)

        self.words.append(w)
        self.found = True

    def found(self):
        return self.found

    @property
    def num_words(self):
        return len(self.words)

    def to_word(self, selection=0):
        return self.words[selection]

    def __str__(self):
        self_str = ''
        for w in self.words:
            self_str += w.__str__() + '\n'

        return self_str


if __name__ == '__main__':
    pass
