import string

import bs4
import sys


if __name__ == '__main__':
    # file_name = sys.argv[1]
    file_name = 'Kindle_ Your Notes and Highlights.html'

    soup = bs4.BeautifulSoup(open(file_name, 'r', encoding='utf-8'), features='lxml')

    highlights = soup.find_all('span', {'id': 'highlight'})

    words = []
    for highlight in highlights:
        word = highlight.get_text().translate(str.maketrans('', '', string.punctuation))
        word = word.strip()
        words.append(word)

    for word in words:
        print(word)