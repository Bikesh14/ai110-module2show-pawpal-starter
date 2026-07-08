# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a pet owner plan care tasks for their pet(s) — tracking walks, feeding, meds, and grooming, and generating a daily schedule based on time, priority, and conflicts.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running it

```bash
# Interactive app (add pets/tasks, generate a schedule):
streamlit run app.py

# CLI demo with hardcoded sample data (proves the backend logic works):
python main.py

# Test suite:
python -m pytest
```

## Features

- **Owner & pets** — add an owner and multiple pets, each with an independent task list.
- **Tasks** — title, duration, priority, category, and an optional fixed time of day.
- **Sorting** — by time (`Scheduler.sort_by_time`) or by priority (`Scheduler.sort_by_priority`).
- **Filtering** — by pet and/or completion status (`Scheduler.filter_tasks`).
- **Conflict warnings** — flags tasks scheduled at the same fixed time (`Scheduler.detect_conflicts`), shown in the UI instead of crashing.
- **Recurring tasks** — completing a daily/weekly task auto-creates its next occurrence (`Task.mark_complete`, `Pet.complete_task`).
- **Daily plan + explanation** — builds a time-budgeted schedule and explains why each task landed where it did (`Scheduler.build_plan`, `Scheduler.explain`).
- **Next available slot** — finds the earliest open gap of a given length (`Scheduler.find_next_available_slot`).
- **Save/load** — persist an owner's pets and tasks to `data.json` (`Owner.save_to_json` / `Owner.load_from_json`).

## System design

The final UML (matching `pawpal_system.py`) is at [diagrams/uml_final.mmd](diagrams/uml_final.mmd); the earlier draft is kept at `diagrams/uml.mmd` for history. Design decisions and tradeoffs are documented in `reflection.md`.

Classes: `Owner` (manages pets, save/load), `Pet` (holds tasks), `Task` (description, duration, priority, fixed time, recurrence, completion), `Scheduler` (retrieves and organizes tasks across all of an owner's pets).

## Stretch features

Beyond the core requirements, four optional extensions are implemented (see `ai_interactions.md` for the AI agent workflow used to build them):

**1. Advanced algorithm — next available slot** (`Scheduler.find_next_available_slot`)

```
>>> scheduler.find_next_available_slot(owner, duration_minutes=15)
08:30
```

Scans existing fixed-time tasks and returns the earliest open gap long enough for a new task, or `None` if the day is full.

**2. Data persistence** (`Owner.save_to_json` / `Owner.load_from_json`)

Saves the owner, all pets, and all tasks to a JSON file (default `data.json`, gitignored as generated data). `time`/`date` fields are converted to ISO strings on save and parsed back on load. In the Streamlit app, the "💾 Save to data.json" and "📂 Load from data.json" buttons write/read this file so a session's pets and tasks can be restored on a later run.

**3. Advanced priority scheduling** (`Scheduler.sort_by_priority`)

```
=== Sorted by time ===        === Sorted by priority ===
08:00  Morning feeding (high)  08:00  Morning feeding (high)
08:00  Morning walk (high)     08:00  Morning walk (high)
—      Litter box (medium)     —      Give medication (high)
—      Playtime (low)          —      Litter box (medium)
—      Give medication (high)  —      Playtime (low)
```

Sorts tasks by priority first (high → medium → low), then by fixed time — complements `sort_by_time()`, which sorts time-first.

**4. Professional output formatting**

`main.py` renders tables with the `tabulate` library plus category emojis (🍽️ feeding, 🚶 walk, 💊 meds, 🧼 grooming, 🧸 enrichment) and status indicators (✅ done / ⏳ pending) instead of plain `print()` lines — see Sample output below.

## Sample output

Output from `python main.py`:

```
=== 📋 All Tasks (sorted by time) ===

| Pet     | Task                  | Time   | Duration   | Priority   | Status    |
|---------|-----------------------|--------|------------|------------|-----------|
| Mochi   | 🍽️ Morning feeding    | 08:00  | 10 min     | high       | ⏳ pending |
| Biscuit | 🚶 Morning walk        | 08:00  | 30 min     | high       | ⏳ pending |
| Mochi   | 🧼 Litter box cleaning | —      | 5 min      | medium     | ⏳ pending |
| Biscuit | 🧸 Playtime            | —      | 20 min     | low        | ⏳ pending |
| Biscuit | 💊 Give medication     | —      | 5 min      | high       | ⏳ pending |

=== ⚠️  Conflict Check ===

  ⚠️  Conflict at 08:00 — Mochi: Morning feeding, Biscuit: Morning walk

=== 📅 Today's Schedule for Jordan's Pets ===

| Time        | Pet     | Task                  | Priority   | Reason                                            |
|-------------|---------|-----------------------|------------|---------------------------------------------------|
| 08:00-08:10 | Mochi   | 🍽️ Morning feeding    | high       | Scheduled at its fixed time (08:00).              |
| 08:00-08:30 | Biscuit | 🚶 Morning walk        | high       | Scheduled at its fixed time (08:00).              |
| 08:30-08:35 | Biscuit | 💊 Give medication     | high       | Ordered by high priority among remaining tasks.   |
| 08:35-08:40 | Mochi   | 🧼 Litter box cleaning | medium     | Ordered by medium priority among remaining tasks. |
| 08:40-09:00 | Biscuit | 🧸 Playtime            | low        | Ordered by low priority among remaining tasks.    |
```

`main.py` deliberately puts Mochi's feeding and Biscuit's walk at the same 08:00 fixed time to demonstrate conflict detection — `build_plan()` still schedules both (conflict detection only catches exact-time matches, not overlapping durations; see `reflection.md` 2b), but the warning is surfaced so the owner can resolve it.

Full CLI output — including priority sorting, per-pet filtering, next-available-slot, recurrence, and save/load — is longer than shown here; run `python main.py` to see all of it.

## Testing

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/bbimali1/Desktop/Codepath_projects/ai110-module2show-pawpal-starter
collected 21 items

tests/test_pawpal.py .....................                               [100%]

============================== 21 passed in 0.01s ==============================
```

21 tests in `tests/test_pawpal.py` cover task completion, sorting (by time and by priority), filtering, conflict detection, recurrence (daily/weekly), scheduling edge cases (no pets, no tasks, time-budget limits), the next-available-slot search, and JSON save/load round-tripping.

**Confidence:** ⭐⭐⭐⭐☆ (4/5) — core behaviors are well covered. The main known gap is that conflict detection only catches exact-time matches, not true duration overlap (see `reflection.md` 2b).

## Demo walkthrough

1. Add pets "Mochi" (cat) and "Biscuit" (dog).
2. Add "Morning feeding" for Mochi, fixed at 08:00, marked daily recurring.
3. Add "Morning walk" for Biscuit, also fixed at 08:00 — the app immediately shows a conflict warning.
4. Add a couple of untimed tasks (e.g. "Playtime", "Give medication") with different priorities.
5. Set available minutes (e.g. 90) and click "Generate schedule" — fixed-time tasks go first, then the rest ordered by priority, each with a one-line reason.
6. Mark "Morning feeding" complete — its next occurrence is created automatically, due the next day.

*Screenshot or video (optional): not included — the walkthrough and CLI output above are the demo evidence.*
