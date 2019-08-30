#!/usr/bin/env python3
import os
import re
import logging
from wiktionaryparser import WiktionaryParser
from pyforvo.api import Forvo
import wget
import urllib.parse
import unicodedata

verb_keywords = ['masculine', 'feminine', 'past', 'indicative', 'perfective', 'imperfective',
                 'first-person', 'singular', 'indicative', 'second-person', 'third-person',
                 'plural', 'future', 'imperative']

adjective_keywords = ['nominative', 'accusative', 'genitive', 'prepositional', 'instrumental',
                      'dative', 'plural', 'singular', 'neuter', 'masculine', 'feminine']

adjective_endings = ['ое', 'ая', 'ые', 'ого', 'ой', 'ых', 'ому', 'ым', 'ою', 'ыми', 'ом']
verb_endings = ['л', 'ла', 'ло', 'ли']
reflexive_verb_endings = ['лся', 'лась', 'лось', 'лись']

parser = WiktionaryParser()

def get_audio_url(word):
    if word and 'pronunciations' in word[0]:
        urls = word[0]['pronunciations']['audio']

        if len(urls) >= 1:
            url = 'http:' + urls[0]
            logging.debug("URL: " + url)
            return url

    return ''


def get_name_from_url(url):
    decode = urllib.parse.unquote(url)

    fname = decode.split('/')[-1]
    print("Name from URL: {}".format(fname))

    return fname


def get_audio_file(url, quiet=False):
    output = ' > /dev/null 2>&1' if quiet else ''
    out_dir = 'vocab'

    stat = os.system('wget ' + url + output)
    if stat != 0:
        logging.error('Error downloading audio file!')
        return ''

    fname_ogg = get_name_from_url(url)
    fname_mp3 = fname_ogg.replace('.ogg', '.mp3')

    # convert to mp3
    stat = os.system('ffmpeg -i ' + fname_ogg + ' ' + fname_mp3 + output)

    if stat != 0:
        logging.error("Error converting file to mp3!")
        return ''

    # remove ogg file
    stat = os.system('rm ' + fname_ogg)

    if stat != 0:
        logging.error("Error removing ogg file!")
        return ''

    # move to folder
    stat = os.system('mv ' + fname_mp3 + ' ' + out_dir + output)

    if stat != 0:
        logging.error("Error copying mp3 file to final destination")
        return ''

    return os.path.join(out_dir, fname_mp3)


def print_definitions(word):
    stat = False
    if not word:
        return stat

    for sub_word in word:
        definitions = get_definitions(sub_word)

        for line in definitions:
            stat = True
            print(line)

    return stat


def parse_definition_from_wik(word):
    def_str = []
    part_of_speech = ''

    if not 'definitions' in word:
        return def_str, part_of_speech

    def_num = 1
    for defs in word['definitions']:
        if 'partOfSpeech' in defs:
            part_of_speech = defs['partOfSpeech']
            def_str.append("<b>" + part_of_speech + "</b><br>")
        else:
            part_of_speech = ''

        for i, line in enumerate(defs.get('text')):
            if i == 0:
                def_str.append(line)
                def_str.append("<ol>")
            else:
                def_str.append("<li>" + line + "</li>")
        def_str.append("</ol>")

        def_num += 1

    return def_str, part_of_speech


def parse_definition_from_wik2(wik):
    def_str = []
    word = []
    for word in wik:
        if not 'definitions' in word:
            print("Definitions not in word!!!")
            print(word)
            return def_str

        for defs in word['definitions']:
            if 'partOfSpeech' in defs:
                part_of_speech = defs['partOfSpeech']
                def_str.append(part_of_speech)
            else:
                part_of_speech = ''

            for line in defs.get('text'):
                print("Appending line: {}".format(line))
                def_str.append(line)

    return def_str


