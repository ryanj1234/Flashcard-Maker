import sys
import logging
import builddeck
from flashcard import Flashcard

INPUT_FILE='max3.txt'
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
            card = Flashcard(word)

            if not card.word:
                not_found.append(word)
            else:
                deck.add_flashcard(card)

            word = f.readline().rstrip().lower()

    deck.export()

    if not_found:
        print("No definition found for the following words:")
        for w in not_found:
            print("\t" + w)
    else:
        print("Definitions found for all words!")

    # if no_pron:
    #     print("No audio found for the following words:")
    #     for w in no_pron:
    #         print("\t" + w)
    # else:
    #     print("Audio found for all words!")