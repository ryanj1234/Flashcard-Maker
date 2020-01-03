import os
from abc import ABC, abstractmethod
import logging

import pyforvo
from vocabword import VocabWord


class ParserBase(ABC):
    @abstractmethod
    def to_word(self, selection):
        pass


class AudioParser(ABC):
    @abstractmethod
    def get_audio_file(self):
        pass

    @property
    def found(self):
        return self._found


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
            self_str += w.__str__ + '\n'

        return self_str


try:
    with open('api.txt', 'r') as w:
        api_key = w.read().rstrip()
except FileNotFoundError:
    with open('../api.txt', 'r') as w:
        api_key = w.read().rstrip()


def get_forvo_filename(word):
    return 'pronunciation_{}_{}.mp3'.format(word.language, word.word)


class ForvoParser(AudioParser):
    forvo = pyforvo.ForvoAgent(api_key)

    def __init__(self, word, pref_user=None, language='ru', out_dir='.media'):
        self.logger = logging.getLogger(__name__)
        self.word = word
        self.out_dir = out_dir
        self.pronunciation = None
        self._found = False

        self.prons = ForvoParser.forvo.query(self.word, language, pref_user)

        if not os.path.exists(self.out_dir):
            os.mkdir(self.out_dir)

        self.file_path = ''

        if not self.prons.download_preferred():
            self.logger.debug("No preferred downloads found for word %s", self.word)

    @property
    def num_prons(self):
        return self.prons.num_pron

    def select(self, idx):
        self.pronunciation = self.prons[idx]

    def get_audio_file(self):
        return self.file_path

    def _download(self):
        if self.pronunciation:
            self.file_path = self.pronunciation.download(out_dir=self.out_dir)
        else:
            self.logger.error('No pronunciations')


def get_input(msg):
    return input(msg)


class CommandLineForvoParser(ForvoParser):
    def __init__(self, *args, **kwargs):
        super(CommandLineForvoParser, self).__init__(*args, **kwargs)

    def download(self):
        if not self.num_prons:
            print("No pronunciations!")
            return

        if self.num_prons > 1:
            self.print_options()
            selection = self.get_selection(1, self.num_prons)
            self.pronunciation = self.prons.get(selection)

        self._download()

    def print_options(self):
        for i, p in enumerate(self.prons):
            print("{}): {}".format(i + 1, p))

    def get_selection(self, sel_min, sel_max):
        while True:
            c = get_input("Select ({}-{}): ".format(sel_min, sel_max))
            try:
                selection = int(c)
            except ValueError:
                selection = -1

            if sel_min <= selection <= sel_max:
                break
            else:
                print("Please input a value between {} and {}".format(sel_min, sel_max))

        self.logger.debug('User selected %d', selection)

        return selection - 1  # convert selection to an index


if __name__ == '__main__':
    a = CommandLineForvoParser('идти', preferred_users='luba1980')
    # a.print_options()
    a.download()
