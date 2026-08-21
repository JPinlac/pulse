# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
Gate-semantics self-test for the public PULSE capacity proposer.

This fixture PINS the semantics of the most-rebindable pieces of the
graduation gate so a future edit to `pulse-calc.py` cannot silently loosen
them without a red test. It is not a coverage suite — it is a set of
tripwires on the exact predicates the dyad ratified (plan item 9):

  * Graduation is the COMPOUND predicate
        bcr >= 0.80  AND  rolling_acr >= 0.60
        AND  median_edits <= 3  AND  reliable_days >= 10
    Dropping ANY one below threshold must block graduation (four negatives).
  * A first-window 3/3 BCR on <10 reliable days is `insufficient-data`,
    NOT a graduation.
  * Revert watches BOTH substrates: a BCR dip <0.70 and (separately) an
    ACR dip <0.60 each withdraw graduation.
  * The revert min-data guard (reliable_days >= 4) blocks the 07-09
    spurious-revert hazard: a single MISS in a 2-row window must NOT revert.
  * The deadline/due layer is LIVE — it goes non-empty the moment a
    committed item carries an in-horizon due date.

Run:  uv run scripts/test_capacity_gates.py
      (plain `python3` works only if pyyaml is already importable; the
       target module does `import yaml` at load time.)

Built against the real functions in ../pulse-calc.py and the as-built keys
(gates["capacity"][...] / capacity.revert_triggered /
 agenda_composition.revert_triggered).
