#!/usr/bin/env python3

import sys
import logging
import wordparser
import builddeck

INPUT_FILE='words.txt'
if __name__ == '__main__':
    not_found = []
    no_pron = []
    if len(sys.argv) > 1:
        INPUT_FILE = sys.argv[1]
    print("Parsing input file {}".format(INPUT_FILE))
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    deck = builddeck.RussianVocabDeck()
    with open(INPUT_FILE, 'r') as f:
        word = f.readline().rstrip().lower()

        while word:
            w = wordparser.VocabWord(word)
            if w.is_empty():
                not_found.append(w.word)
            else:
                deck.add_vocab_word(w)

            if not w.audio_found:
                no_pron.append(w.word)
            word = f.readline().rstrip().lower()

    deck.export()

    if not_found:
        print("No definition found for the following words:")
        for w in not_found:
            print("\t" + w)
    else:
        print("Definitions found for all words!")

    if no_pron:
        print("No audio found for the following words:")
        for w in no_pron:
            print("\t" + w)
    else:
        print("Audio found for all words!")
