from flashcard import Flashcard
import os
import json
from unittest.mock import patch

data_dir = 'data'


def build_obj_from_file(fname, lang):
    data = ''
    with open(os.path.join(data_dir, fname + '_data.txt')) as json_file:
        data = json.load(json_file)
    return data


def test_flashcard():
    with patch('wiktionaryparser.WiktionaryParser.fetch') as mock_fetch:
        mock_fetch.side_effect = build_obj_from_file
        card = Flashcard('идти')

    assert card.num_defs == 6
    assert card.get_def(0) == 'to go'
    assert card.get_def(1) == 'to walk'
    assert card.get_def(2) == '(of precipitation) to fall'
    assert card.get_def(3) == 'to function, to work'
    assert card.get_def(4) == 'to suit, to become (of wearing clothes)'
    assert card.get_def(5) == '(used in expressions)'

    assert card.get_audio_file() == os.path.join('.media', 'Ru-идти.mp3')


def test_selfparse():
    card = Flashcard('идти:verb:to go:to walk:(of precipitation) to fall:to function, to work:to suit, to become (of '
                     'wearing clothes):(used in expressions)', opts=['self_parse'])

    assert card.num_defs == 6
    assert card.get_def(0) == 'to go'
    assert card.get_def(1) == 'to walk'
    assert card.get_def(2) == '(of precipitation) to fall'
    assert card.get_def(3) == 'to function, to work'
    assert card.get_def(4) == 'to suit, to become (of wearing clothes)'
    assert card.get_def(5) == '(used in expressions)'

    assert card.get_audio_file() == os.path.join('.media', 'Ru-идти.mp3')

