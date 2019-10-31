from wikitools import WikiParser, wiki_url_to_file
from wikitools import CommandLineWikiParser
from wikitools import strip_accents
from unittest.mock import patch
import json
import os

data_dir = 'data'


def build_obj_from_file(fname, _):
    with open(os.path.join(data_dir, fname + '_data.txt')) as json_file:
        data = json.load(json_file)
    return data


def test_single_word():
    with patch('wiktionaryparser.WiktionaryParser.fetch') as mock_fetch:
        mock_fetch.side_effect = build_obj_from_file
        wik = WikiParser('идти')

    w = wik.to_word(0)

    assert w.word == 'идти'
    assert w.part_of_speech == 'verb'
    assert w.num_defs == 6
    assert w.get_definition(0) == 'to go'
    assert w.get_definition(1) == 'to walk'
    assert w.get_definition(2) == '(of precipitation) to fall'
    assert w.get_definition(3) == 'to function, to work'
    assert w.get_definition(4) == 'to suit, to become (of wearing clothes)'
    assert w.get_definition(5) == '(used in expressions)'
    assert w.audio_url == '//upload.wikimedia.org/wikipedia/commons/e/e0/Ru-%D0%B8%D0%B4%D1%82%D0%B8.ogg'

    with patch('urllib.request.urlretrieve') as mock_retrieve, patch('pydub.AudioSegment') as mock_conv:
        w.get_audio()

    assert w.audio_file == os.path.join('.media', 'Ru-идти.mp3')


def test_multi_word():
    with patch('wiktionaryparser.WiktionaryParser.fetch') as mock_fetch:
        mock_fetch.side_effect = build_obj_from_file
        wik = WikiParser('ход')

    assert wik.num_words == 4
    w1 = wik.to_word(0)
    w2 = wik.to_word(1)
    w3 = wik.to_word(2)
    w4 = wik.to_word(3)

    assert w1.word == 'ход'
    assert w1.part_of_speech == 'noun'
    assert w1.num_defs == 8
    assert w1.get_definition(0) == 'motion, movement, travel, progress, locomotion, headway'
    assert w1.get_definition(1) == 'course, path, way, run'
    assert w1.get_definition(2) == 'speed, rate, gait, pace'
    assert w1.get_definition(3) == 'stroke (of a piston)'
    assert w1.get_definition(4) == 'functioning, working, process, action'
    assert w1.get_definition(5) == 'gear, thread, pitch'
    assert w1.get_definition(6) == 'shape, trend, dependence (of a curve)'
    assert w1.get_definition(7) == 'range (of a magnet)'
    assert w1.audio_url == '//upload.wikimedia.org/wikipedia/commons/8/80/Ru-%D1%85%D0%BE%D0%B4.ogg'

    assert w2.word == 'ход'
    assert w2.part_of_speech == 'noun'
    assert w2.num_defs == 2
    assert w2.get_definition(0) == 'entrance, entry'
    assert w2.get_definition(1) == 'passage'
    assert w2.audio_url == '//upload.wikimedia.org/wikipedia/commons/8/80/Ru-%D1%85%D0%BE%D0%B4.ogg'

    assert w3.word == 'ход'
    assert w3.part_of_speech == 'noun'
    assert w3.num_defs == 1
    assert w3.get_definition(0) == '(games) move, turn, lead'
    assert w3.audio_url == '//upload.wikimedia.org/wikipedia/commons/8/80/Ru-%D1%85%D0%BE%D0%B4.ogg'

    assert w4.word == 'ход'
    assert w4.part_of_speech == 'noun'
    assert w4.num_defs == 1
    assert w4.get_definition(0) == 'axle with wheels'
    assert w4.audio_url == '//upload.wikimedia.org/wikipedia/commons/8/80/Ru-%D1%85%D0%BE%D0%B4.ogg'


def test_multi_word_with_base():
    with patch('wiktionaryparser.WiktionaryParser.fetch') as mock_fetch:
        mock_fetch.side_effect = build_obj_from_file
        wik1 = WikiParser('пила')
        assert wik1.num_base_words == 1
        wik2 = wik1.to_base(0)

    w1 = wik1.to_word(0)
    w2 = wik2.to_word(0)

    assert w1.word == 'пила'
    assert w1.part_of_speech == 'noun'
    assert w1.num_defs == 1
    assert w1.get_definition(0) == 'saw'
    assert w1.audio_url == '//upload.wikimedia.org/wikipedia/commons/d/d3/Ru-%D0%BF%D0%B8%D0%BB%D0%B0.ogg'

    assert w2.word == 'пить'
    assert w2.num_defs == 1
    assert w2.get_definition(0) == 'to drink'
    assert w2.audio_url == '//upload.wikimedia.org/wikipedia/commons/9/96/Ru-%D0%BF%D0%B8%D1%82%D1%8C.ogg'


def test_no_audio():
    with patch('wiktionaryparser.WiktionaryParser.fetch') as mock_fetch:
        mock_fetch.side_effect = build_obj_from_file
        wik = WikiParser('колотить')

    w = wik.to_word(0)

    assert w.word == 'колотить'
    assert w.part_of_speech == 'verb'
    assert w.num_defs == 5
    assert w.get_definition(0) == 'to knock, to strike, to bang'
    assert w.get_definition(1) == 'to drum'
    assert w.get_definition(2) == 'to beat, to thrash'
    assert w.get_definition(3) == 'to break'
    assert w.get_definition(4) == '(impersonal) to shake, to make someone shudder'
    assert w.audio_url == ''


