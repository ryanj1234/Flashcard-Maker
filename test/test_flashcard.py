from flashcard import Flashcard


def test_flashcard():
    card = Flashcard('идти')
    assert card.get_def(0) == 'to go'
    assert card.get_def(1) == 'to walk'
    assert card.get_def(2) == '(of precipitation) to fall'
    assert card.get_def(3) == 'to function, to work'
    assert card.get_def(4) == 'to suit, to become (of wearing clothes)'
    assert card.get_def(5) == '(used in expressions)'
