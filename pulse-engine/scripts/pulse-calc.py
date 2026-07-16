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
import statistics
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

# Generic text-dedup helper (used by the proposal layer dedup — deadline/floor vs
# core). Not a carry-forward mechanism: the carry-forward feature is not part of
# the public engine.
DEDUP_TOKEN_OVERLAP = 0.60
_STOPWORDS = {
    "a", "an", "the", "to", "of", "for", "and", "or", "in", "on", "at", "with",
    "my", "is", "it", "as", "by", "from", "into", "via", "vs", "s",
}

# ── Stage B: capacity-calc (versioned) ───────────────────────────────────────
CAPACITY_CALC_VERSION = "1.0"
PROPOSAL_SCHEMA_VERSION = "1.0"
KNOWN_RUBRIC_VERSIONS = {"1.0", "1.1"}  # bump when the capacity rubric doc revs

# Load-tier multipliers (depth / resistance). Versioned table — refinable.
CAPACITY_MULTIPLIERS = {
    "low":      {"depth": 1.0, "resistance": 1.0},
    "moderate": {"depth": 0.7, "resistance": 0.6},
    "high":     {"depth": 0.4, "resistance": 0.3},
    "recovery": {"depth": 0.1, "resistance": 0.0},
}
# Worst-tier ordering (higher rank = worse day). Used for "worse tier wins".
_LOAD_RANK = {"low": 0, "moderate": 1, "high": 2, "recovery": 3}
_LOAD_BY_RANK = {v: k for k, v in _LOAD_RANK.items()}

# Practice-quality-graded depth-multiplier lift (samatha ladder). Numeric-only;
# the rubric doc carries the depersonalized description.
SAMATHA_DEPTH_LIFT = {
    "none": 0.0, "missed": 0.0,
    "access": 0.075, "sub-j1": 0.075,
    "j1-j3": 0.15, "j4-plus": 0.15,
}

# Depth / resistance per-item costs (versioned tiers). Ordered best→worst.
DEPTH_COSTS = {"minimal": 0.0, "light": 0.08, "standard": 0.20, "substantial": 0.50, "heavy": 0.85}
RESISTANCE_COSTS = {"low": 0.0, "moderate": 0.40, "high": 0.85}
_DEPTH_LADDER = ["minimal", "light", "standard", "substantial", "heavy"]
PRIMED_DEPTH_DISCOUNT = 0.15  # `primed` tag: depth −0.15, floored at the tier-below cost

# Flags that count as day-degradation for the count-range clean-day bonus.
DEGRADATION_FLAGS = {"collapse-risk", "over-prediction", "physical-relational-at-risk"}

DEFAULT_DEPTH_TIER = "standard"        # unclassified propose items default here
DEFAULT_RESISTANCE_TIER = "moderate"
_OVER_RATIO = 99.0  # sentinel utilization ratio when a budget is 0 but cost > 0

# ── Stage B → --propose (layered assembly) ───────────────────────────────────
SLACK_FILL_TARGET = 0.625   # greedy-fill core until depth_used ≥ this × depth_budget
SLACK_RATIO = 0.375         # slack_slots = round(SLACK_RATIO × (core+floor+deadline)), min 1
STRETCH_COUNT_MAX = 3
STATIC_FLOOR_CORE = 4       # static-floor sizing: up to N substantive core items
CORE_MIN = 2                # force-include top-N ranked core items regardless of budget target
CORE_MIN_COLLAPSE = 1       # collapse-risk days force-include only the single top item
DEADLINE_DUE_HORIZON = 1    # deadline/due layer: due ≤ ref_date + this many days
CANDIDATE_POOL_RANKED = 10  # --candidates: top-N ranked items exposed to the grader

_ABBREV_WEEKDAY = {
    "mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6,
}

# ── Stage 4: --gates (compute-only) ──────────────────────────────────────────
PAR_FALLBACK_MAX_AGE_DAYS = 14  # accuracy-table PAR fallback older than this → stale (no revert signal)
GATES_V1 = {
    # Graduation gate (capacity BCR, ACR-floored, min-data). NEW compound predicate.
    "capacity_bcr_target": 0.80,
    "capacity_bcr_revert": 0.70,
    "capacity_min_days_graduate": 10,
    "capacity_min_days_revert": 4,
    "agenda_acr_floor": 0.60,
    "agenda_edit_median_floor": 3,
    "agenda_revert_acr": 0.60,
    "window_days": 14,
    "revert_window_days": 7,
    # Calibration-only — retained for health/confidence; does NOT gate graduation.
    "priority_par_target": 0.85,
    "priority_min_sessions": 10,
    "priority_revert": 0.70,
    "under_ambition_stretch_rate": 0.50,
    "under_ambition_min_days": 8,
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


@dataclass
class CapacityItemCost:
    id: str
    effort: str
    label: str
    layer_hint: str | None
    depth_tier: str
    resistance_tier: str
    tags: list[str]
    depth_cost: float
    resistance_cost: float
    flags: list[str] = field(default_factory=list)


@dataclass
class CapacityResult:
    calc_version: str
    rubric_version: str
    date: str
    load: str
    load_base: str            # sleep-derived tier before samatha lift note
    mult_depth: float         # post-lift depth multiplier (== depth_budget)
    mult_depth_base: float    # pre-lift depth multiplier
    mult_res: float
    samatha_lift: float
    depth_budget: float
    resistance_budget: float
    depth_used: float
    resistance_used: float
    depth_ratio: float
    resistance_ratio: float
    depth_status: str         # within | edge | over
    resistance_status: str
    binding: str              # depth | resistance | both | neither
    count_low: int
    count_high: int
    committed_total: int
    count_unreliable: bool
    flags: list[str]
    physical_relational_ids: list[str]
    insight_lift_candidate: bool
    item_costs: list[CapacityItemCost]
    capacity_frozen_row: str


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


# ── Text dedup helper ────────────────────────────────────────────────────────

def _normalize_tokens(text: str) -> set[str]:
    """Lowercase, strip wikilinks/punctuation, drop stopwords → token set.
    Generic tokenizer used by the proposal layer-dedup (deadline/floor vs core)."""
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)          # unwrap wikilinks
    text = re.sub(r"\([^)]*\)", " ", text)                   # drop parentheticals
    text = re.sub(r"[^a-z0-9\s-]", " ", text.lower())        # keep alnum + hyphen
    toks = {t for t in text.replace("-", " ").split() if t and t not in _STOPWORDS}
    return toks


