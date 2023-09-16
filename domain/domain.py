from enum import Enum
import random

from adapter import resource_adapter


DEFAULT_PHRASES_PER_LEVEL = 10

random.seed()


class Letter(Enum):
    LETT_L = 1
    LETT_S = 2
    LETT_R = 3
    LETT_SH = 4
    LETT_ZH = 5

    def short_name(self):
        return self.name[5:].lower()


# return Letter instance or raise KeyError
def letter_by_string(lett):
    try:
        return Letter[lett.upper()]
    except KeyError:
        return None


class Level:
    def __init__(self, number, description, phrases, max_phrases):
        assert number > 0
        assert max_phrases > 0
        self.number = number        # not required?
        self.description = description       # short description. Announce on level start. E g "слова с мягким звуком эр"
        self.phrases = phrases              # level will give phrases from this collection
        self.max_phrases = max_phrases      # level completes on this number of phrases


LEVEL_NONE = Level(1, None, None, 1)
LEVEL_BEYOND_END = Level(1, None, None, 1)


class LevelInstance:
    def __init__(self, level, used_phrases):
        assert len(level.phrases) > 0
        assert len(level.phrases) >= len(used_phrases)
        self.level = level
        self.used_phrases = used_phrases    # phrases already given to user

    def is_complete(self):
        return len(self.used_phrases) >= min(self.level.max_phrases, len(self.level.phrases))

    # next phrase. None - if level complete.
    def next_phrase(self):
        if self.is_complete():
            return None
        is_first = not self.used_phrases

        for n in range(1, 100):      # try to find phrase randomly
            i = random.randint(0, len(self.level.phrases) - 1)
            ph = self.level.phrases[i]
            if ph not in self.used_phrases:
                self.used_phrases.append(ph)
                if is_first:
                    return self.level.description + ". " + ph
                else:
                    return ph
        raise Exception("не могу выбрать следующую фразу")


# Hold current level
# defines sequence of levels, from most simple to more difficult
class Path:
    def __init__(self, level):
        self.level =level

    @staticmethod
    def next():
        pass


class Session:
    def __init__(self, letter, level, used_phrases):
        self.letter =  letter     # Letter
        self.level = level


# loads level from resources
class LevelFactory:
    def __init__(self):
        self.res_adapter = resource_adapter.ArchiveResourceAdapter()    # adapter.ResourceAdapter

    def create(self, letter, level_number):
        lett_short_name = letter.short_name()
        resource_meta = "challenge/sound/%s/meta.json" % lett_short_name
        meta = self.res_adapter.read_json(resource_meta)
        if meta is None:
            global LEVEL_NONE
            return LEVEL_NONE
        levels = meta['levels']

        if level_number <= levels:
            resource = "challenge/sound/%s/phrase_%s_%d.txt" % (lett_short_name, lett_short_name, level_number)
        else:
            resource = "challenge/common/%d.txt" % (level_number - levels)

        lines = self.res_adapter.read(resource)
        if lines is None:
            global LEVEL_BEYOND_END
            return LEVEL_BEYOND_END
        assert len(lines) > 2
        max_challenges = int(lines[0])
        descr = lines[1]
        challenges = lines[2:]
        return Level(level_number, descr, challenges, max_challenges)


class LevelInstanceFactory:
    def __init__(self):
        pass

    def create(self, level, used_phrases):
        return LevelInstance(level, used_phrases)

