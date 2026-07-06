"""Canonical Job schema per CLAUDE.md §6 — every adapter normalizes to this."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class Job:
    canonical_key: str
    source_id: str
    external_id: str
    title: str
    company: str
    location: Optional[str]
    remote: bool
    description: Optional[str]
    apply_url: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = None
    posted_at: Optional[datetime] = None
    raw: dict[str, Any] = field(default_factory=dict)
