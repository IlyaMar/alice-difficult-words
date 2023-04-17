import os


def __read_file(name):
    fname = 'resources/' + name
    if not os.path.isfile(fname):
        raise AppException('не найден файл ' + fname)
    try:
        f = open(fname)
    except:
        raise AppException('не могу открыть файл ' + fname)
    return f.read()


def get_introduction():
    return __read_file('introduction.txt')


def get_help(state_description):
    return __read_file('help.txt') % state_description
