import os
import genanki
from flashcard import Flashcard
import logging


def to_html(defs, part_of_speech):
    html_str = "<b>{}</b>".format(part_of_speech)
    html_str += "<br /><ol>"
    for d in defs:
        html_str += "<li>{}</li>".format(d.text)

    html_str += "</ol>"
    return html_str


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

    def add_flashcard(self, card):
        self.logger.debug("Adding word: {}".format(card.word))
        self.logger.debug("Adding defs: {}".format(to_html(card.definitions, card.part_of_speech)))
        self.logger.debug("Adding audio: {}".format(card.audio_file))
        audio_file = '' if card.audio_file is None else card.audio_file
        self.add_note(card.word, to_html(card.definitions, card.part_of_speech), audio_file)

    def export(self, out_file='output.apkg'):
        package = genanki.Package(self.deck)
        package.media_files = self.media_files
        package.write_to_file(out_file)