def check_for_base(word, word_str):
    base_word = ''
    no_text_found = True

    for sub_word in word:
        if 'definitions' in sub_word:
            for defs in sub_word['definitions']:
                if 'partOfSpeech' in defs:
                    part_of_speech = defs['partOfSpeech']
                else:
                    part_of_speech = ''
                    pass

                if 'text' in defs:
                    if defs['text']:
                        no_text_found = False
                        base_word = check_for_base_word(defs['text'], part_of_speech)
                    else:
                        logging.debug("No text found for word")
                else:
                    logging.debug("No text found")
        else:
            logging.debug("No definitions found")

    if no_text_found:
        # try to change to base word
        logging.debug("Text field empty for word {}".format(word_str))
        poss = get_possible_base_words(word_str)

        for base_word in poss:
            wik = get_wiki(base_word, check_base=False)
            if check_for_def(wik):
                break

    return base_word


def check_for_def(wik):
    for word in wik:
        for defs in word.get("definitions"):
            if defs.get("text"):
                return True

    return False


def get_possible_base_words(word_str):
    poss = []

    # check for adjective
    for ending in adjective_endings:
        if ending in word_str:
            for base_ends in ['ой', 'ый', 'ий']:
                word = str.replace(word_str, ending, base_ends)
                poss.append(word)
                logging.debug("Appending word: {}".format(word))
    for ending in verb_endings:
        if ending in word_str:
            word = str.replace(word_str, ending, 'ть')
            logging.debug("Appending word: {}".format(word))
    for ending in reflexive_verb_endings:
        if ending in word_str:
            word = str.replace(word_str, ending, 'ться')
            logging.debug("Appending word: {}".format(word))

    return poss

def check_for_base_word(text, part_of_speech):
    possible_lines = []

    if part_of_speech == 'verb':
        keywords = verb_keywords
    elif part_of_speech == 'adjective':
        keywords = adjective_keywords

    for line in text:
        for kw in verb_keywords:
            if kw in line:
                possible_lines.append(line)
                break

    for line in possible_lines:
        word = find_base_word(line)
        if word:
            return word

    return ''

def find_base_word(text):
    # check for base word in definition text.
    expr = re.search(r"[' ']of[' '](.+)[' ']\(.+\)", text)
    logging.debug("Searching for base word in line {} ".format(text))

    if not expr:
        return ''

    return strip_accents(expr.group(1))


def strip_accents(s):
    # credit to user 'oefe'
    # taken from https://stackoverflow.com/questions/517923/ \
    #        what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
    ikrat = [i for i, ltr in enumerate(s) if ltr == 'й']
    logging.debug("Stripping accents from {}".format(s))
    tmp = ''.join(c for c in unicodedata.normalize('NFD', s)
                if (unicodedata.category(c) != 'Mn'))

    str.replace(tmp, unicodedata.normalize('NFD', 'ё'), 'ё')
    for i in ikrat:
        tmp = tmp[:i - 1] + 'й' + tmp[i + 1:]

    logging.debug("Word without accents {}".format(tmp))

    return tmp


def get_wiki(word, check_base=True):
    # fetch the wiki for a given word. If a wiki is detected to point to a base
    # word that will be returned instead. If no wiki is found, endings will be
    # replaced in an attempt to find a base word.
    wik = parser.fetch(word, 'russian')

    logging.debug("Wiki found for word: {}".format(word))

    logging.debug(wik)
    if wik:
        if check_base:
            base_word = check_for_base(wik, word)

            if base_word:
                logging.info("Replacing input '{}' with base word found: '{}'".format(word, base_word))
                wik = parser.fetch(base_word, 'russian')
                word = base_word

    else:
        print("Word '{}' not found!".format(word))

    return wik, word


def isempty_wiki(wik):
    for words in wik:
        if words.get('definitions'):
            return False
    print("Empty wiki found")
    return True

def get_pronunciation(wik):
    url = get_audio_url(wik)
    if url:
        return get_audio_file(url)

    logging.error("*** Pronunciation not found ***")
    return ''


