import sys
from PyQt5.QtWidgets import QApplication
from flashcard import Flashcard
from russianwiktionaryparser import WiktionaryParser
from main import WordChoice


if __name__ == '__main__':
    app = QApplication(sys.argv)
    card = Flashcard('здорово', WiktionaryParser())
    wc = WordChoice('здорово', card)
    wc.show()
    sys.exit(app.exec_())
