import pytest
from flashcardmaker.wikitools import WikiParser
from flashcardmaker.wikitools import CommandLineWikiParser
from wiktionaryparser import WiktionaryParser
from unittest.mock import patch
import json
import os

def build_obj_from_file(fname, lang):
  data = ''
  with open(os.path.join('test', fname + '_data.txt')) as json_file:
    data = json.load(json_file)
  return data

def test_single_word():
  with patch('wiktionaryparser.WiktionaryParser.fetch') as mock_fetch:
    mock_fetch.side_effect = build_obj_from_file
    wik = WikiParser('идти') 
  
  w = wik.to_word(0)
  
  assert w.word == 'идти'
  assert w.definitions[0]['text'] == 'to go'
  assert w.definitions[1]['text'] == 'to walk'
  assert w.definitions[2]['text'] == '(of precipitation) to fall'
  assert w.definitions[3]['text'] == 'to function, to work'
  assert w.definitions[4]['text'] == 'to suit, to become (of wearing clothes)'
  assert w.definitions[5]['text'] == '(used in expressions)'
  assert w.audio_url == '//upload.wikimedia.org/wikipedia/commons/e/e0/Ru-%D0%B8%D0%B4%D1%82%D0%B8.ogg'
  
def test_multi_word_with_base():
  with patch('wiktionaryparser.WiktionaryParser.fetch') as mock_fetch:
    mock_fetch.side_effect = build_obj_from_file
    wik1 = WikiParser('пила')
    assert wik1.num_base_words == 1
    wik2 = wik1.to_base(0)

  w1 = wik1.to_word(0)
  w2 = wik2.to_word(0)
  
  assert w1.word == 'пила'
  assert w1.definitions[0]['text'] == 'saw'
  assert w1.audio_url == '//upload.wikimedia.org/wikipedia/commons/d/d3/Ru-%D0%BF%D0%B8%D0%BB%D0%B0.ogg'
  assert w2.word == 'пить'
  assert w2.definitions[0]['text'] == 'to drink'
  assert w2.audio_url == '//upload.wikimedia.org/wikipedia/commons/9/96/Ru-%D0%BF%D0%B8%D1%82%D1%8C.ogg'
  
def test_no_audio():
  with patch('wiktionaryparser.WiktionaryParser.fetch') as mock_fetch:
    mock_fetch.side_effect = build_obj_from_file
    wik = WikiParser('колотить')
  
  w = wik.to_word(0)
  
  assert w.definitions[0]['text'] == 'to knock, to strike, to bang'
  assert w.definitions[1]['text'] == 'to drum'
  assert w.definitions[2]['text'] == 'to beat, to thrash'
  assert w.definitions[3]['text'] == 'to break'
  assert w.definitions[4]['text'] == '(impersonal) to shake, to make someone shudder'
  assert w.audio_url == ''

def test_passive_base():
  with patch('wiktionaryparser.WiktionaryParser.fetch') as mock_fetch:
    mock_fetch.side_effect = build_obj_from_file
    wik = WikiParser('пугаться')
    
  w1 = wik.to_word(0)
  
  assert w1.definitions[0]['text'] == 'to be frightened (of), to be startled (of), to take fright (at); to shy (at)'
  
  
def test_command_line_single():
  with patch('wiktionaryparser.WiktionaryParser.fetch') as mock_fetch:
    mock_fetch.side_effect = build_obj_from_file
    wik = CommandLineWikiParser('колотить')
    
  w = wik.to_word()
  assert w.word == 'колотить'
  
  with patch('flashcardmaker.wikitools.CommandLineWikiParser.get_input') as mock_input:
    mock_input.side_effect = '0'
    w = wik.to_word(0)
    
  assert w.word == 'колотить'

  
def test_command_line_multi():
  with patch('wiktionaryparser.WiktionaryParser.fetch') as mock_fetch:
    mock_fetch.side_effect = build_obj_from_file
    wik = CommandLineWikiParser('пила')
  
  with patch('flashcardmaker.wikitools.CommandLineWikiParser.get_input') as mock_input:
    mock_input.return_value = '1'
    w1 = wik.to_word()
    mock_input.return_value = '2'
    w2 = wik.to_word()
    
  assert w1.word == 'пила'
  assert w2.word == 'пить'

def test_command_base_within():
  with patch('wiktionaryparser.WiktionaryParser.fetch') as mock_fetch:
    mock_fetch.side_effect = build_obj_from_file
    wik = CommandLineWikiParser('пугаться')
  
    with patch('flashcardmaker.wikitools.CommandLineWikiParser.get_yn') as mock_input:
      mock_input.return_value = 'y'
      w1 = wik.to_word()
      mock_input.return_value = 'n'
      w2 = wik.to_word()
    
  assert w1.word == 'пугать'
  assert w2.word == 'пугаться'
