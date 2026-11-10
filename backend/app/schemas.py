"""Request/response models."""

import re
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, StrictBool, field_validator, model_validator

from app import rules

Category = Literal["work", "personal", "shopping", "other"]
Priority = Literal["low", "medium", "high"]

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class TodoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    due_date: str | None = None
    category: Category = "other"
    priority: Priority = "medium"

    @field_validator("title")
    @classmethod
    def _title(cls, v: str) -> str:
        return rules.normalize_title(v)

    @field_validator("due_date")
    @classmethod
    def _due_date(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not _DATE_RE.match(v):
            raise ValueError("due_date must be YYYY-MM-DD")
        date.fromisoformat(v)  # rejects impossible dates, e.g. 2026-02-30
        return v


class TodoPatch(BaseModel):
    # Any field other than completed/archived is rejected with 422.
    model_config = ConfigDict(extra="forbid")

    completed: StrictBool | None = None
    archived: StrictBool | None = None

    @model_validator(mode="after")
    def _non_empty(self) -> "TodoPatch":
        if self.completed is None and self.archived is None:
            raise ValueError("provide completed and/or archived")
        return self


class Todo(BaseModel):
    id: int
    title: str
    due_date: str | None
    category: Category
    priority: Priority
    completed: bool
    archived: bool
    created_at: str
