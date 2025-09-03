from kits.kit_common.utils import normalize_text
from kits.kit_common.highlight import make_snippet


def test_normalize_text_basic():
    s = "  A\n\nB \t C  "
    assert normalize_text(s) == "A B C"


def test_make_snippet_with_match():
    text = "Это тестовый документ о возвратах и доставке."
    snippet, hl = make_snippet(text, "возвратах", window=5)
    assert "возвратах" in snippet
    assert hl and hl[0][1] - hl[0][0] == len("возвратах")


def test_make_snippet_no_match():
    text = "Документ без совпадений."
    snippet, hl = make_snippet(text, "ничего")
    assert snippet
    assert hl == []

