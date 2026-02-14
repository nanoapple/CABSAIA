import pytest
from processing.context_negators import (
    ContextNegatorDetector,
    get_severity,
)

@pytest.fixture()
def toy_lexicon():
    return {
        "communication_shutdown": ["shut up", "go away", "stop"],
        "contempt": ["stupid", "idiot"],
        "passive_aggression": ["sure, whatever you say"],
    }

def test_normalised_phrase_match(toy_lexicon):
    det = ContextNegatorDetector(toy_lexicon)
    m = det.detect("Could you SHUT UP??!!")
    assert "communication_shutdown" in m
    assert any("shut up" in s.lower() for s in m["communication_shutdown"])

def test_word_boundary(toy_lexicon):
    det = ContextNegatorDetector(toy_lexicon)
    m = det.detect("stupidity is not the same as stupid")
    assert "contempt" in m
    # should match "stupid" as a word, not trigger on partials only
    assert any(s.lower() == "stupid" for s in [x.lower() for x in m["contempt"]])

def test_multiword_boundary(toy_lexicon):
    det = ContextNegatorDetector(toy_lexicon)
    m = det.detect("sure...whatever you say.")
    assert "passive_aggression" in m

def test_dedupe(toy_lexicon):
    det = ContextNegatorDetector({"communication_shutdown": ["shut up", "Shut up!!", "shut   up"]})
    m = det.detect("shut up")
    assert len(m["communication_shutdown"]) == 1  # deduped

def test_severity():
    matches = {
        "communication_shutdown": ["shut up"],
        "contempt": ["stupid"],
    }
    sev = get_severity(matches)
    assert sev in {"moderate", "high", "critical"}