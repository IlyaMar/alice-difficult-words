import index

import json

# def test_get_phrase():
#     s = index.State()
#     index.get_next_phrase(s)


def read_data(name):
    fname = 'test_data/%s.json' % name
    f = open(fname)
    return json.load(f)


def test_dialog_0():
    req = read_data("step0_begin/req")
    resp = read_data("step0_begin/resp")
    resp1 = index.handler(req, None)
    assert resp == resp1


def test_dialog_1():
    req = read_data("step1_select_letter/req")
    resp = index.handler(req, None)
    assert resp["response"]["text"].startswith("Повторяйте за мной. сначала по одному слову. ")
    ss = resp["session_state"]
    assert ss["lett"] == "lett_l"
    assert ss["level"] == 1
    assert ss["pos"] == 1
    assert len(ss["used_phrases"]) == 1

