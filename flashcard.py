import wikitools
from parsers import SelfParse, ForvoParser, CommandLineForvoParser
from vocabword import VocabWord


class Flashcard(object):
    def __init__(self, word, language='russian', opts=None):
        self.word = word
        self.language = language
        self.audio_file = ''
        self._audio_parsers = []

        if opts is not None:
            self.opts = opts
        else:
            self.opts = []

        self.defs = []
        self._parsers = []
        self.has_def = False
        self.has_audio = False

        if 'self_parse' in self.opts:
            self._parsers.append(SelfParse)

        if 'no_cmd_line' in self.opts:
            self._parsers.append(wikitools.WikiParser)
        else:
            self._parsers.append(wikitools.CommandLineWikiParser)

        self._audio_parsers = [CommandLineForvoParser]

        self._parse()

    @property
    def num_defs(self):
        return len(self.defs)

    def _parse(self):
        w = VocabWord(self.word)
        for p in self._parsers:
            parser = p(self.word, self.language, self.opts)
            w = parser.to_word()
            if w.found():
                self.has_def = True
                for d in w.definitions:
                    self.defs.append(d)
                break

        if w.has_audio:
            w.get_audio()
            self.audio_file = w.get_audio_file()
        else:
            for ap in self._audio_parsers:
                a = ap(w.word, pref_user='1640max')
                if a.found:
                    self.audio_file = a.get_audio_file()

    def get_def(self, idx):
        return self.defs[idx]['text']

    def get_audio_file(self):
        return self.audio_file


if __name__ == '__main__':
    # card = Flashcard('идти')
    card = Flashcard('идти:verb:to go:to walk:(of precipitation) to fall:to function, to work:to suit, to become (of '
                     'wearing clothes):(used in expressions)', opts=['self_parse'])
    for i in range(card.num_defs):
        print(card.get_def(i))

    print(card.get_audio_file())