class WikiDefinition(object):
    def __init__(self, text):
        self.def_str_raw = []
        self.def_str_fmt = []
        self.part_of_speech = ''
        self.examples = []
        self.base_words = []

        self.parse(text)
        self.check_for_base_word()

    def parse(self, text):
        if 'partOfSpeech' in text:
            self.part_of_speech = text['partOfSpeech']
            self.def_str_raw.append(self.part_of_speech)
            self.def_str_fmt.append("<b>" + self.part_of_speech + "</b><br>")

        for i, line in enumerate(text.get('text')):
            if i == 0:
                self.def_str_raw.append(line)
                self.def_str_fmt.append("<ol>")
            else:
                self.def_str_raw.append(line)
                self.def_str_fmt.append("<li>" + line + "</li>")
        self.def_str_fmt.append("</ol>")

    def check_for_base_word(self):
        possible_lines = []
        word = ''

        if self.part_of_speech == 'verb':
            keywords = verb_keywords
        elif self.part_of_speech == 'adjective':
            keywords = adjective_keywords

        for line in self.def_str_raw:
            for kw in verb_keywords:
                if kw in line:
                    possible_lines.append(line)
                    break

        for line in possible_lines:
            base_word = find_base_word(line)
            self.base_words.append(base_word) if base_word else False

    def get_formatted_str(self):
        self_str = ''
        for line in self.def_str_fmt:
            self_str += line

        return self_str

    def __str__(self):
        self_str = ''
        for line in self.def_str_raw:
            self_str += line + '\n'

        return self_str


class ForvoGetter(object):
    def __init__(self, api_file):
        with open(api_file, 'r') as f:
            apikey = f.read().rstrip()
            self.getter = Forvo(apikey)
            self.getter.pronunciations('сказать')

class Pronunciation(object):
    forvoGet = ForvoGetter('apikey.txt').getter

    def __init__(self, word, quiet=False):
        self.logger = logging.getLogger(__name__)
        self.wik = word.wik
        self.word = word.word
        self.MAX_GET = 5
        self.urls = self.get_wiki_urls()
        self.pronunciations = []
        self.output = ' > /dev/null 2>&1' if quiet else ''
        self.out_dir = 'vocab'

    def downloaded_file(self):
        if not self.urls:
            logging.info("No pronunciations found on wiktionary, trying Forvo...")
            return self.download_from_forvo()

        return self.download_from_wiki()

    def get_wiki_urls(self):
        print("Getting wiki pronunciations for word {}".format(self.word))
        for word in self.wik:
            if word and 'pronunciations' in word:
                urls = word['pronunciations']['audio']

                if urls:
                    return 'http:' + urls[0]

                return ''

    def download_from_forvo(self):
        print("Getting forvo pronunciations for word {}".format(self.word))
        pron = Pronunciation.forvoGet.pronunciations(self.word)

        len_opts = len(pron)
        print("Len pron: {}".format(len_opts))
        if len_opts == 0:
            print("No files found!")
            return
        elif len_opts == 1:
            print("Only 1 file found, downloading")
            fname = self.word + '.mp3'
            pron[0].download(fname)
            return self._move_to_output(fname)

        for i, pronunciation in enumerate(pron):
            if i > self.MAX_GET:
                break
            fname = self.create_fname(i)
            print("Playing file {}!".format(fname))
            pronunciation.play()
            self.pronunciations.append(pronunciation)
            #pronunciation.download(fname)

        self.print_pron_opts()

        inp = ''
        while inp != 'q':
            inp = input("Enter the number of the file you would like to use, or enter r to hear them again: ")
            try:
                val = int(inp)
                if val < len_opts:
                    print("Downloading file: {}".format(inp))
                    fname = self.word + '.mp3'
                    self.pronunciations[val].download(fname)
                    return self._move_to_output(fname)
                    inp = 'q'
            except ValueError:
                pass

    def print_pron_opts(self):
        for i, pronunciation in enumerate(self.pronunciations):
            print("{}: {}".format(i, "filename"))

    def create_fname(self, i):
        return self.word + str(i) + '.mp3'

    def download_from_wiki(self, quiet=False):
        if len(self.urls) == 0:
            return ''

        url = self.urls
        print("Downloading url: " + url)
        stat = os.system('wget ' + url + self.output)
        if stat != 0:
            logging.error('Error downloading audio file!')
            print(self.output)
            return ''

        fname_ogg = get_name_from_url(url)
        fname_mp3 = fname_ogg.replace('.ogg', '.mp3')

        # convert to mp3
        print('ffmpeg -i ' + fname_ogg + ' ' + fname_mp3 + self.output)
        stat = os.system('ffmpeg -i ' + fname_ogg + ' ' + fname_mp3 + self.output)

        if stat != 0:
            logging.error("Error converting file to mp3!")
            return ''

        # remove ogg file
        stat = os.system('rm ' + fname_ogg)

        if stat != 0:
            logging.error("Error removing ogg file!")
            return ''

        return self._move_to_output(fname_mp3)

    def _move_to_output(self, fname_mp3):
        # move to folder
        stat = os.system('mv ' + fname_mp3 + ' ' + self.out_dir + self.output)

        if stat != 0:
            logging.error("Error copying mp3 file to final destination")
            return ''

        return os.path.join(self.out_dir, fname_mp3)


