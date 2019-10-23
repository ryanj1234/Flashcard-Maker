import sys
import os
from wiktionaryparser import WiktionaryParser
import json

outdir = 'test'

if len(sys.argv) < 2:
  print("Not enough args")
  sys.exit(0)

parser = WiktionaryParser()
word = sys.argv[1]
data = parser.fetch(word, 'russian')

if not data:
  print("Word {} not found".format(word))
  
with open(os.path.join(outdir, word + '_data.txt'), 'w') as outfile:
  json.dump(data, outfile)
    
print("Data saved")