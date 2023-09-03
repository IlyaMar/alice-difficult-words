import index

# def test_get_phrase():
#     s = index.State()
#     index.get_next_phrase(s)

def test_read_level_phrases():
    event = {
        'version': 123,
        'session': 'sid1',
        'request': {
            'original_utterance': 'utt1',
            'nlu': {
                'intents': {
                    'exercise_letter': {
                        'slots': {
                            'letter': {
                                'value': 'l'
                            }
                        }
                    }
                }
            }
        },
        'state': {
            'session': {
                'lett': 'l',
                'level': '1',
                'pos': '1',
                'last_utterance': 'test_utt1',
                'used_phrases': [],
                'intro_said': True
            },
            'user': {

            }
        }
    }

    resp = index.handler(event, None)

    assert resp['text']
