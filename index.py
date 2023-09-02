import random
import logging
import help

from domain import domain

logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger('main')

random.seed()


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


# pos starts from 1
def get_next_phrase(state):
    level_factory = domain.LevelFactory()
    level = level_factory.create(state.lett, state.level)
    state.pos += 1
    if level == domain.LEVEL_NONE:
        on_start(state)
        return "я пока не готова учить этой букве. попробуйте другую."
    if level == domain.LEVEL_BEYOND_END:
        on_start(state)
        return "мы закончили с этой буквой. можно начать с начала."

    level_instance_factory = domain.LevelInstanceFactory()
    level_instance = level_instance_factory.create(level, state.used_phrases)
    challenge = level_instance.next_phrase()

    if challenge is None:
        # level up
        state.level += 1
        state.pos = 1
        state.used_phrases = []
        challenge = get_next_phrase(state)
    return challenge


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
        text = 'Выберете букву. Сэ, эр, эл, ч'
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