"""

import importlib.util
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent / "pulse-calc.py"
REF = date(2026, 7, 15)  # fixed reference date; all windows anchor here


# ── module loader (target has a hyphen → import by path) ─────────────────────
def load_module():
    spec = importlib.util.spec_from_file_location("pulse_calc", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PC = load_module()


# ── tiny assertion harness (no pytest dependency) ────────────────────────────
FAILURES: list[str] = []


def check(cond: bool, msg: str) -> None:
    print(f"  {'PASS' if cond else 'FAIL'}: {msg}")
    if not cond:
        FAILURES.append(msg)


def section(title: str) -> None:
    print(f"\n== {title} ==")


# ── log-row / vault builders ─────────────────────────────────────────────────
def days_back(n: int) -> list[str]:
    """N ISO dates ending at REF (offsets 0..n-1), all inside the 14-day window."""
    return [(REF - timedelta(days=i)).isoformat() for i in range(n)]


def cv_row(dt: str, binding: str, count: str = "HIT", stretch: str = "0/0") -> str:
    # compute_gates binds to date, count, binding (UNRELIABLE count excluded).
    return f"CAPACITY-VERDICT | date={dt} | count={count} | binding={binding} | stretch={stretch}"


def acr_row(dt: str, c, edits, rejected: str = "no", override: str = "no") -> str:
    # compute_gates binds to date, c, edits, rejected, override.
    return f"ACR-ROW | date={dt} | c={c} | edits={edits} | rejected={rejected} | override={override}"


def make_vault(rows: list[str]) -> Path:
    """A throwaway vault whose only content is a session log holding `rows`."""
    d = Path(tempfile.mkdtemp(prefix="pulse-gate-test-"))
    logs = d / "Daily" / "logs"
    logs.mkdir(parents=True)
    (logs / "2026-07-15-log.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    return d


def gates_for(cv: list[str], acr: list[str]) -> dict:
    return PC.compute_gates(make_vault(cv + acr), REF)


# Reusable passing substrates for isolating single-condition negatives.
def hit_cv(n: int) -> list[str]:
    return [cv_row(dt, "HIT") for dt in days_back(n)]


def clean_acr(n: int, c="0.90", edits=1) -> list[str]:
    return [acr_row(dt, c, edits) for dt in days_back(n)]


# ─────────────────────────────────────────────────────────────────────────────
def test_threshold_constants():
    section("GATES_V1 threshold constants are the ratified values")
    g = PC.GATES_V1
    check(g["capacity_bcr_target"] == 0.80, "capacity_bcr_target == 0.80")
    check(g["capacity_bcr_revert"] == 0.70, "capacity_bcr_revert == 0.70")
    check(g["capacity_min_days_graduate"] == 10, "capacity_min_days_graduate == 10")
    check(g["capacity_min_days_revert"] == 4, "capacity_min_days_revert == 4")
    check(g["agenda_acr_floor"] == 0.60, "agenda_acr_floor == 0.60")
    check(g["agenda_edit_median_floor"] == 3, "agenda_edit_median_floor == 3")
    check(g["agenda_revert_acr"] == 0.60, "agenda_revert_acr == 0.60")


def test_graduation_positive():
    section("Compound gate: all four conditions met → graduates")
    g = gates_for(hit_cv(10), clean_acr(10))["capacity"]
    check(g["bcr"] is not None and g["bcr"] >= 0.80, f"bcr {g['bcr']} >= 0.80")
    check(g["rolling_acr"] is not None and g["rolling_acr"] >= 0.60,
          f"rolling_acr {g['rolling_acr']} >= 0.60")
    check(g["median_edits"] is not None and g["median_edits"] <= 3,
          f"median_edits {g['median_edits']} <= 3")
    check(g["reliable_days"] >= 10, f"reliable_days {g['reliable_days']} >= 10")
    check(g["gate_met"] is True, "gate_met is True")
    check(g["status"] == "graduatable", f"status == 'graduatable' (got {g['status']})")


def test_negative_bcr_below():
    section("Negative 1: BCR below 0.80 blocks graduation (everything else passes)")
    # 7 HIT + 3 MISS over 10 reliable days → bcr 0.70 < 0.80.
    cv = [cv_row(dt, "HIT") for dt in days_back(7)] + \
         [cv_row(dt, "MISS", count="MISS") for dt in days_back(10)[7:]]
    g = gates_for(cv, clean_acr(10))["capacity"]
    check(g["reliable_days"] == 10, f"reliable_days == 10 (got {g['reliable_days']})")
    check(g["bcr"] is not None and g["bcr"] < 0.80, f"bcr {g['bcr']} < 0.80")
    check(g["rolling_acr"] >= 0.60 and g["median_edits"] <= 3,
          "acr/edits floor still satisfied (isolation)")
    check(g["gate_met"] is False, "gate_met is False — BCR is a necessary condition")


def test_negative_acr_below():
    section("Negative 2: rolling_acr below 0.60 blocks graduation")
    # bcr 1.0, reliable_days 10, edits fine — only ACR coverage fails (c=0.50).
    g = gates_for(hit_cv(10), clean_acr(10, c="0.50"))["capacity"]
    check(g["bcr"] >= 0.80 and g["reliable_days"] >= 10, "bcr/min-days still satisfied (isolation)")
    check(g["median_edits"] <= 3, "median_edits still satisfied (isolation)")
    check(g["rolling_acr"] is not None and g["rolling_acr"] < 0.60,
          f"rolling_acr {g['rolling_acr']} < 0.60")
    check(g["gate_met"] is False, "gate_met is False — ACR floor is a necessary condition")


def test_negative_edits_above():
    section("Negative 3: median_edits above 3 blocks graduation")
    # bcr 1.0, acr 0.90, reliable_days 10 — only edit-churn fails (edits=5).
    g = gates_for(hit_cv(10), clean_acr(10, edits=5))["capacity"]
    check(g["bcr"] >= 0.80 and g["reliable_days"] >= 10, "bcr/min-days still satisfied (isolation)")
    check(g["rolling_acr"] >= 0.60, "acr floor still satisfied (isolation)")
    check(g["median_edits"] is not None and g["median_edits"] > 3,
          f"median_edits {g['median_edits']} > 3")
    check(g["gate_met"] is False, "gate_met is False — edit-median floor is a necessary condition")


def test_negative_reliable_days_below():
    section("Negative 4: reliable_days below 10 blocks graduation")
    # bcr 1.0, acr fine — only 9 reliable days.
    g = gates_for(hit_cv(9), clean_acr(9))["capacity"]
    check(g["bcr"] >= 0.80, "bcr still satisfied (isolation)")
    check(g["rolling_acr"] >= 0.60 and g["median_edits"] <= 3, "acr/edits still satisfied (isolation)")
    check(g["reliable_days"] == 9, f"reliable_days == 9 (< 10)")
    check(g["gate_met"] is False, "gate_met is False — min-data is a necessary condition")
    check(g["status"] == "insufficient-data",
          f"status == 'insufficient-data' (got {g['status']})")


def test_first_window_three_of_three():
    section("First-window 3/3 BCR on <10 reliable days → insufficient-data, not graduation")
    g = gates_for(hit_cv(3), clean_acr(3))["capacity"]
    check(g["bcr"] == 1.0, f"bcr == 1.0 (3/3, got {g['bcr']})")
    check(g["reliable_days"] == 3, "reliable_days == 3")
    check(g["gate_met"] is False, "gate_met is False despite perfect BCR")
    check(g["status"] == "insufficient-data",
          f"status == 'insufficient-data' (got {g['status']})")


def test_revert_bcr_dip():
    section("Revert substrate A: a BCR dip < 0.70 withdraws graduation")
    # 5 rows in the last 7 days, HIT-rate 0.20 (1 HIT / 4 MISS), len >= 4.
    dts = days_back(5)
    cv = [cv_row(dts[0], "HIT")] + [cv_row(d, "MISS", count="MISS") for d in dts[1:]]
    caps = gates_for(cv, [])
    check(caps["capacity"]["revert_triggered"] is True,
          "capacity.revert_triggered is True on a <0.70 BCR window")


def test_revert_acr_dip():
    section("Revert substrate B: an ACR dip < 0.60 withdraws graduation")
    # 5 ACR rows in the last 7 days, mean c 0.40 < 0.60, len >= 4.
    acr = [acr_row(d, "0.40", 1) for d in days_back(5)]
    caps = gates_for([], acr)
    check(caps["agenda_composition"]["revert_triggered"] is True,
          "agenda_composition.revert_triggered is True on a <0.60 ACR window")


def test_revert_min_data_guard():
    section("Revert min-data guard (07-09 hazard): <4 reliable rows must NOT revert")
    # Two rows only, 1 HIT + 1 MISS → 0.50 HIT-rate but len 2 < 4 → NO revert.
    dts = days_back(2)
    cv2 = [cv_row(dts[0], "HIT"), cv_row(dts[1], "MISS", count="MISS")]
    g2 = gates_for(cv2, [])
    check(g2["capacity"]["reliable_days"] == 2, "2 reliable rows in window")
    check(g2["capacity"]["revert_triggered"] is False,
          "capacity.revert_triggered is False — 1 MISS in a 2-row window does NOT trip (min-data guard)")
    # Contrast: exactly 4 reliable rows below 0.70 DOES revert (guard is a floor, not an off-switch).
    cv4 = [cv_row(d, "MISS", count="MISS") for d in days_back(4)]
    g4 = gates_for(cv4, [])
    check(g4["capacity"]["reliable_days"] == 4, "4 reliable rows in window")
    check(g4["capacity"]["revert_triggered"] is True,
          "capacity.revert_triggered is True at 4 reliable rows (guard boundary)")


def test_deadline_layer_is_live():
    section("Deadline/due layer is LIVE — non-empty the moment an item carries a due date")
    check(PC.DEADLINE_DUE_HORIZON == 1, "DEADLINE_DUE_HORIZON == 1")
    note_due = PC.NoteData(
        slug="ship-release", efforts=["work"], status="active",
        importance="high", due=REF, updated=REF, timescale=None,
    )
    got = PC.collect_deadline_items([note_due], [], REF)
    check(len(got) == 1, f"one in-horizon due item surfaces (got {len(got)})")
    check(got and got[0]["id"] == "work::note::ship-release",
          "deadline item id shape preserved (effort::note::slug)")
    check(got and got[0]["due"] == REF.isoformat(), "due date carried on the entry")

    note_no_due = PC.NoteData(
        slug="ship-release", efforts=["work"], status="active",
        importance="high", due=None, updated=REF, timescale=None,
    )
    check(PC.collect_deadline_items([note_no_due], [], REF) == [],
          "same item with NO due date → deadline layer empty (layer is driven by the date)")

    note_far = PC.NoteData(
        slug="later-thing", efforts=["work"], status="active",
        importance="high", due=REF + timedelta(days=2), updated=REF, timescale=None,
    )
    check(PC.collect_deadline_items([note_far], [], REF) == [],
          "due beyond horizon (ref+2) → excluded (horizon is exactly ref+1)")

    # And it feeds the candidate pool as a live 'deadline' layer.
    pool = PC.build_candidate_pool([], [], PC.collect_deadline_items([note_due], [], REF))
    check(any(p.get("layer_hint") == "deadline" for p in pool),
          "candidate pool carries a live 'deadline' layer_hint")


def main():
    for t in (
        test_threshold_constants,
        test_graduation_positive,
        test_negative_bcr_below,
        test_negative_acr_below,
        test_negative_edits_above,
        test_negative_reliable_days_below,
        test_first_window_three_of_three,
        test_revert_bcr_dip,
        test_revert_acr_dip,
        test_revert_min_data_guard,
        test_deadline_layer_is_live,
    ):
        t()
    print("\n" + "=" * 60)
    if FAILURES:
        print(f"FAILED — {len(FAILURES)} assertion(s) failed:")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    print("ALL GATE-SEMANTICS ASSERTIONS PASSED")
    sys.exit(0)


if __name__ == "__main__":
    main()
