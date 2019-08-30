#!/usr/bin/env python3

import sys
import os
from wordparser import VocabWord

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide a list of words in input")
        sys.exit(1)

    if(os.path.isfile(sys.argv[1])):
        f = open(sys.argv[1], 'r')
        word = f.readline().rstrip().lower()
        while word:
            print("*** {} ***".format(word))
            w = VocabWord(word, def_only=True)
            w.print_definitions()
            word = f.readline().rstrip().lower()

    else:
        for word in sys.argv[1:]:
            print("*** {} ***".format(word))
            w = VocabWord(word, def_only=True)
            w.print_definitions()
