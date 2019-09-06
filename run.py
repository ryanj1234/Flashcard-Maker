#!/usr/bin/env python3
import os
import re
import logging
from wiktionaryparser import WiktionaryParser
import wget
import urllib.parse
import unicodedata
from build_deck import RussianVocabDeck

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

    return fname


def get_audio_file(url):
    stat = os.system('wget ' + url)
    if stat != 0:
        logging.error('Error downloading audio file!')
        return ''

    fname_ogg = get_name_from_url(url)
    fname_mp3 = fname_ogg.replace('.ogg', '.mp3')

    # convert to mp3
    stat = os.system('ffmpeg -i ' + fname_ogg + ' ' + fname_mp3 + ' > /dev/null 2>&1')

    if stat != 0:
        logging.error("Error converting file to mp3!")
        return ''

    # remove ogg file
    stat = os.system('rm ' + fname_ogg)

    if stat != 0:
        logging.error("Error removing ogg file!")
        return ''

    return fname_mp3


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


def get_defs(word):
    defs = ''
    for sub_word in word:
        definitions = get_definitions(sub_word)

        for line in definitions:
            defs += line

    return defs


def get_definitions(word):
    def_str = []

    if not 'definitions' in word:
        print("Definitions not in word!!!")
        print(word)
        return def_str

    def_num = 1
    for defs in word['definitions']:

        if 'partOfSpeech' in defs:
            part_of_speech = defs['partOfSpeech']
            def_str.append("<b>" + part_of_speech + "</b><br>")
        else:
            part_of_speech = ''

        #def_str.append("Definition {}: {}".format(def_num, part_of_speech))

        for i, line in enumerate(defs.get('text')):
            if i == 0:
                def_str.append(line)
                def_str.append("<ol>")
            else:
                def_str.append("<li>" + line + "</li>")
        def_str.append("</ol>")

        def_num += 1

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


class VocabWord(object):
    parser = WiktionaryParser()

    def __init__(self, word):
        self.word = word
        self.wik = VocabWord.parser.fetch(word, 'russian')


if __name__ == '__main__':
    word = VocabWord('сказать')

'''
INPUT_FILE='words.txt'
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    deck = RussianVocabDeck()
    with open(INPUT_FILE, 'r') as f:
        word = f.readline().rstrip().lower()

        while word:
            print("Word: {}".format(word))
            wik, word = get_wiki(word)
            defs = get_defs(wik)
            audio = get_pronunciation(wik)
            print(word)
            print(defs)
            print(audio)
            deck.add_note(word, defs, audio)
            word = f.readline().rstrip().lower()

    deck.export()
    '''