# ── Stage B: capacity-calc ───────────────────────────────────────────────────

def parse_graded_input(raw: str) -> tuple[dict, list[dict]]:
    """Accept a path OR inline JSON string. Returns (graded_dict, warnings)."""
    warnings: list[dict] = []
    p = Path(raw)
    text = raw
    try:
        if p.exists() and p.is_file():
            text = p.read_text(encoding="utf-8")
    except OSError:
        pass
    try:
        return json.loads(text), warnings
    except json.JSONDecodeError as e:
        warnings.append({"type": "graded_parse_error", "detail": str(e)})
        return {}, warnings


def _num(x) -> float | None:
    """Coerce a graded numeric field to float; non-coercible → None.

    A sub-agent grader may emit numbers as strings (e.g. "6.5") or garbage; treating
    a non-coercible value as absent keeps the deterministic comparisons below from
    crashing on a TypeError. None behaves exactly like a missing field."""
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _derive_load(graded: dict) -> tuple[str, bool]:
    """Sleep → load tier. Worst-of-two-axes (hours vs quality); recovery overrides.

    Realizes the spec's four rules via the 'worse tier wins' precedence:
    hours→{≥7.5 low, ≥6.5 moderate, <6.5 high}; quality→{good/excellent low,
    fair moderate, poor/below-avg high, depleted recovery}; take the WORSE
    (higher-rank) of the two axes so `low` requires BOTH hours≥7.5 AND good/
    excellent quality. Explicit day_context.recovery forces recovery.
    """
    sleep = graded.get("sleep") or {}
    hours = _num(sleep.get("hours"))
    tier = str(sleep.get("tier") or "").lower()
    recovery_flag = bool((graded.get("day_context") or {}).get("recovery"))

    ranks = []
    if hours is not None:
        if hours >= 7.5:
            ranks.append(_LOAD_RANK["low"])
        elif hours >= 6.5:
            ranks.append(_LOAD_RANK["moderate"])
        else:
            ranks.append(_LOAD_RANK["high"])
    q = {
        "excellent": "low", "good": "low", "fair": "moderate",
        "below-avg": "high", "poor": "high", "depleted": "recovery",
    }.get(tier)
    if q is not None:
        ranks.append(_LOAD_RANK[q])

    base_rank = max(ranks) if ranks else _LOAD_RANK["moderate"]
    if recovery_flag:
        base_rank = _LOAD_RANK["recovery"]
    return _LOAD_BY_RANK[base_rank], recovery_flag


def _derive_multipliers(load: str, samatha_tier: str) -> tuple[float, float, float, float, list[str]]:
    """(mult_depth_base, mult_depth_post_lift, mult_res, samatha_lift, flags).

    The samatha lift is added to the DEPTH multiplier only. The reported load tier
    stays sleep-derived so there is a single source of truth for load (fatigue-
    exemption, over-prediction, etc.).
    """
    base = CAPACITY_MULTIPLIERS[load]
    mult_depth_base = base["depth"]
    mult_res = base["resistance"]
    lift = SAMATHA_DEPTH_LIFT.get(samatha_tier, 0.0)
    flags = ["deep-attainment-watch"] if samatha_tier == "j4-plus" else []
    return mult_depth_base, round(mult_depth_base + lift, 3), mult_res, lift, flags


def _day_flags(graded: dict, load: str) -> tuple[list[str], bool, bool]:
    """Day-level flags independent of the committed set.
    Returns (flags, collapse_risk, insight_lift_candidate)."""
    dctx = graded.get("day_context") or {}
    sleep = graded.get("sleep") or {}
    hours = _num(sleep.get("hours"))
    tier = str(sleep.get("tier") or "").lower()
    s3 = _num(graded.get("sleep_3day_avg"))
    trend = str(graded.get("sleep_trend") or "").lower()
    sprint_tail = bool(dctx.get("sprint_tail"))
    fasting = bool(dctx.get("fasting"))

    flags: list[str] = []
    collapse = False
    if (s3 is not None and s3 < 7.0 and trend == "declining" and sprint_tail) or (
        hours is not None and hours < 5.5 and tier == "poor"
    ):
        collapse = True
        flags.append("collapse-risk")
    if load in ("high", "recovery") or fasting or sprint_tail:
        flags.append("over-prediction")

    insight_tier = str((graded.get("insight") or {}).get("tier") or "none").lower()
    insight_lift_candidate = insight_tier == "good"
    return flags, collapse, insight_lift_candidate


def _one_cost(
    dtier: str, rtier: str, tags: list[str], effort: str, effort_seen: set,
    mult_depth: float, fatigue: bool, unclassified: bool,
) -> tuple[float, float, list[str], str, str]:
    """Cost of a single item given running effort_seen state. Does not mutate it."""
    flags: list[str] = []
    if dtier not in DEPTH_COSTS:
        dtier = DEFAULT_DEPTH_TIER
    if rtier not in RESISTANCE_COSTS:
        rtier = DEFAULT_RESISTANCE_TIER
    if unclassified:
        flags.append("unclassified-default")

    depth = DEPTH_COSTS[dtier]
    has_primed = "primed" in tags
    has_partial = "partial-carry" in tags
    if has_primed and has_partial:
        flags.append("tag-conflict:partial-carry-wins")  # partial-carry wins; warn
    if has_partial:  # bump one depth tier up
        idx = _DEPTH_LADDER.index(dtier)
        depth = DEPTH_COSTS[_DEPTH_LADDER[min(idx + 1, len(_DEPTH_LADDER) - 1)]]
        flags.append("depth-underscore")
    elif has_primed:  # depth −0.15, floored at the tier-below cost
        idx = _DEPTH_LADDER.index(dtier)
        below = DEPTH_COSTS[_DEPTH_LADDER[max(idx - 1, 0)]]
        depth = max(depth - PRIMED_DEPTH_DISCOUNT, below)
    if fatigue and ("generative" in tags or "momentum" in tags):
        depth = depth * mult_depth  # exactly cancels the budget discount for this item
        flags.append("fatigue-exempt")

    rcost = 0.0 if effort in effort_seen else RESISTANCE_COSTS[rtier]
    return round(depth, 3), round(rcost, 3), flags, dtier, rtier


