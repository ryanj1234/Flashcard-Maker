#!/usr/bin/env python3

import os
from pyforvo.api import Forvo

FORVO_API_KEY = os.getenv('FORVO_API_KEY')

f = Forvo(FORVO_API_KEY)
pron = f.pronounce('сказать', language='ru', file_name='test.mp3')

#for i, pronunciation in enumerate(pron):
#    print("Downloading pronunciation {}".format(i))
#    pronunciation.download('сказать' + str(i) + '.mp3')
