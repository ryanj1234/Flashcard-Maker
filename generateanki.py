import sys
import logging
import builddeck
from flashcard import Flashcard
from russianwiktionaryparser.russianwiktionaryparser import WiktionaryParser
from pyforvo import ForvoParser

logging.basicConfig(level=logging.INFO, format='%(message)s')


def get_user_selection(num_choices):
    user_selection = 0
    while not 0 < user_selection <= num_choices:
        entered_value = input(f'Enter a number between 1 and {num_choices}: ')
        if entered_value.isnumeric():
            user_selection = int(entered_value)
    return user_selection


if __name__ == '__main__':
    not_found = []
    no_audio = []
    if len(sys.argv) < 2:
        print("Error: Must provide an input file")
        sys.exit(-1)
    INPUT_FILE = sys.argv[1]
    logging.info("Parsing input file {}".format(INPUT_FILE))
    deck = builddeck.RussianVocabDeck()

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        word = f.readline().rstrip().lower()

        while word:
            if not word.startswith('#'):
                logging.info(f"Parsing word {word}")
                card = Flashcard(word, WiktionaryParser(), ForvoParser())

                if len(card.entries) > 1:
                    print(card)
                    choice = get_user_selection(len(card.entries))
                    card.select_entry(choice-1)

                if card.entries:
                    deck.add_flashcard(card)
                    print(card.front)
                    print(card.back)
                    if card.audio_file is None:
                        no_audio.append(word)
                    print(f"Audio: {card.audio_file}")
                else:
                    print("Word not found!")
                    not_found.append(word)

            word = f.readline().rstrip().lower()

    deck.export()

    if not_found:
        print("No definition found for the following words:")
        for w in not_found:
            print("\t" + w)
    else:
        print("Definitions found for all words!")
