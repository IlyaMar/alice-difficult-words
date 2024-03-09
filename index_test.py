import index
import pytest
import json

# def test_get_phrase():
#     s = index.State()
#     index.get_next_phrase(s)


@pytest.fixture(autouse=True)
def run_before_and_after_tests(tmpdir):
    index.init("test_data/resources")


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
    req = read_data("step1_select_letter")
    resp = index.handler(req, None)
    assert resp["response"]["text"].lower().startswith("повторяйте за мной. сначала по одному слову. ")
    ss = resp["session_state"]
    assert ss["lett"] == "lett_l"
    assert ss["level"] == 1
    assert len(ss["used_phrases"]) == 1


def test_dialog_2():
    req = read_data("step2_reply_on_challenge1")
    resp = index.handler(req, None)
    assert resp["response"]["text"]
    ss = resp["session_state"]
    assert ss["lett"] == "lett_l"
    assert ss["level"] == 1
    assert len(ss["used_phrases"]) == 2


def test_dialog_3():
    req = read_data("stepN_reply_on_challenge_last_in_level")
    resp = index.handler(req, None)
    assert resp["response"]["text"]
    ss = resp["session_state"]
    assert ss["lett"] == "lett_l"
    assert ss["level"] == 2
    assert len(ss["used_phrases"]) == 1


def test_dialog_4():
    req = read_data("step_reply_on_challenge_last_in_level2")
    resp = index.handler(req, None)
    assert resp["response"]["text"].startswith("теперь скороговорки")
    ss = resp["session_state"]
    assert ss["lett"] == "lett_l"
    assert ss["level"] == 3
    assert len(ss["used_phrases"]) == 1


def test_dialog_5_complete_letter():
    req = read_data("step_reply_on_challenge_last_in_level3")
    resp = index.handler(req, None)
    assert resp["response"]["text"] == "мы закончили с этой буквой. можно начать с начала."
    ss = resp["session_state"]
    assert ss["lett"] is None
    assert ss["level"] == 0
    assert len(ss["used_phrases"]) == 0