def _item_costs(committed: list[dict], mult_depth: float, load: str) -> list[CapacityItemCost]:
    """Per-item costs over the committed set in order (resistance paid once/effort)."""
    fatigue = load in ("high", "recovery")
    effort_seen: set = set()
    out: list[CapacityItemCost] = []
    for it in committed:
        eff = it.get("effort", "")
        tags = [str(t).lower() for t in (it.get("tags") or [])]
        dtier = str(it.get("depth_tier") or DEFAULT_DEPTH_TIER).lower()
        rtier = str(it.get("resistance_tier") or DEFAULT_RESISTANCE_TIER).lower()
        depth, rcost, flags, dtier2, rtier2 = _one_cost(
            dtier, rtier, tags, eff, effort_seen, mult_depth, fatigue,
            bool(it.get("_unclassified")),
        )
        effort_seen.add(eff)  # 2nd+ item in same effort → resistance 0
        out.append(CapacityItemCost(
            id=it.get("id", ""), effort=eff, label=it.get("label", it.get("id", "")),
            layer_hint=it.get("layer_hint"), depth_tier=dtier2, resistance_tier=rtier2,
            tags=tags, depth_cost=depth, resistance_cost=rcost, flags=flags,
        ))
    return out


def _ratio(used: float, budget: float) -> float:
    if budget <= 0:
        return 0.0 if used <= 1e-9 else _OVER_RATIO
    return used / budget


def _status(r: float) -> str:
    if r > 1.0:
        return "over"
    if r >= 0.8:
        return "edge"
    return "within"


def compute_capacity(graded: dict, committed: list[dict], ref_date: date) -> CapacityResult | None:
    """Stage-B deterministic capacity vector over a committed item set.
    Returns None when sleep input is absent (caller skips)."""
    sleep = graded.get("sleep") or {}
    if sleep.get("hours") is None and not sleep.get("tier"):
        return None  # no sleep input → capacity cannot run

    date_str = graded.get("date") or ref_date.isoformat()
    rubric_version = str(graded.get("rubric_version") or "unknown")

    load, _recovery = _derive_load(graded)
    samatha_tier = str((graded.get("samatha") or {}).get("tier") or "none").lower()
    mult_depth_base, mult_depth, mult_res, lift, lift_flags = _derive_multipliers(load, samatha_tier)
    depth_budget = round(1.0 * mult_depth, 3)
    resistance_budget = round(1.0 * mult_res, 3)

    flags, collapse, insight_candidate = _day_flags(graded, load)
    flags = list(flags) + lift_flags

    costs = _item_costs(committed, mult_depth, load)
    committed_total = len(costs)
    depth_used = round(sum(c.depth_cost for c in costs), 3)
    resistance_used = round(sum(c.resistance_cost for c in costs), 3)

    # physical/relational-at-risk (needs committed set)
    pr_ids = [c.id for c in costs if "embodied" in c.tags]
    if load in ("high", "recovery") and pr_ids:
        flags.append("physical-relational-at-risk")
    else:
        pr_ids = []

    depth_ratio = _ratio(depth_used, depth_budget)
    resistance_ratio = _ratio(resistance_used, resistance_budget)
    d, r = depth_ratio, resistance_ratio
    if d >= 0.8 and r >= 0.8 and abs(d - r) <= 0.1:
        binding = "both"
    elif d >= 0.8 or r >= 0.8:
        binding = "depth" if d >= r else "resistance"
    else:
        binding = "neither"

    # Count range (v1.0 — refinable). low = greedy cumulative fit in order.
    depth_cum = res_cum = 0.0
    count_low = 0
    for c in costs:
        if depth_cum + c.depth_cost > depth_budget + 1e-9 or \
           res_cum + c.resistance_cost > resistance_budget + 1e-9:
            break
        depth_cum += c.depth_cost
        res_cum += c.resistance_cost
        count_low += 1
    light_beyond = sum(1 for c in costs[count_low:] if c.depth_tier in ("light", "minimal"))
    clean_bonus = 0 if (set(flags) & DEGRADATION_FLAGS) else 1
    count_high = count_low + light_beyond + clean_bonus
    count_high = max(count_low, min(count_high, committed_total))

    flags_str = ",".join(flags) if flags else "none"
    row = (
        f"CAPACITY-FROZEN | date={date_str} | rubric={rubric_version} | calc={CAPACITY_CALC_VERSION} | "
        f"load={load} | mult_depth={mult_depth:.2f} | mult_res={mult_res:.2f} | "
        f"range={count_low}-{count_high}/{committed_total} | binding={binding} | flags={flags_str}"
    )

    return CapacityResult(
        calc_version=CAPACITY_CALC_VERSION, rubric_version=rubric_version, date=date_str,
        load=load, load_base=load, mult_depth=mult_depth, mult_depth_base=mult_depth_base,
        mult_res=mult_res, samatha_lift=lift, depth_budget=depth_budget,
        resistance_budget=resistance_budget, depth_used=depth_used, resistance_used=resistance_used,
        depth_ratio=round(depth_ratio, 3), resistance_ratio=round(resistance_ratio, 3),
        depth_status=_status(depth_ratio), resistance_status=_status(resistance_ratio),
        binding=binding, count_low=count_low, count_high=count_high, committed_total=committed_total,
        count_unreliable=collapse, flags=flags, physical_relational_ids=pr_ids,
        insight_lift_candidate=insight_candidate, item_costs=costs, capacity_frozen_row=row,
    )


# ── Stage B → --propose (layered agenda draft) ───────────────────────────────

def parse_routine_floor(template_path: Path, weekday: int) -> tuple[list[dict], list[dict]]:
    """Parse Templates/routine-floor.md → floor items matching today's weekday.
    Format: `- item text (days: daily|mon,tue,…; effort: slug)`.
    Missing template → empty floor + a warning (graceful)."""
    warnings: list[dict] = []
    items: list[dict] = []
    if not template_path.exists():
        warnings.append({"type": "missing_floor_template", "file": str(template_path)})
        return items, warnings
    try:
        content = template_path.read_text(encoding="utf-8")
    except OSError as e:
        warnings.append({"type": "floor_read_error", "detail": str(e)})
        return items, warnings
    _, body = parse_frontmatter(content)
    for line in body.split("\n"):
        s = line.strip()
        m = re.match(r"^-\s+(.*?)\s*\(\s*days:\s*([^;]+);\s*effort:\s*([^)]+)\)\s*$", s)
        if not m:
            continue
        text, days_raw, effort = m.group(1).strip(), m.group(2).strip().lower(), m.group(3).strip()
        if _floor_matches_day(days_raw, weekday):
            items.append({"text": text, "effort": effort})
    return items, warnings


