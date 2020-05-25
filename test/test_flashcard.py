import logging
import os
import urllib
from unittest.mock import patch

from bs4 import BeautifulSoup
from flashcard import Flashcard
from russianwiktionaryparser import wiktionaryparser

dir_path = os.path.dirname(os.path.realpath(__file__))
data_dir = 'data'

logging.basicConfig(level=logging.DEBUG)


def get_filename_from_link(link):
    return urllib.parse.unquote(link.split('/')[-1]).replace('File:', '')


def build_soup_from_file(word):
    full_file_path = os.path.join(dir_path, data_dir, f"{word} - Wiktionary.html")
    return BeautifulSoup(open(full_file_path, 'r', encoding='utf-8'), features="lxml")


def build_soup_for_url(url):
    word = urllib.parse.unquote(url.split('/')[-1])
    if '#' in word:
        word = ''.join(word.split('#')[:-1])
    return build_soup_from_file(word)


def mock_audio_download(link, destination):
    file_name = get_filename_from_link(link)
    return os.path.join(destination, file_name)


def run_mock(word):
    wiki = wiktionaryparser.WiktionaryParser()
    with patch('russianwiktionaryparser.wiktionaryparser.make_soup') as mock_fetch, \
            patch('russianwiktionaryparser.wiktionaryparser.make_soup_from_url') as mock_url_fetch, \
            patch('russianwiktionaryparser.wiktionaryparser.WiktionaryParser.download_audio') as mock_audio:
        mock_fetch.side_effect = build_soup_from_file
        mock_url_fetch.side_effect = build_soup_for_url
        mock_audio.side_effect = mock_audio_download
        flashcard = Flashcard(word, wiki)
    return flashcard


def test_to_say():
    flashcard = run_mock('сказать')

    assert len(flashcard.definitions) == 1
    assert flashcard.definitions[0].text == 'to say, to tell'
    assert flashcard.audio_file == os.path.join('.media', 'Ru-сказать.ogg')


def test_said():
    flashcard = run_mock('сказал')

    assert len(flashcard.definitions) == 1
    assert flashcard.definitions[0].text == 'to say, to tell'
    assert flashcard.audio_file == os.path.join('.media', 'Ru-сказать.ogg')
