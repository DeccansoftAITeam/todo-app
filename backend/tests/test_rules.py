from datetime import date
from pathlib import Path

import pytest

from app import rules


def test_title_trimmed():
    assert rules.normalize_title("  Buy milk  ") == "Buy milk"


@pytest.mark.parametrize("bad", ["", "   ", "x" * 201, "  " + "x" * 201 + "  "])
def test_title_rejected(bad):
    with pytest.raises(ValueError):
        rules.normalize_title(bad)


def test_title_length_limits_ok():
    assert rules.normalize_title("a") == "a"
    assert len(rules.normalize_title("x" * 200)) == 200


@pytest.mark.parametrize(
    "due,completed,expected",
    [
        ("2026-11-08", False, True),
        ("2026-11-09", False, False),
        ("2026-11-08", True, False),
        ("2026-11-10", False, False),
        (None, False, False),
    ],
)
def test_is_overdue(due, completed, expected):
    assert rules.is_overdue(due, completed, date(2026, 11, 9)) is expected


def test_rules_has_no_clock():
    src = Path(rules.__file__).read_text(encoding="utf-8")
    assert "datetime.now" not in src
    assert "date.today" not in src


@pytest.mark.parametrize(
    "title,q,expected",
    [
        ("Buy Milk", "milk", True),
        ("Buy Milk", "MILK", True),
        ("Straße", "STRASSE", True),
        ("Buy Milk", "eggs", False),
        ("Buy Milk", "", True),
        ("Buy Milk", None, True),
    ],
)
def test_matches_query(title, q, expected):
    assert rules.matches_query(title, q) is expected