def _floor_matches_day(days_raw: str, weekday: int) -> bool:
    tokens = [d.strip() for d in days_raw.split(",")]
    if "daily" in tokens:
        return True
    for d in tokens:
        if _ABBREV_WEEKDAY.get(d) == weekday or WEEKDAY_MAP.get(d) == weekday:
            return True
    return False


def _floor_id(effort: str, text: str) -> str:
    """Canonical id for a routine-floor item — must match everywhere (propose,
    --candidates, grader input) so classification lookups never miss."""
    return f"{effort}::floor::{re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')[:40]}"


def build_candidate_pool(
    important_items: list["ItemScore"], floor_items: list[dict], deadline_items: list[dict],
) -> list[dict]:
    """The gradeable candidate pool for the grader: exact item ids the proposal
    assembly will look up. Deadline/floor first (their layer wins on id collision),
    then top-ranked items."""
    pool: list[dict] = []
    seen: set = set()
    for c in deadline_items:
        if c["id"] in seen:
            continue
        seen.add(c["id"])
        pool.append({"id": c["id"], "label": c.get("label", c["id"]), "effort": c["effort"],
                     "layer_hint": "deadline", "due": c.get("due"), "carry": None})
    for f in floor_items:
        fid = _floor_id(f["effort"], f["text"])
        if fid in seen:
            continue
        seen.add(fid)
        pool.append({"id": fid, "label": f["text"], "effort": f["effort"],
                     "layer_hint": "floor", "due": None, "carry": None})
    for it in important_items[:CANDIDATE_POOL_RANKED]:
        if it.id in seen:
            continue
        seen.add(it.id)
        pool.append({"id": it.id, "label": it.description, "effort": it.effort,
                     "layer_hint": "core", "due": it.due, "carry": None})
    return pool


def _classify(item_id: str, effort: str, classified: dict) -> dict:
    """Look up an item's grader classification; default standard/moderate if absent."""
    g = classified.get(item_id)
    if g:
        return {
            "id": item_id, "effort": effort,
            "depth_tier": g.get("depth_tier", DEFAULT_DEPTH_TIER),
            "resistance_tier": g.get("resistance_tier", DEFAULT_RESISTANCE_TIER),
            "tags": g.get("tags", []) or [], "layer_hint": g.get("layer_hint"),
            "_unclassified": False,
        }
    return {
        "id": item_id, "effort": effort, "depth_tier": DEFAULT_DEPTH_TIER,
        "resistance_tier": DEFAULT_RESISTANCE_TIER, "tags": [], "layer_hint": None,
        "_unclassified": True,
    }


def collect_deadline_items(notes: list[NoteData], maps: list[MapData], ref_date: date) -> list[dict]:
    """Deadline/due layer: any open Note or Minor Action (ANY effort, incl. suppressed
    / below-floor) with due ≤ ref_date + DEADLINE_DUE_HORIZON. This is the internal
    per-item due-date exemption path over vault items — NOT external-calendar ingestion
    (external calendars are out of scope)."""
    horizon = ref_date + timedelta(days=DEADLINE_DUE_HORIZON)
    out: list[dict] = []
    seen: set = set()
    for n in notes:
        if n.status not in ("active", "waiting") or n.due is None or n.due > horizon:
            continue
        eff = n.efforts[0] if n.efforts else ""
        key = ("note", n.slug)
        if key in seen:
            continue
        seen.add(key)
        out.append({"id": f"{eff}::note::{n.slug}", "slug": n.slug, "effort": eff,
                    "label": n.slug, "due": n.due.isoformat()})
    for m in maps:
        for ma in m.minor_actions:
            if ma.due is None or ma.due > horizon:
                continue
            out.append({"id": f"{m.slug}::minor::{ma.description[:60]}", "slug": None,
                        "effort": m.slug, "label": ma.description, "due": ma.due.isoformat()})
    return out


