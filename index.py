import random
import os.path
import logging
import help

logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger('main')

random.seed()
g_index = 0
LEVEL_SIZE = 10     # phrases on each level

class State:
    def __init__(self, session, user_session):
        self.lett = session.get('lett', None)
        self.level = int(session.get('level', '0'))
        self.pos = int(session.get('pos', '0'))      # position inside level
        self.used_phrases = session.get('used_phrases', None)
        self.last_utterance = session.get('last_utterance', None)
        # long-term state
        self.intro_said = user_session.get('intro_said', False)

    def to_output(self):
        return {'lett': self.lett, 'level': self.level, 'pos': self.pos, 'used_phrases': self.used_phrases, 'last_utterance': self.last_utterance}, {'intro_said': self.intro_said}

class Request:
    def __init__(self, req):
        self.utterance = req.get('original_utterance', None)     # user's utterance
        self.intents = req.get('nlu', {}).get('intents',{})

    def is_intent_repeat(self):
        return self.intents.get('YANDEX.REPEAT', None) is not None

    def is_intent_restart(self):
        return self.intents.get('restart', None) is not None

    def get_intent_letter(self):
        el = self.intents.get('exercise_letter', None)
        if not el:
            return None
        return el['slots']['letter']['value']

class AppException(Exception):
    def __init__(self, message):
        self.message = message


def next_level_intro(level):
    assert level > 1
    return 'теперь по %d слов%s. ' % (level, '' if level >= 5 else 'а')

def select_phrase(all_phrases, used_phrases):
    if len(used_phrases) >= len(all_phrases):
        return None
    for n in range(1,10):
        i = random.randint(0,len(all_phrases)-1)
        ph = all_phrases[i]
        if ph not in used_phrases:
            phrase = ph
            used_phrases.append(ph)
            return ph
    for ph in all_phrases:
        if ph not in used_phrases:
            phrase = ph
            used_phrases.append(ph)
            return ph
    raise AppException("не могу выбрать следующую фразу")

def read_level_phrases(state):
    lett_short = state.lett[5:]
    fname = 'phrase_%s_%d.txt' % (lett_short, state.level)
    if not os.path.isfile(fname):
        return None
    try:
        f = open(fname)
    except:
        raise AppException('не могу открыть список фраз. файл ' + fname)
    return f.read().splitlines()


# pos starts from 1
def get_next_phrase(state):
    global LEVEL_SIZE       # each level span on [1, LEVEL_SIZE]
    appender = ''
    state.pos += 1
    level_phrases = read_level_phrases(state)
    if (not level_phrases):
        on_start(state)
        return "я пока не готова учить этой букве. попробуйте другую." if state.level == 1 else "слова кончинись. попробуйте другую букву."
    if state.pos > len(level_phrases) or state.pos > LEVEL_SIZE:
        # level up
        if state.level >= 4:
            on_start(state)
            return "мы закончили с этой буквой. можно начать с начала."
        state.level += 1
        state.pos = 1
        state.used_phrases = []
        appender = next_level_intro(state.level)
        level_phrases = read_level_phrases(state)
    ph = select_phrase(level_phrases, state.used_phrases)
    return appender + ph


def on_start(state):     # go to s_empty
    state.lett = None
    state.level = 0
    state.pos = 0
    state.used_phrases = []
    text = 'Выберете букву'
    if not state.intro_said:
        state.intro_said = True
        text = help.get_introduction() + ' ' + text
    return text

def on_empty(req, state):     # go to s_letter / s_empty
    assert not state.lett
    assert state.level == 0
    lett = req.get_intent_letter()
    if lett:
        state.lett = lett
        state.level = 1
        ph = get_next_phrase(state)
        text = 'повторяйте за мной. ' + ph
    else:
        text = 'Выберете букву. Сэ, жэ, эр.'
    return text

def on_letter(req, state):
    assert state.level > 0
    assert state.lett
    return get_next_phrase(state)      # used_phrases modified


def handler(event, context):
    """
    Entry-point for Serverless Function.
    :param event: request payload.
    :param context: information about current execution context.
    :return: response to be serialized as JSON.
    """
    orig_utt = event['request'].get('original_utterance', None)
    state = State(event['state']['session'], event['state']['user'])
    req = Request(event['request'])

    logger.debug("Input state %s", state)

    try:
        if not req.utterance or req.is_intent_restart():
            text = on_start(state)
        elif req.is_intent_repeat():
            text = state.last_utterance
        elif not state.lett:
            text = on_empty(req, state)
        else:
            text = on_letter(req, state)
    except AppException as e:
        on_start(state)     # reset state
        text = 'Ой, у меня ошибка! ' + e.message

    state_ret, user_state_ret = state.to_output()
    state_ret['last_utterance'] = text      # remember last utterance to be able to repeat

    return {
        'version': event['version'],
        'session': event['session'],
        'response': {
            'text': text,
            # Don't finish the session after this response.
            'end_session': 'false'
        },
        "session_state": state_ret,
        "user_state_update": user_state_ret
    }