def test_passive_base():
    with patch('wiktionaryparser.WiktionaryParser.fetch') as mock_fetch:
        mock_fetch.side_effect = build_obj_from_file
        wik = WikiParser('пугаться')

    w1 = wik.to_word(0)

    assert w1.word == 'пугаться'
    assert w1.part_of_speech == 'verb'
    assert w1.num_defs == 2
    assert w1.get_definition(0) == 'to be frightened (of), to be startled (of), to take fright (at); to shy (at)'
    assert w1.get_definition(1) == 'passive of пугать (pugatʹ)'


def test_command_line_single():
    with patch('wiktionaryparser.WiktionaryParser.fetch') as mock_fetch:
        mock_fetch.side_effect = build_obj_from_file
        wik = CommandLineWikiParser('колотить')

    w = wik.to_word()
    assert w.word == 'колотить'

    with patch('wikitools.get_input') as mock_input:
        mock_input.side_effect = '0'
        w = wik.to_word(0)

    assert w.word == 'колотить'


def test_command_line_multi():
    with patch('wiktionaryparser.WiktionaryParser.fetch') as mock_fetch:
        mock_fetch.side_effect = build_obj_from_file
        wik = CommandLineWikiParser('пила')

        with patch('wikitools.get_input') as mock_input:
            mock_input.return_value = '1'
            w1 = wik.to_word()
            mock_input.return_value = '2'
            w2 = wik.to_word()

    assert w1.word == 'пила'
    assert w1.part_of_speech == 'noun'
    assert w1.num_defs == 1
    assert w1.get_definition(0) == 'saw'
    assert w1.audio_url == '//upload.wikimedia.org/wikipedia/commons/d/d3/Ru-%D0%BF%D0%B8%D0%BB%D0%B0.ogg'

    assert w2.word == 'пить'
    assert w2.num_defs == 1
    assert w2.get_definition(0) == 'to drink'
    assert w2.audio_url == '//upload.wikimedia.org/wikipedia/commons/9/96/Ru-%D0%BF%D0%B8%D1%82%D1%8C.ogg'


def test_command_base_within():
    with patch('wiktionaryparser.WiktionaryParser.fetch') as mock_fetch:
        mock_fetch.side_effect = build_obj_from_file
        wik = CommandLineWikiParser('пугаться')

        with patch('wikitools.get_input') as mock_input:
            mock_input.return_value = 'y'
            w1 = wik.to_word()
            mock_input.return_value = 'n'
            w2 = wik.to_word()

    assert w1.word == 'пугать'
    assert w2.word == 'пугаться'


def test_stripper():
    assert strip_accents('пожа́луй') == 'пожалуй'


def test_multi_verb():
    with patch('wiktionaryparser.WiktionaryParser.fetch') as mock_fetch:
        mock_fetch.side_effect = build_obj_from_file
        wik = WikiParser('зубрила')

    w1 = wik.to_word(0)
    assert w1.word == 'зубрила'
    assert w1.part_of_speech == 'noun'
    assert w1.num_defs == 1
    assert w1.get_definition(0) == '(colloquial, disapproving) swot, grind, grade-grubber'
    assert w1.audio_url == ''

    w2 = wik.to_word(1)
    assert w2.word == 'зубрила'
    assert w2.part_of_speech == 'verb'
    assert w2.num_defs == 1
    assert w2.get_definition(0) == 'feminine singular past indicative imperfective of зубрить (zubritʹ)'
    assert w2.audio_url == ''


def test_not_found():
    with patch('wiktionaryparser.WiktionaryParser.fetch') as mock_fetch:
        mock_fetch.side_effect = build_obj_from_file
        wik = WikiParser('измочить')

    assert wik.num_words == 0
    w = wik.to_word(0)
    assert w.word == ''


def test_not_found_commandline():
    with patch('wiktionaryparser.WiktionaryParser.fetch') as mock_fetch:
        mock_fetch.side_effect = build_obj_from_file
        wik = CommandLineWikiParser('измочить')

    assert wik.num_words == 0
    w = wik.to_word(0)
    assert w.word == ''


def test_audio_parse():
    assert wiki_url_to_file(
        '//upload.wikimedia.org/wikipedia/commons/9/96/Ru-%D0%BF%D0%B8%D1%82%D1%8C.ogg') == 'Ru-пить.ogg'
    assert wiki_url_to_file(
        '//upload.wikimedia.org/wikipedia/commons/d/d3/Ru-%D0%BF%D0%B8%D0%BB%D0%B0.ogg') == 'Ru-пила.ogg'
    assert wiki_url_to_file(
        '//upload.wikimedia.org/wikipedia/commons/8/80/Ru-%D1%85%D0%BE%D0%B4.ogg') == 'Ru-ход.ogg'
    assert wiki_url_to_file(
        '//upload.wikimedia.org/wikipedia/commons/e/e0/Ru-%D0%B8%D0%B4%D1%82%D0%B8.ogg') == 'Ru-идти.ogg'