def build_proposal(
    important_items: list[ItemScore], deadline_items: list[dict], floor_items: list[dict],
    graded: dict | None, ref_date: date, vault_path: Path,
) -> dict:
    """Assemble the layered agenda draft (deadline / floor / core / stretch / slack)
    and its capacity block. Returns the proposal artifact dict."""
    date_str = (graded or {}).get("date") or ref_date.isoformat()
    classified = {it["id"]: it for it in (graded or {}).get("items", [])}
    capacity_available = bool(graded and (graded.get("sleep") or {}))

    if capacity_available:
        load, _rec = _derive_load(graded)
        samatha_tier = str((graded.get("samatha") or {}).get("tier") or "none").lower()
        _mdb, mult_depth, _mr, _lift, _lf = _derive_multipliers(load, samatha_tier)
        depth_budget = round(1.0 * mult_depth, 3)
        fatigue = load in ("high", "recovery")
        sized_by = "capacity"
    else:
        load, mult_depth, depth_budget, fatigue, sized_by = "unknown", 1.0, None, False, "static-floor"

    # Keys already consumed by deadline/floor (skip them in the ranked core).
    used_slugs = {c["slug"] for c in deadline_items if c.get("slug")}
    floor_deadline_texts = [_normalize_tokens(c.get("label", "")) for c in deadline_items]
    floor_deadline_texts += [_normalize_tokens(f["text"]) for f in floor_items]

    def _already_placed(item: ItemScore) -> bool:
        slug = item.id.split("::")[-1]
        if slug in used_slugs:
            return True
        dt = _normalize_tokens(item.description)
        for ft in floor_deadline_texts:
            if ft and dt and len(ft & dt) / len(ft) >= DEDUP_TOKEN_OVERLAP:
                return True
        return False

    core: list[ItemScore] = []
    consumed_ids: set = set()
    effort_seen: set = set()
    depth_used = 0.0
    high_res_count = 0
    cap_tripped = False
    target = SLACK_FILL_TARGET * depth_budget if depth_budget is not None else None

    # Seed the depth budget with the already-committed deadline + floor layers so the
    # greedy core fills only the REMAINING budget. Without this the committed set
    # (deadline + floor + core) ran ~2x over depth_budget and the frozen range sat far
    # below the committed count. Walk deadline → floor in the same order (threading the
    # same effort_seen) as the committed-set / capacity recompute so resistance-once
    # accounting stays consistent end-to-end.
    def _seed_layer(item_id: str, effort: str) -> None:
        nonlocal depth_used
        cls = _classify(item_id, effort, classified)
        depth, _rc, _fl, _dt, _rt = _one_cost(
            str(cls["depth_tier"]).lower(), str(cls["resistance_tier"]).lower(),
            [str(t).lower() for t in cls["tags"]],
            effort, effort_seen, mult_depth, fatigue, cls["_unclassified"],
        )
        effort_seen.add(effort)
        if target is not None:
            depth_used += depth

    for c in deadline_items:
        _seed_layer(c["id"], c["effort"])
    for f in floor_items:
        _seed_layer(_floor_id(f["effort"], f["text"]), f["effort"])

    # Collapse-risk days force-include only the single top item; normal days force the
    # top CORE_MIN regardless of the seeded budget (guarantees a non-trivial agenda
    # even when deadline + floor already consume the budget). v1.0 — refinable.
    if capacity_available:
        _cf, collapse_risk, _ilc = _day_flags(graded, load)
    else:
        collapse_risk = False
    core_min = CORE_MIN_COLLAPSE if collapse_risk else CORE_MIN

    for it in important_items:
        if _already_placed(it):
            continue
        cls = _classify(it.id, it.effort, classified)
        rtier = str(cls["resistance_tier"]).lower()
        is_high = (rtier == "high") and (it.effort not in effort_seen)
        if is_high and high_res_count >= 1:
            cap_tripped = True
            continue  # hard cap: max 1 high-resistance item/day
        if target is None:  # static-floor sizing: up to STATIC_FLOOR_CORE items
            core.append(it)
            consumed_ids.add(it.id)
            effort_seen.add(it.effort)
            if is_high:
                high_res_count += 1
            if len(core) >= STATIC_FLOOR_CORE:
                break
            continue
        depth, _rc, _fl, _dt, _rt = _one_cost(
            str(cls["depth_tier"]).lower(), rtier, [str(t).lower() for t in cls["tags"]],
            it.effort, effort_seen, mult_depth, fatigue, cls["_unclassified"],
        )
        core.append(it)
        consumed_ids.add(it.id)
        effort_seen.add(it.effort)
        if is_high:
            high_res_count += 1
        depth_used += depth
        # Force-include the top core_min items; only then honor the greedy stop.
        if len(core) >= core_min and depth_used >= target - 1e-9:
            break

    # Stretch: next ranked items beyond the core (never budgeted / verdicted).
    stretch: list[ItemScore] = []
    for it in important_items:
        if it.id in consumed_ids or _already_placed(it):
            continue
        stretch.append(it)
        consumed_ids.add(it.id)
        if len(stretch) >= STRETCH_COUNT_MAX:
            break

    # Committed set (order: deadline → floor → core) for the capacity recompute.
    committed_dicts: list[dict] = []
    for c in deadline_items:
        cl = _classify(c["id"], c["effort"], classified)
        cl["label"] = c.get("label", c["id"])
        committed_dicts.append(cl)
    for f in floor_items:
        fid = _floor_id(f['effort'], f['text'])
        cl = _classify(fid, f["effort"], classified)
        cl["label"] = f["text"]
        committed_dicts.append(cl)
    for it in core:
        cl = _classify(it.id, it.effort, classified)
        cl["label"] = it.description
        committed_dicts.append(cl)

    capacity_result = compute_capacity(graded, committed_dicts, ref_date) if capacity_available else None
    cost_by_id = {c.id: c for c in (capacity_result.item_costs if capacity_result else [])}

    def _entry(item_id, effort, label, source, due=None):
        cl = _classify(item_id, effort, classified)
        c = cost_by_id.get(item_id)
        return {
            "id": item_id, "effort": effort, "label": label, "source": source, "due": due,
            "depth_tier": cl["depth_tier"], "resistance_tier": cl["resistance_tier"],
            "tags": cl["tags"], "layer_hint": cl["layer_hint"],
            "depth_cost": c.depth_cost if c else None,
            "resistance_cost": c.resistance_cost if c else None,
            "flags": (c.flags if c else (["unclassified-default"] if cl["_unclassified"] else [])),
            "carry": None,
        }

    deadline_entries = [_entry(c["id"], c["effort"], c.get("label", c["id"]), "deadline", c.get("due"))
                        for c in deadline_items]
    floor_entries = []
    for f in floor_items:
        fid = _floor_id(f['effort'], f['text'])
        floor_entries.append(_entry(fid, f["effort"], f["text"], "floor"))
    core_entries = [_entry(it.id, it.effort, it.description, "core", it.due) for it in core]
    stretch_entries = [_entry(it.id, it.effort, it.description, "stretch", it.due) for it in stretch]

    slack_slots = max(1, round(SLACK_RATIO * (len(core) + len(floor_items) + len(deadline_items))))

    # Day-type confidence
    reasons: list[str] = []
    dctx = (graded or {}).get("day_context") or {}
    cold = _num(dctx.get("cold_start_days")) or 0        # graded numeric — coerce before compare
    override_streak = _num(dctx.get("override_streak")) or 0
    collapse = bool(capacity_result and capacity_result.count_unreliable)
    deadline_nonempty = len(deadline_items) > 0
    deadline_3d = any(
        i.due and (date.fromisoformat(i.due) - ref_date).days <= 3
        for i in important_items if i.due
    )
    if collapse:
        reasons.append("collapse-risk")
    if cold > 3:
        reasons.append(f"cold_start_days={cold}")
    if override_streak > 1:
        reasons.append(f"override_streak={override_streak}")
    if not (deadline_nonempty or deadline_3d):
        reasons.append("no deadline / near-deadline anchor")
    if cap_tripped:
        reasons.append("high-resistance cap tripped during fill")
    confidence = "clean" if not [r for r in reasons if r != "high-resistance cap tripped during fill"] else "turbulent"

    agenda_frozen = (
        f"AGENDA-FROZEN | date={date_str} | core={len(core)} | floor={len(floor_items)} | "
        f"deadline={len(deadline_items)} | stretch={len(stretch)} | slack={slack_slots} | "
        f"confidence={confidence} | sized_by={sized_by} | schema={PROPOSAL_SCHEMA_VERSION}"
    )

    return {
        "schema_version": PROPOSAL_SCHEMA_VERSION,
        "computed_at": datetime.now().isoformat(timespec="seconds"),
        "date": date_str,
        "capacity": to_serializable(capacity_result) if capacity_result else None,
        "proposal": {
            "deadline": deadline_entries, "floor": floor_entries, "core": core_entries,
            "stretch": stretch_entries, "slack_slots": slack_slots,
            "confidence": confidence, "confidence_reasons": reasons, "sized_by": sized_by,
        },
        "rows": {
            "agenda_frozen": agenda_frozen,
            "capacity_frozen": capacity_result.capacity_frozen_row if capacity_result else None,
        },
    }


