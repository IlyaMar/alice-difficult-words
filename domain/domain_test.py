from domain import domain


def test_level_exist():
    l1 = domain.LevelFactory().create("l", 1)
    assert l1 != domain.LEVEL_NONE
    assert l1 != domain.LEVEL_BEYOND_END
    assert l1.phrases
    assert l1.description
    assert l1.max_phrases > 1


def test_level_not_exist():
    l1 = domain.LevelFactory().create("x", 1)
    assert l1 == domain.LEVEL_NONE


def test_level_beyond():
    l1 = domain.LevelFactory().create("l", 100)
    assert l1 == domain.LEVEL_BEYOND_END


def test_level_get_challenge():
    l1 = domain.LevelFactory().create("l", 1)
    li = domain.LevelInstanceFactory().create(l1, [])
    assert not li.used_phrases
    ch = li.next_phrase()
    assert ch
    assert li.used_phrases
