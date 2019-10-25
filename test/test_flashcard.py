from flashcard import Flashcard


def test_flashcard():
    card = Flashcard('идти')
    assert card.get_def(0) == 'to go'
    assert card.get_def(1) == 'to walk'
    assert card.get_def(2) == '(of precipitation) to fall'
    assert card.get_def(3) == 'to function, to work'
    assert card.get_def(4) == 'to suit, to become (of wearing clothes)'
    assert card.get_def(5) == '(used in expressions)'


def test_selfparse():
    card = Flashcard('идти:verb:to go:to walk:(of precipitation) to fall:to function, to work:to suit, to become (of '
                     'wearing clothes):(used in expressions)', opts=['self_parse'])

    assert card.get_def(0) == 'to go'
    assert card.get_def(1) == 'to walk'
    assert card.get_def(2) == '(of precipitation) to fall'
    assert card.get_def(3) == 'to function, to work'
    assert card.get_def(4) == 'to suit, to become (of wearing clothes)'
    assert card.get_def(5) == '(used in expressions)'