class VocabWord(object):
    parser = WiktionaryParser()

    def __init__(self, word):
        self.word = word
        self.base_word = ''
        self.entries = []
        self.pronunciations = []
        self.audio_found = False
        self.definition_found = False

        self.logger = logging.getLogger(__name__)
        self.logger.info("*** Generating card for word {} ***".format(word))

        self.wik = VocabWord.parser.fetch(word, 'russian')
        self.get_definition()
        self.get_pronunciation()

        self.print_definitions()

    def get_definition(self):
        self._get_entries()
        self._check_for_base_word()
        if self.base_word != '' and self.base_word != self.word:
            self.word = self.base_word
            self.wik = VocabWord.parser.fetch(self.word, 'russian')
            self._get_entries()

    def get_pronunciation(self):
        pronunciation = Pronunciation(self)
        self.audio = pronunciation.downloaded_file()
        if self.audio:
            self.audio_found = True

        return

    def get_formatted_defs(self):
        def_str = ''
        for word in self.entries:
            def_str += word.get_formatted_str()

        if def_str:
            return def_str

        return "No definitions found"

    def print_definitions(self):
        for word in self.entries:
            print(word)

    def get_base_word(self):
        self._check_for_base_word
        if self.base_word:
            return self.base_word
        else:
            return self.word

    def is_empty(self):
        is_empty = True
        for word in self.entries:
            if word.__str__():
                is_empty = False
                break
        return is_empty

    def _get_entries(self):
        self.entries = []
        for word in self.wik:
           for defs in word['definitions']:
               self.entries.append(WikiDefinition(defs))

    def _check_for_base_word(self):
        possibilities = []
        for word in self.entries:
            for base_word in word.base_words:
                possibilities.append(base_word)

        if not possibilities:
            self.logger.info("*** No base words found! ***")
        elif len(possibilities) > 1 and not all(elem == possibilities[0] for elem in possibilities):
            self.logger.info("Multiple base words found!")
        else:
            self.base_word = possibilities[0]
            self.logger.info("*** Base word found: {} ***".format(self.base_word))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    word1 = VocabWord('сказал')
    word2 = VocabWord('рукава')
    word3 = VocabWord('измочил')
    word4 = VocabWord('выгораживать')
    print("Word {} is empty: {}".format(word1.word, word1.is_empty()))
    print("Word {} is empty: {}".format(word2.word, word2.is_empty()))
    print("Word {} is empty: {}".format(word3.word, word3.is_empty()))
    print("Word {} is empty: {}".format(word4.word, word4.is_empty()))
