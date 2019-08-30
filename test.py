#!/usr/bin/env python3

import unittest
import pytest
from wordparser import VocabWord

class TestWiki(unittest.TestCase):
    def test_wik(self):
        w = VocabWord('сказать')
        self.assertEquals(w.word, 'сказать')