# ── --verdict (mechanical outcome scoring) ───────────────────────────────────

def compute_verdict(proposal: dict, actual: dict, ref_date: date) -> dict:
    """Mechanical count/binding/stretch verdict over a frozen proposal + actuals.
    Pure function — no vault loading."""
    cap = proposal.get("capacity") or {}
    date_str = proposal.get("date") or ref_date.isoformat()

    # Static-floor mornings freeze no capacity prediction (capacity block is null /
    # has no count_low). Emitting a MISS row here would poison BCR from every
    # input-less day, so skip cleanly with no CAPACITY-VERDICT row.
    if not proposal.get("capacity") or cap.get("count_low") is None:
        return {
            "skipped": "no capacity prediction in frozen artifact (static-floor day)",
            "date": date_str,
        }

    low = cap.get("count_low")
    high = cap.get("count_high")
    unreliable = bool(cap.get("count_unreliable"))
    binding_pred = cap.get("binding")
    calc_v = cap.get("calc_version", CAPACITY_CALC_VERSION)
    rubric_v = cap.get("rubric_version", "unknown")

    actual_n = actual.get("completed_committed")
    binding_actual = actual.get("binding_actual")
    stretch_offered = len(proposal.get("proposal", {}).get("stretch", []))
    stretch_done = actual.get("completed_stretch", 0)

    if unreliable:
        count = "UNRELIABLE"
    elif low is None or high is None or actual_n is None:
        count = "MISS"
    elif low <= actual_n <= high:
        count = "HIT"
    elif abs(actual_n - low) <= 1 or abs(actual_n - high) <= 1:
        count = "DIR-HIT"
    else:
        count = "MISS"

    binding_v = "HIT" if (binding_pred and binding_actual and binding_pred == binding_actual) else "MISS"

    row = (
        f"CAPACITY-VERDICT | date={date_str} | range={low}-{high} | actual={actual_n} | "
        f"count={count} | binding_pred={binding_pred} | binding_actual={binding_actual} | "
        f"binding={binding_v} | stretch={stretch_done}/{stretch_offered} | calc={calc_v} | rubric={rubric_v}"
    )
    return {
        "date": date_str, "range": [low, high], "actual": actual_n,
        "count": count, "binding_pred": binding_pred, "binding_actual": binding_actual,
        "binding": binding_v, "stretch_done": stretch_done, "stretch_offered": stretch_offered,
        "override_day": bool(actual.get("override_day")), "count_unreliable": unreliable,
        "capacity_verdict_row": row,
    }


# ── --gates (compute-only phase status) ──────────────────────────────────────

def _parse_kv_row(line: str) -> dict:
    d: dict = {}
    parts = [p.strip() for p in line.split("|")]
    if parts:
        d["_prefix"] = parts[0]
    for seg in parts[1:]:
        if "=" in seg:
            k, v = seg.split("=", 1)
            d[k.strip()] = v.strip()
    return d


def _grep_log_rows(vault_path: Path, prefix: str) -> list[dict]:
    rows: list[dict] = []
    logs_dir = vault_path / "Daily" / "logs"
    if not logs_dir.exists():
        return rows
    for fp in sorted(logs_dir.glob("*-log.md")):
        try:
            content = fp.read_text(encoding="utf-8")
        except OSError:
            continue
        for line in content.split("\n"):
            line = line.strip()
            if "|" in line and line.split("|", 1)[0].strip() == prefix:
                rows.append(_parse_kv_row(line))
    return rows


def _rows_in_window(rows: list[dict], ref_date: date, days: int) -> list[dict]:
    lo = ref_date - timedelta(days=days - 1)
    out = []
    for r in rows:
        try:
            rd = date.fromisoformat(r.get("date", ""))
        except ValueError:
            continue
        if lo <= rd <= ref_date:
            out.append(r)
    return out


def _is_float(s) -> bool:
    try:
        float(s)
        return True
    except (TypeError, ValueError):
        return False


def _acr_revert(acr_rows: list[dict], ref_date: date) -> bool:
    """ACR revert: mean(ACR-ROW.c) < agenda_revert_acr in any 7-day window ending
    within the last 14 days, WITH a reliable_days ≥ capacity_min_days_revert (=4)
    min-data guard (a 2-row window cannot trip a spurious revert). The all-windows
    outer scan latches the revert for up to 14 days after the bad rows age out —
    a stateless anti-flap cooldown (no stored revert timestamp)."""
    min_data = GATES_V1["capacity_min_days_revert"]
    for end_off in range(0, GATES_V1["window_days"]):
        end = ref_date - timedelta(days=end_off)
        win = _rows_in_window(acr_rows, end, GATES_V1["revert_window_days"])
        c_vals = [float(r["c"]) for r in win if _is_float(r.get("c"))]
        if len(c_vals) >= min_data and statistics.mean(c_vals) < GATES_V1["agenda_revert_acr"]:
            return True
    return False


def _bcr_revert(cv_rows: list[dict], ref_date: date) -> bool:
    """BCR revert: binding-HIT rate < capacity_bcr_revert in any 7-day window ending
    within the last 14 days, WITH a reliable_days ≥ capacity_min_days_revert (=4)
    min-data guard (the 0/4-reliable spurious-revert hazard). Same stateless anti-flap
    cooldown as _acr_revert — one breach latches revert for up to 14 days so a BCR
    oscillating in the 0.70–0.80 hysteresis band cannot flip the live branch on
    consecutive closes. UNRELIABLE rows are excluded from the window."""
    min_data = GATES_V1["capacity_min_days_revert"]
    for end_off in range(0, GATES_V1["window_days"]):
        end = ref_date - timedelta(days=end_off)
        win = [r for r in _rows_in_window(cv_rows, end, GATES_V1["revert_window_days"])
               if r.get("count") != "UNRELIABLE"]
        if len(win) >= min_data:
            hits = sum(1 for r in win if r.get("binding") == "HIT")
            if (hits / len(win)) < GATES_V1["capacity_bcr_revert"]:
                return True
    return False


