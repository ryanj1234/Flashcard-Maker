#!/usr/bin/env python3

import os
import genanki
from wordparser import VocabWord
import logging

class RussianVocabDeck(object):
    def __init__(self, guid=205940011, name='Auto Generated Vocab'):
        self.logger = logging.getLogger(__name__)
        self.deck = genanki.Deck(
            guid,
            name)

        self.model = genanki.Model(
            1607392312,
            'Auto Vocab',
            fields=[
                {'name': 'Front'},
                {'name': 'Back'},
                {'name': 'Audio'},
            ],
            templates=[
            {
                'name': 'Card 1',
                'qfmt': 'Listen...<br>{{Audio}}',
                'afmt': '{{Front}}<hr id="answer">{{Back}}',
            },
            {
                'name': 'Card 2',
                'qfmt': '{{Back}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Front}}{{Audio}}',
            }]
        )

        self.media_files = []

    def add_note(self, front, back, audio_file=''):
        if audio_file:
            fname = os.path.split(audio_file)[-1]
            audio = '[sound:' + fname + ']'
            self.media_files.append(audio_file)
        else:
            audio = ''

        note = genanki.Note(model=self.model, fields=[front, back, audio])
        self.deck.add_note(note)

    def add_vocab_word(self, vocab_word):
        self.logger.debug("Adding word: {}".format(vocab_word.word))
        self.logger.debug("Adding defs: {}".format(vocab_word.get_formatted_defs()))
        self.logger.debug("Adding audio: {}".format(vocab_word.audio))
        self.add_note(vocab_word.word, vocab_word.get_formatted_defs(), vocab_word.audio)

    def export(self, out_file='output.apkg'):
        package = genanki.Package(self.deck)
        package.media_files = self.media_files
        package.write_to_file(out_file)


if __name__ == '__main__':
    deck = RussianVocabDeck()
    deck.add_note("говорить", "to speak", "")
    word = VocabWord('сказать')
    deck.add_vocab_word(word)
    deck.export()
