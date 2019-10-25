from parsers import SelfParse


def test_simple_selfparse():
    p = SelfParse('идти:to go')

    w = p.to_word(0)

    assert w.word == 'идти'
    assert w.part_of_speech == ''
    assert w.num_defs == 1
    assert w.get_definition(0) == 'to go'


def test_selfparse_part_of_speech():
    p = SelfParse('идти:verb:to go')

    w = p.to_word(0)

    assert w.word == 'идти'
    assert w.part_of_speech == 'verb'
    assert w.num_defs == 1
    assert w.get_definition(0) == 'to go'


def test_selfparse_multidef():
    p = SelfParse('идти:verb:to go:to walk:(of precipitation) to fall:to function, to work:to suit, to become (of '
                  'wearing clothes):(used in expressions)')

    w = p.to_word(0)

    assert w.word == 'идти'
    assert w.part_of_speech == 'verb'
    assert w.num_defs == 6
    assert w.get_definition(0) == 'to go'
    assert w.get_definition(1) == 'to walk'
    assert w.get_definition(2) == '(of precipitation) to fall'
    assert w.get_definition(3) == 'to function, to work'
    assert w.get_definition(4) == 'to suit, to become (of wearing clothes)'
    assert w.get_definition(5) == '(used in expressions)'