def _parse_par_table(vault_path: Path) -> tuple[float | None, int | None, date | None]:
    """Last PAR value + session number + row date from the Accuracy Tracking table.

    Restricted to the `## Accuracy Tracking` section only: the ACR Tracking table
    (and other pipe tables) share a `| date | int | … |` column shape, so scanning
    the whole note would let a cross-table row pollute the PAR fallback. Also
    returns the last row's date so the caller can detect stale pre-gap data."""
    cal = vault_path / "Notes" / "pulse-priority-calibration.md"
    if not cal.exists():
        return None, None, None
    last_par = last_session = last_date = None
    in_section = False
    for line in cal.read_text(encoding="utf-8").split("\n"):
        stripped = line.strip()
        if stripped.startswith("## "):
            in_section = re.match(r"^##\s+Accuracy Tracking\b", stripped) is not None
            continue
        if not in_section:
            continue
        m = re.match(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(\d+)\s*\|\s*\d+\s*\|\s*([0-9.]+)\s*\|", line)
        if m:
            try:
                last_date = date.fromisoformat(m.group(1))
            except ValueError:
                last_date = None
            last_session = int(m.group(2))
            last_par = float(m.group(3))
    return last_par, last_session, last_date


def compute_gates(vault_path: Path, ref_date: date) -> dict:
    """Compute-only phase status vs GATES_V1 (public). No writes, no scheduling.

    THE graduation gate is compound and lives on the `capacity` block:
      capacity.gate_met = bcr≥0.80 AND rolling_acr≥0.60 AND median_edits≤3
                          AND reliable_days≥10.
    `agenda_composition` holds the ACR revert substrate; `priority_par` and
    `under_ambition` are calibration/health only and do NOT gate graduation.
    """
    acr_rows = _grep_log_rows(vault_path, "ACR-ROW")
    cv_rows = _grep_log_rows(vault_path, "CAPACITY-VERDICT")
    par_rows = _grep_log_rows(vault_path, "PAR-ROW")

    # ── Agenda composition (ACR revert substrate + the composition floor inputs) ──
    win = _rows_in_window(acr_rows, ref_date, GATES_V1["window_days"])
    edits = [int(r["edits"]) for r in win if str(r.get("edits", "")).isdigit()]
    agenda_days = len(win)
    median_edits = statistics.median(edits) if edits else None
    full_rej = sum(1 for r in win if r.get("rejected") == "yes" and r.get("override") != "yes")
    c_vals = [float(r["c"]) for r in win if _is_float(r.get("c"))]
    rolling_acr = round(statistics.mean(c_vals), 3) if c_vals else None
    agenda = {
        "rolling_acr": rolling_acr, "median_edits": median_edits, "agenda_days": agenda_days,
        "full_rejections_non_override": full_rej,
        "revert_triggered": _acr_revert(acr_rows, ref_date),
        "days_of_data": agenda_days,
        "status": "insufficient-data" if agenda_days < GATES_V1["capacity_min_days_graduate"] else "measuring",
    }

    # ── Capacity → BCR: THE graduation gate (compound, ACR-floored, min-data) ──
    cwin = [r for r in _rows_in_window(cv_rows, ref_date, GATES_V1["window_days"])
            if r.get("count") != "UNRELIABLE"]
    reliable_days = len(cwin)
    binding_hits = sum(1 for r in cwin if r.get("binding") == "HIT")
    bcr = round(binding_hits / reliable_days, 3) if reliable_days else None
    gate_met = bool(
        bcr is not None and bcr >= GATES_V1["capacity_bcr_target"]
        and rolling_acr is not None and rolling_acr >= GATES_V1["agenda_acr_floor"]
        and median_edits is not None and median_edits <= GATES_V1["agenda_edit_median_floor"]
        and reliable_days >= GATES_V1["capacity_min_days_graduate"]
    )
    if reliable_days < GATES_V1["capacity_min_days_graduate"]:
        cap_status = "insufficient-data"
    elif gate_met:
        cap_status = "graduatable"
    else:
        cap_status = "measuring"
    capacity = {
        "bcr": bcr, "reliable_days": reliable_days,
        "rolling_acr": rolling_acr, "median_edits": median_edits,
        "gate_met": gate_met,
        "revert_triggered": _bcr_revert(cv_rows, ref_date),
        "days_of_data": reliable_days,
        "status": cap_status,
    }

    # ── Priority PAR — CALIBRATION ONLY (does NOT gate graduation) ──
    pwin = _rows_in_window(par_rows, ref_date, GATES_V1["window_days"])
    par_stale = False
    if pwin:
        zero = sum(1 for r in pwin if str(r.get("corrections", "")).isdigit() and int(r["corrections"]) == 0)
        par = round(zero / len(pwin), 3)
        par_sessions = len(pwin)
        par_source = "PAR-ROW"
    else:
        par, par_sessions, par_date = _parse_par_table(vault_path)
        par_source = "accuracy-table-fallback"
        # Pre-gap fallback data older than the window is stale: report it but never
        # let it drive a revert signal.
        if par_date is not None and (ref_date - par_date).days > PAR_FALLBACK_MAX_AGE_DAYS:
            par_stale = True
            par_source = "accuracy-table-fallback-stale"
    if par_stale:
        priority = {
            "par": par, "sessions": par_sessions or 0, "par_source": par_source,
            "revert_triggered": False,  # stale pre-gap data must not signal a revert
            "days_of_data": par_sessions or 0,
            "status": "stale",
        }
    else:
        priority = {
            "par": par, "sessions": par_sessions or 0, "par_source": par_source,
            "revert_triggered": bool(par is not None and par < GATES_V1["priority_revert"]),
            "days_of_data": par_sessions or 0,
            "status": "insufficient-data" if (par_sessions or 0) < GATES_V1["priority_min_sessions"] else "measuring",
        }

    # ── Under-ambition tripwire — CALIBRATION/HEALTH ONLY (does NOT gate) ──
    # Exclude UNRELIABLE rows (same as BCR): a collapse-risk day's stretch outcome
    # is not a trustworthy under-ambition signal.
    uwin = [r for r in _rows_in_window(cv_rows, ref_date, GATES_V1["window_days"])
            if r.get("count") != "UNRELIABLE"]
    stretch_days = 0
    s_total = k_total = 0
    for r in uwin:
        sk = str(r.get("stretch", ""))
        if "/" in sk:
            s_str, k_str = sk.split("/", 1)
            if s_str.isdigit() and k_str.isdigit() and int(k_str) > 0:
                stretch_days += 1
                s_total += int(s_str)
                k_total += int(k_str)
    stretch_rate = round(s_total / k_total, 3) if k_total else None
    tripwire = bool(stretch_rate is not None
                    and stretch_rate >= GATES_V1["under_ambition_stretch_rate"]
                    and stretch_days >= GATES_V1["under_ambition_min_days"])
    under_ambition = {
        "stretch_rate": stretch_rate, "stretch_offered_days": stretch_days,
        "tripwire": tripwire,
        "flag": "widen sizing" if tripwire else None,
        "status": "insufficient-data" if stretch_days < GATES_V1["under_ambition_min_days"] else "measuring",
    }

    return {
        "computed_at": datetime.now().isoformat(timespec="seconds"),
        "reference_date": ref_date.isoformat(),
        "gates_version": "GATES_V1_PUBLIC",
        "capacity": capacity,
        "agenda_composition": agenda,
        "priority_par": priority,
        "under_ambition": under_ambition,
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
    # Stage B / capacity-proposer flags
    parser.add_argument("--capacity-input",
                        help="Graded capacity JSON (path or inline) → Stage-B budget vector")
    parser.add_argument("--propose", action="store_true",
                        help="Emit layered agenda proposal (deadline/floor/core/stretch/slack)")
    parser.add_argument("--propose-out",
                        help="Override path for the proposal artifact (default: Daily/cache/DATE-proposal.json)")
    parser.add_argument("--verdict", action="store_true",
                        help="Mechanical capacity verdict from a frozen proposal + --actual")
    parser.add_argument("--actual", help="JSON actuals for --verdict")
    parser.add_argument("--gates", action="store_true",
                        help="Compute-only phase/gate status (GATES_V1_PUBLIC); no writes, no scheduling")
    parser.add_argument("--candidates", action="store_true",
                        help="Emit the gradeable candidate pool (deadline + floor + top-ranked) "
                             "with exact item ids; read-only")
    args = parser.parse_args()

    # Vault path resolution: --vault flag > $PULSE_VAULT env var > ./pulse-vault default
    raw_vault = args.vault or os.environ.get("PULSE_VAULT") or "./pulse-vault"
    vault_path = Path(raw_vault).resolve()

    today = date.fromisoformat(args.date) if args.date else date.today()

    # ── --verdict: pure function over two JSON blobs (bypasses vault loading) ──
    if args.verdict:
        prop_path = (Path(args.propose_out) if args.propose_out
                     else vault_path / "Daily" / "cache" / f"{today.isoformat()}-proposal.json")
        if not prop_path.exists():
            print(json.dumps({"skipped": "no frozen proposal artifact", "path": str(prop_path)}, indent=2))
            return
        try:
            proposal = json.loads(prop_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(json.dumps({"error": f"malformed proposal JSON: {e}", "path": str(prop_path)}, indent=2))
            return
        try:
            actual = json.loads(args.actual) if args.actual else {}
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"malformed --actual JSON: {e}", "arg": args.actual}, indent=2))
            return
        print(json.dumps(compute_verdict(proposal, actual, today), indent=2))
        return

    # ── --gates: compute-only phase status (reads calibration + daily logs) ──
    if args.gates:
        if args.propose or args.capacity_input:
            print(json.dumps({"error": "--gates is standalone"}, indent=2))
            return
        print(json.dumps(compute_gates(vault_path, today), indent=2))
        return

    cal_offsets: dict[str, float] = {}
    if args.calibration_offsets:
        try:
            cal_offsets = json.loads(args.calibration_offsets)
        except json.JSONDecodeError:
            print("Warning: could not parse --calibration-offsets", file=sys.stderr)

    all_warnings: list[dict] = []

    # Parse graded capacity input up-front (shared by capacity-input + propose paths).
    graded: dict = {}
    if args.capacity_input:
        graded, graded_warnings = parse_graded_input(args.capacity_input)
        all_warnings.extend(graded_warnings)
        rv = graded.get("rubric_version")
        if rv is not None and rv not in KNOWN_RUBRIC_VERSIONS:
            all_warnings.append({"type": "rubric_version_mismatch", "detail": f"unknown rubric_version {rv!r}"})

    # ── --capacity-input WITHOUT --propose: standalone Stage-B over the graded pool ──
    if args.capacity_input and not args.propose:
        if not (graded.get("sleep") or {}):
            print(json.dumps({"skipped": "no sleep input"}, indent=2))
            return
        result = compute_capacity(graded, graded.get("items", []), today)
        if result is None:
            print(json.dumps({"skipped": "no sleep input"}, indent=2))
            return
        print(json.dumps(to_serializable(result), indent=2))
        return

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

    # ── --candidates: emit the gradeable candidate pool (read-only, no writes) ──
    if args.candidates:
        floor_path = vault_path / "Templates" / "routine-floor.md"
        floor_items, floor_warnings = parse_routine_floor(floor_path, today.weekday())
        all_warnings.extend(floor_warnings)
        deadline_items = collect_deadline_items(active_notes, maps, today)
        candidates = build_candidate_pool(important_items, floor_items, deadline_items)
        print(json.dumps({
            "reference_date": today.isoformat(),
            "candidates": candidates,
            "warnings": all_warnings,
        }, indent=2))
        return

    # ── --propose: layered agenda draft (deadline/floor/core/stretch/slack) ──
    if args.propose:
        floor_path = vault_path / "Templates" / "routine-floor.md"
        floor_items, floor_warnings = parse_routine_floor(floor_path, today.weekday())
        all_warnings.extend(floor_warnings)
        deadline_items = collect_deadline_items(active_notes, maps, today)
        proposal = build_proposal(
            important_items, deadline_items, floor_items,
            graded if graded else None, today, vault_path,
        )
        if all_warnings:
            proposal["warnings"] = all_warnings
        out_path = (Path(args.propose_out) if args.propose_out
                    else vault_path / "Daily" / "cache" / f"{today.isoformat()}-proposal.json")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(proposal, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(proposal, indent=2))
        return

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
