"""Pure business rules. No clock, no DB, no I/O."""

from datetime import date

TITLE_MAX_LENGTH = 200


def normalize_title(title: str) -> str:
    """Trim a title and enforce 1-200 characters (R2)."""
    trimmed = title.strip()
    if not trimmed:
        raise ValueError("title must not be blank")
    if len(trimmed) > TITLE_MAX_LENGTH:
        raise ValueError(f"title must be at most {TITLE_MAX_LENGTH} characters")
    return trimmed


def is_overdue(due_date: str | None, completed: bool, today: date) -> bool:
    """R6: due strictly before today and not completed."""
    if due_date is None or completed:
        return False
    return date.fromisoformat(due_date) < today


def matches_query(title: str, q: str | None) -> bool:
    """Case-insensitive substring match on the title."""
    if not q:
        return True
    return q.casefold() in title.casefold()
