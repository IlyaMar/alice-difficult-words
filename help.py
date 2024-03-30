import os

from domain import domain


def __read_file(name):
    fname = 'resources/%s' % name
    if not os.path.isfile(fname):
        raise AppException('не найден файл ' + fname)
    try:
        f = open(fname)
    except:
        raise AppException('не могу открыть файл ' + fname)
    return f.read()


def get_introduction():
    return __read_file('introduction.txt')


def get_help(letter):
    if letter:
        # letter in form "lett_s"
        let = domain.Letter[letter.upper()]
        return __read_file('help_letter.txt') % let.get_transcription()
    else:
        return __read_file('help_start.txt')


