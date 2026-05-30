# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
PULSE Priority Calculator — deterministic computation of priority weights
and effective item scores from vault frontmatter.

Reads Maps/*.md and Notes/*.md, computes all formula components,
outputs structured JSON for the agent to interpret.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml


# ── Constants ──────────────────────────────────────────────────────────────

IMPORTANCE_WEIGHTS = {"high": 0.04, "medium": 0.02, "low": 0.01}
IMPORTANCE_MODIFIERS = {"high": 0.08, "medium": 0.04, "low": 0.00}
DEFAULT_IMPORTANCE = "medium"

URGENCY_CAP = 0.20
URGENCY_NOTE_DUE_MAX = 0.15
URGENCY_NOTE_WAITING_MAX = 0.05
URGENCY_MA_MAX = 0.15

RECENCY_MAX = 0.12
RECENCY_DECAY_DAYS = 7

TIMESCALE_THRESHOLDS = {
    "daily": 1, "weekly": 6, "monthly": 25,
    "quarterly": 75, "biannual": 150, "annual": 300,
}
TIMESCALE_DEFAULT = 6  # null timescale

EXTERNAL_INPUT_CADENCE = {
    # Default cadence (days) by generic batch name.
    # User-specific batches fall back to the nearest match or DEFAULT below.
    "Work": 7,
    "Maintenance": 14,
    "Projects": 21,
    "Leisure": 21,
}
EXTERNAL_INPUT_CADENCE_DEFAULT = 21  # fallback for any batch not listed above

BATCH_GATING_THRESHOLD = 0.40  # Phase 1
EFFORT_ITEM_CAP = 3  # Max high/medium items per effort in Important Items
IMPORTANT_ITEMS_CEILING = 20

WEEKDAY_MAP = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}


# ── Data Classes ───────────────────────────────────────────────────────────

@dataclass
class MinorAction:
    description: str
    status: str  # "open", "done", "waiting"
    importance: str
    due: date | None = None
    waiting_since: date | None = None
    depends_on: list[str] = field(default_factory=list)


@dataclass
class MapData:
    slug: str
    context_batch: str
    base_priority: int
    last_active: date | None
    last_external_input: date | None
    open_loops_declared: int
    related_efforts: list[str]
    purpose: str
    track_external_input: bool = True
    minor_actions: list[MinorAction] = field(default_factory=list)
    active_thread_summaries: dict[str, str] = field(default_factory=dict)
    filepath: str = ""


@dataclass
class NoteData:
    slug: str
    efforts: list[str]
    status: str
    importance: str
    due: date | None
    updated: date | None
    timescale: str | None
    subtype: str = "note"
    depends_on: list[str] = field(default_factory=list)
    filepath: str = ""

    @property
    def is_reference(self) -> bool:
        """Reference/theory Notes don't count as open loops."""
        return self.subtype == "reference"


@dataclass
class CalibrationData:
    correction_counts: dict[str, dict[str, int]] = field(default_factory=dict)
    patterns: list[str] = field(default_factory=list)


@dataclass
class UrgencySource:
    source: str  # "note_due", "note_waiting", "minor_action_due", "minor_action_soon"
    description: str
    due: str | None
    contribution: float


@dataclass
class OpenItems:
    active_notes: int = 0
    waiting_notes: int = 0
    active_minor_actions: int = 0
    waiting_minor_actions: int = 0


@dataclass
class ExternalInput:
    last_input: str | None
    cadence_days: int
    days_since: int | None
    stale: bool


@dataclass
class EffortResult:
    slug: str
    context_batch: str
    base_score: float
    recency_boost: float
    urgency_spike: float
    urgency_breakdown: list[UrgencySource]
    loop_factor: float
    loop_count: int
    calibration_offset: float
    priority_weight: float
    open_items: OpenItems
    external_input: ExternalInput
    stale_flag: bool
    days_since_active: int | None


@dataclass
class ScoreBreakdown:
    effort_weight: float
    importance_modifier: float
    due_proximity_boost: float
    status_modifier: float


@dataclass
class ItemScore:
    id: str
    type: str  # "note" or "minor_action"
    effort: str
    description: str
    importance: str
    status: str
    due: str | None
    depends_on: list[str]
    dependency_state: str  # "blocked", "unblocked", "no_deps"
    effective_score: float
    score_breakdown: ScoreBreakdown
    waiting_suppressed: bool


@dataclass
class WaitingItem:
    id: str
    effort: str
    description: str
    importance: str
    waiting_since: str | None
    days_waiting: int
    due: str | None
    effective_score: float
    gate_active: bool  # True = excluded from Important Items


@dataclass
class BatchResult:
    name: str
    combined_weight: float
    efforts: list[str]
    gated: bool
    has_due_within_7d: bool
    has_waiting_over_3d: bool


@dataclass
class ResurfacingCandidate:
    slug: str
    effort: str
    timescale: str | None
    threshold_days: int
    days_since_update: int


# ── Parsing ────────────────────────────────────────────────────────────────

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Split markdown on --- fences, return (yaml_dict, body)."""
    content = content.lstrip("\ufeff")  # strip BOM
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, parts[2]


def resolve_date(date_val: Any, ref: date) -> date | None:
    """Resolve a date value from frontmatter or inline metadata."""
    if date_val is None:
        return None
    if isinstance(date_val, date) and not isinstance(date_val, datetime):
        return date_val
    if isinstance(date_val, datetime):
        return date_val.date()

    s = str(date_val).strip().lower()
    if not s or s == "null" or s == "none":
        return None

    # YYYY-MM-DD
    try:
        return date.fromisoformat(s)
    except ValueError:
        pass

    # Informal dates
    if s in ("tonight", "today"):
        return ref
    if s == "tomorrow":
        return ref + timedelta(days=1)
    if s == "this weekend":
        days_until_sat = (5 - ref.weekday()) % 7
        if days_until_sat == 0 and ref.weekday() != 5:
            days_until_sat = 7
        return ref + timedelta(days=days_until_sat)

    # "next monday", "before friday"
    before_match = re.match(r"before\s+(\w+)", s)
    if before_match:
        day_name = before_match.group(1)
        if day_name in WEEKDAY_MAP:
            target = WEEKDAY_MAP[day_name]
            days_ahead = (target - ref.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            return ref + timedelta(days=days_ahead - 1)

    next_match = re.match(r"next\s+(\w+)", s)
    if next_match:
        day_name = next_match.group(1)
        if day_name in WEEKDAY_MAP:
            target = WEEKDAY_MAP[day_name]
            days_ahead = (target - ref.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            return ref + timedelta(days=days_ahead)

    return None  # unparseable


def parse_inline_metadata(text: str) -> dict[str, str]:
    """Extract key-value pairs from a parenthetical suffix like (importance: high, due: 2026-04-15).
    Finds the first parenthetical that contains 'importance:' since that's the metadata marker."""
    result = {}
    # Find all parenthetical groups, pick the one with key-value metadata
    all_parens = re.findall(r"\(([^)]+)\)", text)
    inner = None
    for candidate in all_parens:
        if re.search(r"\b(importance|due|waiting_since|depends)\s*::?\s*", candidate):
            inner = candidate
            break
    if inner is None:
        return result
    # Split on commas, then parse each segment
    for segment in inner.split(","):
        segment = segment.strip()
        # Handle "done YYYY-MM-DD" (no colon)
        done_match = re.match(r"done\s+(\d{4}-\d{2}-\d{2})", segment)
        if done_match:
            result["done"] = done_match.group(1)
            continue
        # Handle key:: value and key: value
        kv_match = re.match(r"([\w_]+)::?\s*(.+)", segment)
        if kv_match:
            key = kv_match.group(1).strip()
            val = kv_match.group(2).strip()
            result[key] = val
    return result


def strip_wikilinks(text: str) -> list[str]:
    """Extract slugs from [[slug]] patterns."""
    return re.findall(r"\[\[([^\]]+)\]\]", text)


def parse_active_threads(body: str) -> dict[str, str]:
    """Extract wikilink slugs and their summaries from ## Active Threads.
    Returns {slug: summary} where summary is the human-readable description
    from the Map entry (text between ' — ' and the trailing parenthetical).
    Only Notes listed here count as open loops for loop_factor."""
    threads: dict[str, str] = {}
    in_section = False
    for line in body.split("\n"):
        stripped = line.strip()
        if re.match(r"^##\s+Active Threads", stripped):
            in_section = True
            continue
        if in_section and re.match(r"^##\s+", stripped):
            break
        if not in_section:
            continue
        # Skip strikethrough (completed) lines
        if stripped.startswith("- ~~"):
            continue
        slugs = strip_wikilinks(stripped)
        if not slugs:
            continue
        slug = slugs[0]
        # Extract summary: text between ' — ' and trailing (subtype, date)
        summary = slug  # fallback
        dash_match = re.search(r"\]\]\s*—\s*(.+)", stripped)
        if dash_match:
            summary_text = dash_match.group(1).strip()
            # Strip trailing parenthetical like (plan, 2026-03-28)
            summary_text = re.sub(r"\s*\([^)]*\d{4}-\d{2}-\d{2}[^)]*\)\s*$", "", summary_text).strip()
            # Also strip trailing (subtype) without date
            summary_text = re.sub(r"\s*\((?:plan|note|log|reference|capture)\)\s*$", "", summary_text).strip()
            if summary_text:
                summary = summary_text
        threads[slug] = summary
    return threads


def parse_minor_actions(body: str, ref_date: date) -> list[MinorAction]:
    """Parse ## Minor Actions section from Map body text."""
    actions = []
    in_section = False
    for line in body.split("\n"):
        stripped = line.strip()
        if re.match(r"^##\s+Minor Actions", stripped):
            in_section = True
            continue
        if in_section and re.match(r"^##\s+", stripped):
            break
        if not in_section:
            continue

        cb_match = re.match(r"^-\s+\[([ xXwW])\]\s+(.+)$", stripped)
        if not cb_match:
            continue

        state = cb_match.group(1).lower()
        content = cb_match.group(2)

        if state == "x":
            continue  # done items don't contribute

        status = "waiting" if state == "w" else "open"
        meta = parse_inline_metadata(content)

        importance = meta.get("importance", DEFAULT_IMPORTANCE)
        due = resolve_date(meta.get("due"), ref_date)
        waiting_since = resolve_date(meta.get("waiting_since"), ref_date)

        depends_on = []
        depends_raw = meta.get("depends", "")
        if depends_raw:
            wikilinks = strip_wikilinks(depends_raw)
            depends_on = wikilinks if wikilinks else [depends_raw]

        desc_clean = re.sub(r"\s*\([^)]+\)\s*$", "", content).strip()

        actions.append(MinorAction(
            description=desc_clean,
            status=status,
            importance=importance,
            due=due,
            waiting_since=waiting_since,
            depends_on=depends_on,
        ))

    return actions


def load_maps(vault_path: Path, ref_date: date) -> tuple[list[MapData], list[dict]]:
    """Load user Maps from vault root (excludes INDEX.md and _system/ subdirectory)."""
    maps = []
    warnings = []
    maps_dir = vault_path / "Maps"

    for fp in sorted(maps_dir.glob("*.md")):  # top-level only — _system/ not included
        if fp.name == "INDEX.md":
            continue

        try:
            content = fp.read_text(encoding="utf-8")
        except Exception as e:
            warnings.append({"type": "read_error", "file": str(fp), "detail": str(e)})
            continue

        fm, body = parse_frontmatter(content)

        if fm.get("type") not in ("map",):
            continue

        slug = fm.get("effort", "")
        if not slug:
            warnings.append({"type": "missing_field", "file": str(fp), "detail": "effort slug missing"})
            continue

        base_priority = fm.get("base_priority")
        if base_priority is None:
            warnings.append({"type": "missing_field", "file": str(fp), "detail": "base_priority missing"})
            continue

        maps.append(MapData(
            slug=slug,
            context_batch=fm.get("context_batch", ""),
            base_priority=int(base_priority),
            last_active=resolve_date(fm.get("last_active"), ref_date),
            last_external_input=resolve_date(fm.get("last_external_input"), ref_date),
            open_loops_declared=fm.get("open_loops", 0),
            related_efforts=fm.get("related_efforts", []) or [],
            purpose=fm.get("purpose", ""),
            track_external_input=fm.get("track_external_input", True),
            minor_actions=parse_minor_actions(body, ref_date),
            active_thread_summaries=parse_active_threads(body),
            filepath=str(fp),
        ))

    return maps, warnings


def load_system_maps(vault_path: Path) -> list[dict]:
    """Load system Maps from Maps/_system/. Returns minimal dicts (not included in priority computation)."""
    system_maps = []
    system_dir = vault_path / "Maps" / "_system"
    if not system_dir.exists():
        return system_maps

    for fp in sorted(system_dir.glob("*.md")):
        try:
            content = fp.read_text(encoding="utf-8")
        except Exception:
            continue

        fm, _ = parse_frontmatter(content)
        if fm.get("type") != "system-map":
            continue

        system_maps.append({
            "slug": fm.get("effort", fp.stem.lower()),
            "type": "system-map",
            "context_batch": fm.get("context_batch", "System"),
            "priority_weight": fm.get("priority_weight", 0.0),
            "base_priority": fm.get("base_priority", 0),
            "last_active": fm.get("last_active", ""),
            "open_loops": fm.get("open_loops", 0),
            "purpose": fm.get("purpose", ""),
            "aliases": fm.get("aliases", []),
        })

    return system_maps


def load_notes(vault_path: Path, ref_date: date, include_archive: bool = False) -> tuple[list[NoteData], list[dict]]:
    """Load Notes from vault. Returns (notes, warnings)."""
    notes = []
    warnings = []
    notes_dir = vault_path / "Notes"

    for fp in sorted(notes_dir.glob("*.md")):
        if fp.name == "pulse-priority-calibration.md":
            continue

        try:
            content = fp.read_text(encoding="utf-8")
        except Exception as e:
            warnings.append({"type": "read_error", "file": str(fp), "detail": str(e)})
            continue

        fm, _ = parse_frontmatter(content)
        status = fm.get("status", "")
        if status not in ("active", "waiting"):
            continue

        # Normalize effort/efforts
        efforts = fm.get("efforts", [])
        if not efforts:
            effort_singular = fm.get("effort")
            if effort_singular:
                efforts = [effort_singular] if isinstance(effort_singular, str) else effort_singular
            else:
                efforts = []

        # Normalize depends/depends::
        depends_on = []
        for key in ("depends", "depends::"):
            dep_val = fm.get(key)
            if dep_val:
                if isinstance(dep_val, str):
                    wikilinks = strip_wikilinks(dep_val)
                    depends_on.extend(wikilinks if wikilinks else [dep_val])
                elif isinstance(dep_val, list):
                    for d in dep_val:
                        wikilinks = strip_wikilinks(str(d))
                        depends_on.extend(wikilinks if wikilinks else [str(d)])

        slug = fp.stem
        notes.append(NoteData(
            slug=slug,
            efforts=efforts if isinstance(efforts, list) else [efforts],
            status=status,
            importance=fm.get("importance", DEFAULT_IMPORTANCE),
            due=resolve_date(fm.get("due"), ref_date),
            updated=resolve_date(fm.get("updated"), ref_date),
            timescale=fm.get("timescale"),
            subtype=fm.get("subtype", "note"),
            depends_on=depends_on,
            filepath=str(fp),
        ))

    # Also load archive notes for dependency resolution only
    if include_archive:
        archive_dir = notes_dir / "archive"
        if archive_dir.exists():
            for fp in sorted(archive_dir.glob("*.md")):
                try:
                    content = fp.read_text(encoding="utf-8")
                except Exception:
                    continue
                fm, _ = parse_frontmatter(content)
                slug = fp.stem
                notes.append(NoteData(
                    slug=slug,
                    efforts=fm.get("efforts", []) or [],
                    status=fm.get("status", "done"),
                    importance=fm.get("importance", DEFAULT_IMPORTANCE),
                    due=None,
                    updated=resolve_date(fm.get("updated"), ref_date),
                    timescale=None,
                    depends_on=[],
                    filepath=str(fp),
                ))

    return notes, warnings


def load_calibration(vault_path: Path) -> CalibrationData:
    """Parse pulse-priority-calibration.md for correction tallies."""
    cal_path = vault_path / "Notes" / "pulse-priority-calibration.md"
    if not cal_path.exists():
        return CalibrationData()

    try:
        content = cal_path.read_text(encoding="utf-8")
    except Exception:
        return CalibrationData()

    correction_counts: dict[str, dict[str, int]] = {}
    patterns: list[str] = []

    # Parse Corrections section — look for "Mis-ranked" and "Expected" lines
    in_corrections = False
    in_patterns = False
    current_effort = ""

    for line in content.split("\n"):
        if line.startswith("## Corrections"):
            in_corrections = True
            in_patterns = False
            continue
        if line.startswith("## Patterns"):
            in_corrections = False
            in_patterns = True
            continue
        if line.startswith("## ") and line.startswith("## Corrections") is False:
            if not line.startswith("## Patterns"):
                in_corrections = False
                in_patterns = False
            continue

        if in_corrections:
            # Look for "Mis-ranked": effort at position N
            mis_match = re.search(r"\*\*Mis-ranked\*\*:\s*(\S+)", line)
            if mis_match:
                current_effort = mis_match.group(1).lower().rstrip(",")
                continue

            # Look for "Expected": should be higher/lower
            exp_match = re.search(r"\*\*Expected\*\*:.*\b(higher|lower|above|below)\b", line, re.IGNORECASE)
            if exp_match and current_effort:
                direction_word = exp_match.group(1).lower()
                direction = "higher" if direction_word in ("higher", "above") else "lower"
                if current_effort not in correction_counts:
                    correction_counts[current_effort] = {"higher": 0, "lower": 0}
                correction_counts[current_effort][direction] += 1
                current_effort = ""

        if in_patterns:
            pattern_match = re.match(r"^###\s+(.+)", line)
            if pattern_match:
                patterns.append(pattern_match.group(1).strip())

    return CalibrationData(correction_counts=correction_counts, patterns=patterns)


# ── Computation ────────────────────────────────────────────────────────────

def compute_recency_boost(last_active: date | None, today: date) -> float:
    """Linear decay from 0.12 at day 0 to 0.0 at day 7+."""
    if last_active is None:
        return 0.0
    days_since = (today - last_active).days
    if days_since < 0:
        days_since = 0  # future date clamp
    return max(0.0, RECENCY_MAX * (1 - days_since / RECENCY_DECAY_DAYS))


def compute_urgency_spike(
    effort_notes: list[NoteData],
    effort_mas: list[MinorAction],
    today: date,
    note_summaries: dict[str, str] | None = None,
) -> tuple[float, list[UrgencySource]]:
    """Compute urgency_spike with all sub-component caps. Returns (spike, breakdown)."""
    breakdown: list[UrgencySource] = []

    # Notes with due within 7d (capped at +0.15)
    note_due_total = 0.0
    for n in effort_notes:
        if n.is_reference:
            continue
        if n.due is None:
            continue
        days_until = (n.due - today).days
        # Waiting exception: skip unless within 1d or overdue
        if n.status == "waiting" and days_until > 1:
            continue
        if days_until <= 7:
            contrib = min(0.05, URGENCY_NOTE_DUE_MAX - note_due_total)
            if contrib > 0:
                note_due_total += contrib
                breakdown.append(UrgencySource(
                    source="note_due",
                    description=(note_summaries or {}).get(n.slug, n.slug),
                    due=n.due.isoformat(),
                    contribution=contrib,
                ))

    # Notes waiting >3d with no due date (capped at +0.05)
    note_waiting_total = 0.0
    for n in effort_notes:
        if n.is_reference:
            continue
        if n.status != "waiting":
            continue
        if n.due is not None:
            continue  # has due date — handled above
        if n.updated is None:
            continue
        days_waiting = (today - n.updated).days
        if days_waiting > 3:
            contrib = min(0.02, URGENCY_NOTE_WAITING_MAX - note_waiting_total)
            if contrib > 0:
                note_waiting_total += contrib
                breakdown.append(UrgencySource(
                    source="note_waiting",
                    description=(note_summaries or {}).get(n.slug, n.slug),
                    due=None,
                    contribution=contrib,
                ))

    # Minor Actions with due dates
    ma_total = 0.0
    for ma in effort_mas:
        if ma.due is None:
            continue
        # Waiting MAs with due >1d out: skip (same exception as notes)
        if ma.status == "waiting":
            days_until = (ma.due - today).days
            if days_until > 1:
                continue
        days_until = (ma.due - today).days
        if days_until <= 0:
            # Overdue or same-day
            contrib = min(0.05, URGENCY_MA_MAX - ma_total)
        elif days_until <= 2:
            contrib = min(0.03, URGENCY_MA_MAX - ma_total)
        else:
            continue
        if contrib > 0:
            ma_total += contrib
            breakdown.append(UrgencySource(
                source="minor_action_due" if days_until <= 0 else "minor_action_soon",
                description=ma.description,
                due=ma.due.isoformat(),
                contribution=contrib,
            ))

    total = min(note_due_total + note_waiting_total + ma_total, URGENCY_CAP)
    return total, breakdown


def compute_loop_factor(
    effort_notes: list[NoteData],
    effort_mas: list[MinorAction],
) -> tuple[float, int, OpenItems]:
    """Importance-weighted open item load. Returns (factor, count, open_items_breakdown).
    Excludes reference-subtype Notes (theory/docs — not open loops)."""
    total = 0.0
    count = 0
    items = OpenItems()

    for n in effort_notes:
        if n.is_reference:
            continue
        weight = IMPORTANCE_WEIGHTS.get(n.importance, IMPORTANCE_WEIGHTS[DEFAULT_IMPORTANCE])
        total += weight
        count += 1
        if n.status == "active":
            items.active_notes += 1
        elif n.status == "waiting":
            items.waiting_notes += 1

    for ma in effort_mas:
        weight = IMPORTANCE_WEIGHTS.get(ma.importance, IMPORTANCE_WEIGHTS[DEFAULT_IMPORTANCE])
        total += weight
        count += 1
        if ma.status == "open":
            items.active_minor_actions += 1
        elif ma.status == "waiting":
            items.waiting_minor_actions += 1

    return total, count, items


def resolve_dependencies(
    notes: list[NoteData],
    all_notes: list[NoteData],
) -> dict[str, dict]:
    """Resolve dependency states for notes with depends fields.
    Returns {slug: {"state": "blocked"|"unblocked"|"no_deps", "blocking": [...]}}.
    """
    # Build status lookup for all notes (including archived)
    status_by_slug: dict[str, str] = {}
    for n in all_notes:
        status_by_slug[n.slug] = n.status

    results = {}
    for n in notes:
        if not n.depends_on:
            results[n.slug] = {"state": "no_deps", "blocking": []}
            continue

        blocking = []
        for dep_slug in n.depends_on:
            dep_status = status_by_slug.get(dep_slug)
            if dep_status in ("done", "archived"):
                continue  # resolved
            blocking.append(dep_slug)

        if blocking:
            results[n.slug] = {"state": "blocked", "blocking": blocking}
        else:
            results[n.slug] = {"state": "unblocked", "blocking": []}

    return results


def compute_effort_weights(
    maps: list[MapData],
    notes: list[NoteData],
    calibration: CalibrationData,
    calibration_offsets: dict[str, float],
    today: date,
) -> list[EffortResult]:
    """Compute priority_weight for each effort."""
    # Group notes by effort.
    # For loop_factor: only count Notes listed under ## Active Threads in the Map.
    # For urgency_spike: all Notes that reference the effort contribute.
    # Build active thread sets per Map for filtering.
    active_threads_by_effort: dict[str, set[str]] = {}
    summaries_by_effort: dict[str, dict[str, str]] = {}
    for m in maps:
        active_threads_by_effort[m.slug] = set(m.active_thread_summaries.keys())
        summaries_by_effort[m.slug] = m.active_thread_summaries

    notes_by_effort_loops: dict[str, list[NoteData]] = {}
    notes_by_effort_all: dict[str, list[NoteData]] = {}
    for n in notes:
        for eff in n.efforts:
            notes_by_effort_all.setdefault(eff, []).append(n)
            # Only count toward loops if this Note is in the Map's Active Threads
            if n.slug in active_threads_by_effort.get(eff, set()):
                notes_by_effort_loops.setdefault(eff, []).append(n)

    results = []
    for m in maps:
        effort_notes_all = notes_by_effort_all.get(m.slug, [])
        effort_notes_loops = notes_by_effort_loops.get(m.slug, [])
        effort_mas = m.minor_actions  # already filtered to open/waiting

        base_score = m.base_priority / 10.0
        recency = compute_recency_boost(m.last_active, today)
        urgency, urgency_breakdown = compute_urgency_spike(
            effort_notes_all, effort_mas, today, summaries_by_effort.get(m.slug)
        )
        loops, loop_count, open_items = compute_loop_factor(effort_notes_loops, effort_mas)

        # Calibration offset
        offset = calibration_offsets.get(m.slug, 0.0)
        # Auto-offset from correction counts (3+ same direction)
        if m.slug in calibration.correction_counts:
            counts = calibration.correction_counts[m.slug]
            if counts.get("higher", 0) >= 3:
                offset += 0.04
            elif counts.get("lower", 0) >= 3:
                offset -= 0.04

        weight = base_score + recency + urgency + loops + offset

        # External input staleness
        cadence = EXTERNAL_INPUT_CADENCE.get(m.context_batch, EXTERNAL_INPUT_CADENCE_DEFAULT)
        ext_stale = False
        ext_days_since = None
        if m.track_external_input and m.last_active and (today - m.last_active).days <= 7 and loop_count > 0:
            if m.last_external_input:
                ext_days_since = (today - m.last_external_input).days
                ext_stale = ext_days_since > cadence
            else:
                ext_days_since = None
                ext_stale = True  # never had external input

        # Staleness flag (last_active > 14 days as default)
        days_since_active = (today - m.last_active).days if m.last_active else None
        stale_flag = days_since_active is not None and days_since_active > 14

        results.append(EffortResult(
            slug=m.slug,
            context_batch=m.context_batch,
            base_score=round(base_score, 2),
            recency_boost=round(recency, 3),
            urgency_spike=round(urgency, 3),
            urgency_breakdown=urgency_breakdown,
            loop_factor=round(loops, 3),
            loop_count=loop_count,
            calibration_offset=round(offset, 3),
            priority_weight=round(weight, 3),
            open_items=open_items,
            external_input=ExternalInput(
                last_input=m.last_external_input.isoformat() if m.last_external_input else None,
                cadence_days=cadence,
                days_since=ext_days_since,
                stale=ext_stale,
            ),
            stale_flag=stale_flag,
            days_since_active=days_since_active,
        ))

    # Sort by priority_weight descending
    results.sort(key=lambda r: r.priority_weight, reverse=True)
    return results


def compute_effective_item_scores(
    effort_results: list[EffortResult],
    notes: list[NoteData],
    maps: list[MapData],
    dep_states: dict[str, dict],
    today: date,
) -> tuple[list[ItemScore], list[WaitingItem]]:
    """Compute per-item effective scores. Returns (scored_items, waiting_items)."""
    weight_by_effort = {r.slug: r.priority_weight for r in effort_results}
    items: list[ItemScore] = []
    waiting: list[WaitingItem] = []

    def _score_item(
        item_id: str,
        item_type: str,
        effort_slug: str,
        description: str,
        importance: str,
        status: str,
        due: date | None,
        depends_on: list[str],
        waiting_since: date | None,
        updated: date | None,
    ):
        effort_weight = weight_by_effort.get(effort_slug, 0.0)
        imp_mod = IMPORTANCE_MODIFIERS.get(importance, IMPORTANCE_MODIFIERS[DEFAULT_IMPORTANCE])

        # Due proximity boost
        due_boost = 0.0
        is_waiting = status == "waiting"

        if due is not None:
            days_until = (due - today).days
            if is_waiting and days_until > 1:
                # Waiting exception: suppress boost
                due_boost = 0.0
            else:
                if days_until < 0:
                    due_boost = 0.10  # overdue
                elif days_until <= 1:
                    due_boost = 0.06  # within 1d (handles waiting items near due)
                elif days_until <= 3:
                    due_boost = 0.06  # within 3d
                elif days_until <= 7:
                    due_boost = 0.03  # within 7d

        # Status modifier
        status_mod = 0.0
        if is_waiting:
            if due is not None:
                days_until = (due - today).days
                if days_until > 1:
                    status_mod = 0.0  # waiting exception: suppress
                # else: no extra status mod, due_boost handles it
            else:
                # Waiting without due date, check days waiting
                ref_date_for_waiting = waiting_since or updated
                if ref_date_for_waiting:
                    days_w = (today - ref_date_for_waiting).days
                    if days_w > 3:
                        status_mod = 0.02
        else:
            # Check for unblocked dependency
            dep_key = item_id.split("::")[2] if "::" in item_id else description
            # For notes, use slug
            if item_type == "note":
                slug = description  # we'll fix this below
                dep_info = dep_states.get(slug, {})
            else:
                dep_info = {}
            if dep_info.get("state") == "unblocked":
                status_mod = 0.02

        score = effort_weight + imp_mod + due_boost + status_mod
        breakdown = ScoreBreakdown(
            effort_weight=round(effort_weight, 3),
            importance_modifier=imp_mod,
            due_proximity_boost=due_boost,
            status_modifier=status_mod,
        )

        # Determine if this is a waiting item that should be gated
        if is_waiting:
            gate_active = True  # default: exclude from Important Items
            if due is not None:
                days_until = (due - today).days
                if days_until <= 1:
                    gate_active = False  # actionable — re-enters Important Items

            ref_for_days = waiting_since or updated
            days_w = (today - ref_for_days).days if ref_for_days else 0

            waiting.append(WaitingItem(
                id=item_id,
                effort=effort_slug,
                description=description,
                importance=importance,
                waiting_since=ref_for_days.isoformat() if ref_for_days else None,
                days_waiting=days_w,
                due=due.isoformat() if due else None,
                effective_score=round(score, 3),
                gate_active=gate_active,
            ))

            if gate_active:
                return  # don't add to main items list

        # Dependency state
        dep_state = "no_deps"
        blocking = []
        if item_type == "note":
            dep_info = dep_states.get(item_id.split("::")[-1] if "::" in item_id else "", {})
            dep_state = dep_info.get("state", "no_deps")
            blocking = dep_info.get("blocking", [])

        items.append(ItemScore(
            id=item_id,
            type=item_type,
            effort=effort_slug,
            description=description,
            importance=importance,
            status=status,
            due=due.isoformat() if due else None,
            depends_on=depends_on,
            dependency_state=dep_state,
            effective_score=round(score, 3),
            score_breakdown=breakdown,
            waiting_suppressed=False,
        ))

    # Build active thread sets + summaries per Map for filtering and descriptions
    active_threads_by_effort: dict[str, set[str]] = {}
    summaries_by_effort: dict[str, dict[str, str]] = {}
    for m in maps:
        active_threads_by_effort[m.slug] = set(m.active_thread_summaries.keys())
        summaries_by_effort[m.slug] = m.active_thread_summaries

    # Score all active/waiting Notes that are Active Threads (excluding reference/theory)
    for n in notes:
        if n.status not in ("active", "waiting"):
            continue
        if n.is_reference:
            continue
        for eff in n.efforts:
            if eff not in weight_by_effort:
                continue
            # Only score Notes listed under Active Threads in their Map
            if n.slug not in active_threads_by_effort.get(eff, set()):
                continue
            item_id = f"{eff}::note::{n.slug}"

            # Use Map entry summary as description, fall back to slug
            description = summaries_by_effort.get(eff, {}).get(n.slug, n.slug)

            # For dependency state lookup, use slug directly
            dep_info = dep_states.get(n.slug, {})

            _score_item(
                item_id=item_id,
                item_type="note",
                effort_slug=eff,
                description=description,
                importance=n.importance,
                status=n.status,
                due=n.due,
                depends_on=n.depends_on,
                waiting_since=None,
                updated=n.updated,
            )

    # Score all open/waiting Minor Actions
    for m in maps:
        for ma in m.minor_actions:
            item_id = f"{m.slug}::minor::{ma.description[:60]}"
            _score_item(
                item_id=item_id,
                item_type="minor_action",
                effort_slug=m.slug,
                description=ma.description,
                importance=ma.importance,
                status="waiting" if ma.status == "waiting" else "active",
                due=ma.due,
                depends_on=ma.depends_on,
                waiting_since=ma.waiting_since,
                updated=None,
            )

    # Sort items by effective_score descending
    items.sort(key=lambda i: i.effective_score, reverse=True)
    return items, waiting


def compute_batch_aggregates(
    effort_results: list[EffortResult],
    items: list[ItemScore],
    waiting_items: list[WaitingItem],
    today: date,
) -> list[BatchResult]:
    """Group efforts by batch and compute gating status."""
    batches: dict[str, list[EffortResult]] = {}
    for r in effort_results:
        batches.setdefault(r.context_batch, []).append(r)

    # Check for due/waiting signals per batch
    items_by_batch: dict[str, list] = {}
    for item in items:
        for r in effort_results:
            if r.slug == item.effort:
                items_by_batch.setdefault(r.context_batch, []).append(item)
                break

    waiting_by_batch: dict[str, list] = {}
    for w in waiting_items:
        for r in effort_results:
            if r.slug == w.effort:
                waiting_by_batch.setdefault(r.context_batch, []).append(w)
                break

    results = []
    combined_weights = {}
    for batch_name, efforts in batches.items():
        combined = sum(r.priority_weight for r in efforts)
        combined_weights[batch_name] = combined

    top_weight = max(combined_weights.values()) if combined_weights else 0.0

    for batch_name, efforts in batches.items():
        combined = combined_weights[batch_name]
        effort_slugs = [r.slug for r in efforts]

        has_due = any(
            i.due and (date.fromisoformat(i.due) - today).days <= 7
            for i in items_by_batch.get(batch_name, [])
            if i.due
        )
        has_waiting_3d = any(
            w.days_waiting > 3
            for w in waiting_by_batch.get(batch_name, [])
        )

        gated = (
            top_weight > 0
            and combined < BATCH_GATING_THRESHOLD * top_weight
            and not has_due
            and not has_waiting_3d
        )

        results.append(BatchResult(
            name=batch_name,
            combined_weight=round(combined, 3),
            efforts=effort_slugs,
            gated=gated,
            has_due_within_7d=has_due,
            has_waiting_over_3d=has_waiting_3d,
        ))

    results.sort(key=lambda b: b.combined_weight, reverse=True)
    return results


def compute_resurfacing(notes: list[NoteData], today: date) -> list[ResurfacingCandidate]:
    """Find notes past their timescale threshold for resurfacing."""
    candidates = []
    for n in notes:
        if n.status not in ("active", "waiting"):
            continue
        if n.updated is None:
            continue

        ts = n.timescale
        threshold = TIMESCALE_THRESHOLDS.get(ts, TIMESCALE_DEFAULT) if ts else TIMESCALE_DEFAULT
        days_since = (today - n.updated).days

        if days_since > threshold:
            candidates.append(ResurfacingCandidate(
                slug=n.slug,
                effort=n.efforts[0] if n.efforts else "",
                timescale=ts,
                threshold_days=threshold,
                days_since_update=days_since,
            ))

    candidates.sort(key=lambda c: c.days_since_update, reverse=True)
    return candidates


# ── Output Assembly ────────────────────────────────────────────────────────

def to_serializable(obj: Any) -> Any:
    """Convert dataclasses and dates to JSON-serializable form."""
    if hasattr(obj, "__dataclass_fields__"):
        return {k: to_serializable(v) for k, v in asdict(obj).items()}
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, list):
        return [to_serializable(i) for i in obj]
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    return obj


def apply_effort_cap(
    items: list[ItemScore],
    cap: int,
    floor: int = 3,
    ceiling: int = IMPORTANT_ITEMS_CEILING,
) -> list[ItemScore]:
    """Apply per-effort cap to Important Items, with low-importance items exempt.

    Cap applies to high/medium items per effort — prevents any single effort from
    dominating the list. Low-importance items compete naturally without suppression,
    serving as break-time / peripheral tasks.

    Items are pre-sorted by effective_score descending."""
    effort_counts: dict[str, int] = {}  # counts only high/medium items
    result: list[ItemScore] = []
    deferred: list[ItemScore] = []

    for item in items:
        if item.effective_score < 0.55:
            continue
        # Low-importance items are exempt from the effort cap
        if item.importance == "low":
            result.append(item)
            continue
        count = effort_counts.get(item.effort, 0)
        if count < cap:
            result.append(item)
            effort_counts[item.effort] = count + 1
        else:
            deferred.append(item)

    # Re-sort since low items were interleaved
    result.sort(key=lambda i: i.effective_score, reverse=True)

    # Enforce floor — if under, pull from deferred
    if len(result) < floor:
        for item in deferred:
            result.append(item)
            if len(result) >= floor:
                break
        result.sort(key=lambda i: i.effective_score, reverse=True)

    # Enforce ceiling
    if len(result) > ceiling:
        result = result[:ceiling]

    return result


def build_briefing_output(
    effort_results: list[EffortResult],
    important_items: list[ItemScore],
    waiting_items: list[WaitingItem],
    batches: list[BatchResult],
    resurfacing: list[ResurfacingCandidate],
    calibration: CalibrationData,
    warnings: list[dict],
    today: date,
    effort_cap: int,
    system_maps: list[dict] | None = None,
) -> dict:
    """Compact output with only what the /pulse briefing needs.
    ~200 lines instead of ~2400."""
    return {
        "computed_at": datetime.now().isoformat(timespec="seconds"),
        "reference_date": today.isoformat(),
        "effort_cap": effort_cap,
        "efforts": [
            {
                "slug": e.slug,
                "context_batch": e.context_batch,
                "priority_weight": e.priority_weight,
                "loop_count": e.loop_count,
                "days_since_active": e.days_since_active,
                "stale": e.stale_flag,
                "ext_input_stale": e.external_input.stale,
                "ext_input_days": e.external_input.days_since,
            }
            for e in effort_results
        ],
        "important_items": [
            {
                "description": i.description,
                "effort": i.effort,
                "score": i.effective_score,
                "importance": i.importance,
                "due": i.due,
                "dep": i.dependency_state if i.dependency_state != "no_deps" else None,
            }
            for i in important_items
        ],
        "waiting": [
            {
                "description": w.description,
                "effort": w.effort,
                "days": w.days_waiting,
                "due": w.due,
                "gate": w.gate_active,
            }
            for w in waiting_items
        ],
        "batches": [
            {
                "name": b.name,
                "weight": b.combined_weight,
                "efforts": b.efforts,
                "gated": b.gated,
            }
            for b in batches
        ],
        "resurfacing": [
            {
                "slug": r.slug,
                "effort": r.effort,
                "timescale": r.timescale,
                "days": r.days_since_update,
            }
            for r in resurfacing
        ],
        "system_efforts": system_maps or [],
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description="PULSE Priority Calculator")
    parser.add_argument(
        "--vault",
        default=None,
        help="Path to vault root (overrides $PULSE_VAULT env var; default: ./pulse-vault)",
    )
    parser.add_argument("--date", help="Override date (YYYY-MM-DD) for testing")
    parser.add_argument("--calibration-offsets", help="JSON object of {effort: offset} overrides")
    parser.add_argument("--effort-cap", type=int, default=EFFORT_ITEM_CAP,
                        help=f"Max items per effort in Important Items (default: {EFFORT_ITEM_CAP})")
    parser.add_argument("--briefing", action="store_true",
                        help="Compact output for /pulse briefing (default: full diagnostic output)")
    parser.add_argument("--cache", help="Write output to this path (in addition to stdout)")
    args = parser.parse_args()

    # Vault path resolution: --vault flag > $PULSE_VAULT env var > ./pulse-vault default
    raw_vault = args.vault or os.environ.get("PULSE_VAULT") or "./pulse-vault"
    vault_path = Path(raw_vault).resolve()

    today = date.fromisoformat(args.date) if args.date else date.today()
    cal_offsets: dict[str, float] = {}
    if args.calibration_offsets:
        try:
            cal_offsets = json.loads(args.calibration_offsets)
        except json.JSONDecodeError:
            print("Warning: could not parse --calibration-offsets", file=sys.stderr)

    all_warnings: list[dict] = []

    # Phase B: Load Maps
    maps, map_warnings = load_maps(vault_path, today)
    all_warnings.extend(map_warnings)

    # Load system maps (excluded from priority computation, included in output)
    system_maps = load_system_maps(vault_path)

    # Phase C: Load Notes (include archive for dep resolution)
    notes, note_warnings = load_notes(vault_path, today, include_archive=True)
    all_warnings.extend(note_warnings)

    # Active notes only (for computation — archive is only for dep resolution)
    active_notes = [n for n in notes if n.status in ("active", "waiting")]

    # Load calibration
    calibration = load_calibration(vault_path)

    # Phase D: Compute
    effort_results = compute_effort_weights(maps, active_notes, calibration, cal_offsets, today)

    # Resolve dependencies
    dep_states = resolve_dependencies(active_notes, notes)

    # Effective item scores
    items, waiting_items = compute_effective_item_scores(
        effort_results, active_notes, maps, dep_states, today
    )

    # Batch aggregates
    batches = compute_batch_aggregates(effort_results, items, waiting_items, today)

    # Resurfacing
    resurfacing = compute_resurfacing(active_notes, today)

    # Apply effort cap for Important Items display
    important_items = apply_effort_cap(items, cap=args.effort_cap)

    # Assemble output
    if args.briefing:
        output = build_briefing_output(
            effort_results, important_items, waiting_items,
            batches, resurfacing, calibration, all_warnings,
            today, args.effort_cap,
            system_maps=system_maps,
        )
    else:
        output = {
            "computed_at": datetime.now().isoformat(timespec="seconds"),
            "reference_date": today.isoformat(),
            "effort_cap": args.effort_cap,
            "efforts": to_serializable(effort_results),
            "system_efforts": system_maps,
            "important_items": to_serializable(important_items),
            "items": to_serializable(items),
            "waiting_items": to_serializable(waiting_items),
            "dependencies": to_serializable(dep_states),
            "batches": to_serializable(batches),
            "resurfacing": to_serializable(resurfacing),
            "calibration": {
                "correction_counts": calibration.correction_counts,
                "offsets_applied": cal_offsets,
                "patterns": calibration.patterns,
            },
            "warnings": all_warnings,
        }

    json_str = json.dumps(output, indent=2, default=lambda o: o.isoformat() if isinstance(o, (date, datetime)) else str(o))

    # Write to cache file if requested
    if args.cache:
        cache_path = Path(args.cache)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json_str + "\n", encoding="utf-8")

    print(json_str)


if __name__ == "__main__":
    main()
