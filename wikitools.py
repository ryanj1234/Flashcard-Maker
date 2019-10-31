import os
import re
import logging
import socket

from pydub import AudioSegment
from wiktionaryparser import WiktionaryParser
from parsers import ParserBase, AudioParser
from vocabword import VocabWord
from vocabword import strip_accents
import urllib.parse
import urllib.request

logging.basicConfig(level=logging.INFO)


def wiki_url_to_file(url):
    return urllib.parse.unquote(url.split('/')[-1])


class WikiWord(VocabWord):
    def __init__(self, word, dat, audio=None):
        super(WikiWord, self).__init__('')
        self.word = word
        self.part_of_speech = ''
        self.audio_url = ''
        self.audio = audio if audio else []
        self.audio_file = ''
        if dat:
            self._parse_def(dat)

        if audio:
            self._parse_audio(audio)

    def found(self):
        return self.word != ''

    def get_audio(self, audio_sel=0):
        if self.audio_url:
            a = WikiAudioParser(self.audio_url)
            self.audio_file = a.get_file()
        else:
            # implement forvo downloader
            print("No audio found for word {}".format(self.word))

    def _parse_desc(self, desc):
        sp = desc.split()
        self.word = strip_accents(sp[0])

    def _parse_audio(self, audio):
        if len(audio) > 1:
            self.logger.info('Multiple URLs found for word %s. Only using the first', self.word)

        self.audio_url = audio[0]

    def _parse_def(self, wiki_dat):
        self.part_of_speech = wiki_dat.get('partOfSpeech', '')
        for i, t in enumerate(wiki_dat.get('text', [])):
            self.logger.debug('Parsing line %s', t)
            if i == 0:
                self._parse_desc(t)
            else:
                bw = self.find_base_word(t)
                if bw and bw not in self.base_words:
                    self.base_words.append(bw)
                self.add_definition(t)

    def find_base_word(self, text):
        # check for base word in definition text.
        expr = re.search(r"[' ']of[' '](.+)[' ']\(.+\)", text)
        self.logger.debug("Searching for base word in line %s", text)

        if not expr:
            self.logger.debug('No base word found')
            return ''

        self.logger.debug('Base word %s found', strip_accents(expr.group(1)))

        return strip_accents(expr.group(1))


def is_empty(wiki_dat):
    for w in wiki_dat:
        if w['etymology'] != '':
            return False
        elif len(w['definitions']) > 0:
            return False
    return True


class WikiParser(ParserBase):
    parser = WiktionaryParser()

    def __init__(self, word, language='russian', opts=None):
        self.logger = logging.getLogger(__name__)
        raw_dat = WikiParser.parser.fetch(word, language)
        self.words = []
        self.base_words = []
        self.opts = opts if opts else []
        self.found = False
        self.selection = -1
        self._audio_file = ''

        if is_empty(raw_dat):
            print("No data found for word {}!".format(word))

        for w in raw_dat:
            audio = w.get('pronunciations', {}).get('audio', [])
            for dat in w.get('definitions', []):
                ww = WikiWord(word, dat, audio)
                self.words.append(ww)
                self.base_words += ww.base_words

    @property
    def num_base_words(self):
        return len(self.base_words)

    @property
    def num_words(self):
        return len(self.words)

    def to_word(self, selection):
        if not self.num_words:
            return WikiWord('', '')

        self.selection = selection
        return self.words[selection]

    def to_base(self, base_selection=0):
        self.logger.info("Converting to base word %s", self.base_words[base_selection])
        return WikiParser(self.base_words[base_selection])


def get_input(msg):
    return input(msg)


def get_yn():
    while True:
        inp = get_input('Enter Selection (y/n): ')
        if inp == 'y' or inp == 'n':
            break
    return inp


class CommandLineWikiParser(WikiParser):
    def __init__(self, *args):
        super(CommandLineWikiParser, self).__init__(*args)

    def to_word(self, sel=None):
        # TODO: test
        sel_made = False
        if self.num_words == 0:
            print("No words found!")
            return WikiWord('', '')
        # case: user did not provide a selection and there is only one choice
        elif not sel and self.num_words == 1:
            sel = 0
        # case: user did not provide a selection but there are multiple choices
        elif not sel and self.num_words > 1:
            print("Multiple words detected {}".format(self.num_words))
            self.print_words()
            sel = self.get_selection(1, self.num_words)
            sel_made = True

        # case: there is a base word in the selection and it is the only def
        if self.words[sel].num_base == 1 and self.words[sel].num_defs == 1:
            base_wik = CommandLineWikiParser(self.words[sel].base_words[0])
            return base_wik.to_word()
        # there is a base word but there are multiple defs
        elif self.words[sel].num_base == 1 and self.words[sel].num_defs > 1:
            self.print_words()
            print("Use base word {}?".format(self.words[sel].base_words[0]))
            res = get_yn()
            if res == 'y':
                base_wik = CommandLineWikiParser(self.words[sel].base_words[0])
                return base_wik.to_word()
        # there are multiple base words
        elif self.words[sel].num_base > 1:
            self.print_base_words()
            print("FIXME: Select the word you would like to use: ")
            base_wik = CommandLineWikiParser(self.words[sel].base_words[0])
            return base_wik.to_word()

        return super(CommandLineWikiParser, self).to_word(sel)

    def print_words(self):
        for i, wor in enumerate(self.words):
            print('{}) {}'.format(i + 1, wor))

    def print_base_words(self):
        for i, wor in enumerate(self.base_words):
            print('{}) {}'.format(i + 1, wor))

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


class WikiAudioParser(AudioParser):
    def __init__(self, audio_url, out_dir='.media'):
        self.logger = logging.getLogger(__name__)
        self.out_dir = out_dir
        self.out_file_mp3 = ''

        filename = wiki_url_to_file(audio_url)
        if not os.path.exists(self.out_dir):
            os.mkdir(self.out_dir)

        self.out_file_ogg = os.path.join(self.out_dir, filename)
        # noinspection PyBroadException
        try:
            urllib.request.urlretrieve('http:' + audio_url, self.out_file_ogg)
        except:
            self.logger.error("An error occurred while downloading audio file", exc_info=True)
            return

        self.convert_to_mp3()

    def convert_to_mp3(self):
        self.out_file_mp3 = self.out_file_ogg.replace('.ogg', '.mp3')
        AudioSegment.from_file(self.out_file_ogg).export(self.out_file_mp3, format="mp3")

    def get_file(self):
        return self.out_file_mp3


if __name__ == '__main__':
    f = open('words.txt', 'r')
    lines = f.readlines()
    for w in lines[:-1]:
        if not w:
            continue
        wik = CommandLineWikiParser(w[:-1])
        wrd = wik.to_word()
        wrd.get_audio()
        print("Final selection: ")
        print(wrd)
    f.close()
    # wik = CommandLineWikiParser('ход')
    # word = wik.to_word(0)
    # print("Selection: ")
    # print(word)
    # wik = WikiParser('идти')
    # w = wik.to_word(0)
    # wik.get_audio()
    # print(wik.audio_file)
