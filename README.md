# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## ✨ Features

- **Owner & pet management** — add an owner and multiple pets, each with their own independent task list.
- **Task creation** — add care tasks with a title, duration, priority, category, and an optional fixed time of day.
- **Sorting by time** — `Scheduler.sort_by_time()` orders tasks chronologically by fixed time, with unscheduled tasks listed last.
- **Filtering** — `Scheduler.filter_tasks()` narrows the task list by pet and/or completion status, both in the CLI demo and the Streamlit UI.
- **Conflict warnings** — `Scheduler.detect_conflicts()` flags any tasks (same or different pets) scheduled at the exact same fixed time, shown as `st.warning` banners in the UI instead of crashing the app.
- **Daily/weekly recurrence** — marking a recurring task complete (`Pet.complete_task()` / `Task.mark_complete()`) automatically creates its next occurrence, due one day (or one week) later.
- **Explainable daily plan** — `Scheduler.build_plan()` builds a time-budgeted schedule ordered by fixed time then priority, and `Scheduler.explain()` describes why each task landed where it did.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

The final UML, matching the implementation in `pawpal_system.py`, lives at [diagrams/uml_final.mmd](diagrams/uml_final.mmd) (the earlier draft is kept at `diagrams/uml.mmd` for history).

## 🖥️ Sample Output

Output from running `python main.py`:

```
All tasks sorted by time:

  [08:00] Morning feeding
  [08:00] Morning walk
  [unscheduled] Litter box cleaning
  [unscheduled] Playtime
  [unscheduled] Give medication

Pending tasks for Mochi:

  Litter box cleaning
  Morning feeding

Conflict check:

  WARNING: Conflict at 08:00 — Mochi: Morning feeding, Biscuit: Morning walk

Completing Mochi's recurring feeding task...

  Created next occurrence: Morning feeding due 2026-07-08

Today's Schedule for Jordan's pets:

  08:00 - 08:10  [Mochi] Morning feeding (10 min, high priority)
      reason: Scheduled at its fixed time (08:00).
  08:00 - 08:30  [Biscuit] Morning walk (30 min, high priority)
      reason: Scheduled at its fixed time (08:00).
  08:30 - 08:35  [Biscuit] Give medication (5 min, high priority)
      reason: Ordered by high priority among remaining tasks.
  08:35 - 08:40  [Mochi] Litter box cleaning (5 min, medium priority)
      reason: Ordered by medium priority among remaining tasks.
  08:40 - 09:00  [Biscuit] Playtime (20 min, low priority)
      reason: Ordered by low priority among remaining tasks.

Explanation:

08:00 - Mochi: Morning feeding (10 min, high priority) — Scheduled at its fixed time (08:00).
08:00 - Biscuit: Morning walk (30 min, high priority) — Scheduled at its fixed time (08:00).
08:30 - Biscuit: Give medication (5 min, high priority) — Ordered by high priority among remaining tasks.
08:35 - Mochi: Litter box cleaning (5 min, medium priority) — Ordered by medium priority among remaining tasks.
08:40 - Biscuit: Playtime (20 min, low priority) — Ordered by low priority among remaining tasks.
```

Note: `main.py` deliberately schedules Mochi's feeding and Biscuit's walk at the same 08:00 fixed time to demonstrate conflict detection — `build_plan()` still places both (see the exact-match tradeoff in `reflection.md`, section 2b), but `detect_conflicts()` surfaces the warning above the schedule so the owner can resolve it.

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

The suite in `tests/test_pawpal.py` (16 tests) covers:

- **Task completion**: `mark_complete()` flips `completed`, and adding a task increases a pet's task count.
- **Sorting**: `sort_by_time()` orders fixed-time tasks chronologically, puts unscheduled tasks last, and is stable when two tasks share a time.
- **Filtering**: `filter_tasks()` by pet name, by completion status, and by both together.
- **Conflict detection**: `detect_conflicts()` flags two tasks (same or different pets) at the same `fixed_time`, ignores distinct times, and returns no warnings when no tasks have a fixed time.
- **Recurring tasks**: completing a `daily` task creates a next occurrence due `+1 day`; completing a `weekly` task advances `+7 days`; completing a non-recurring task creates no next occurrence; `Pet.complete_task()` adds the new occurrence to the pet's task list.
- **Scheduling edge cases**: an owner with no pets, and a pet with no tasks, both produce an empty plan without errors; `build_plan()` respects the available-minutes budget and skips already-completed tasks.

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/.../pawpal-starter
collected 16 items

tests/test_pawpal.py ................                                    [100%]

============================== 16 passed in 0.01s ==============================
```

**Confidence Level:** ⭐⭐⭐⭐☆ (4/5) — core scheduling, sorting, filtering, and recurrence logic are well covered and passing. The main known gap is that conflict detection only catches exact-time matches, not true duration overlaps (see `reflection.md`, section 2b), so it's not yet a full guarantee against double-booking.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks by `fixed_time` ("HH:MM"); tasks with no fixed time sort last. |
| Filtering | `Scheduler.filter_tasks()` | Filters an owner's tasks by `pet_name` and/or `completed` status. |
| Time-budget filtering | `Scheduler.build_plan()` | Skips a candidate task once it no longer fits in the remaining available minutes. |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags tasks (same or different pets) that share the same exact `fixed_time`; returns warning strings instead of raising. See reflection.md 2b for the exact-match vs. overlap tradeoff. |
| Recurring tasks | `Task.mark_complete()`, `Task.next_occurrence()`, `Pet.complete_task()` | Completing a `daily`/`weekly` task automatically creates and adds its next occurrence, due one cycle later (via `timedelta`). |

## 📸 Demo Walkthrough

**Main UI features and actions**

- Enter an owner name at the top of the page; it's kept in `st.session_state` so it persists across interactions.
- Add one or more pets (name + species) through the "Add pet" form.
- Add care tasks to a chosen pet (title, duration, priority, category, and an optional fixed time) through the "Add task" form.
- Filter and sort the current task table by pet and/or completion status.
- Mark a pending task complete from the "Mark a task complete" expander — if it's recurring, the next occurrence is created automatically and a success message reports its due date.
- Any tasks sharing the same fixed time are flagged as warnings above the schedule section, before you even click "Generate schedule."
- Set the available minutes for the day and click "Generate schedule" to see the ordered plan with a reasoning explanation.

**Example workflow**

1. Add pet "Mochi" (cat) and pet "Biscuit" (dog).
2. Add a task "Morning feeding" for Mochi at a fixed time of 08:00, marked as daily recurring.
3. Add a task "Morning walk" for Biscuit, also fixed at 08:00 — the app immediately shows a conflict warning ("Conflict at 08:00 — Mochi: Morning feeding, Biscuit: Morning walk").
4. Add a couple more untimed tasks (e.g. "Playtime", "Give medication") with different priorities.
5. Set available minutes (e.g. 90) and click "Generate schedule" — fixed-time tasks appear first in the plan, followed by the remaining tasks ordered by priority, each with a one-line reason.
6. Mark "Morning feeding" complete — a new "Morning feeding" task is added automatically, due the next day.

**Key Scheduler behaviors shown**: fixed-time sorting, priority-based ordering of untimed tasks, time-budget enforcement (tasks that don't fit are skipped), conflict detection on duplicate fixed times, and daily recurrence on task completion.

**Sample CLI output** (from `python main.py`, exercising sorting, filtering, conflict detection, and recurrence together):

```
All tasks sorted by time:

  [08:00] Morning feeding
  [08:00] Morning walk
  [unscheduled] Litter box cleaning
  [unscheduled] Playtime
  [unscheduled] Give medication

Pending tasks for Mochi:

  Litter box cleaning
  Morning feeding

Conflict check:

  WARNING: Conflict at 08:00 — Mochi: Morning feeding, Biscuit: Morning walk

Completing Mochi's recurring feeding task...

  Created next occurrence: Morning feeding due 2026-07-08

Today's Schedule for Jordan's pets:

  08:00 - 08:10  [Mochi] Morning feeding (10 min, high priority)
      reason: Scheduled at its fixed time (08:00).
  08:00 - 08:30  [Biscuit] Morning walk (30 min, high priority)
      reason: Scheduled at its fixed time (08:00).
  08:30 - 08:35  [Biscuit] Give medication (5 min, high priority)
      reason: Ordered by high priority among remaining tasks.
  08:35 - 08:40  [Mochi] Litter box cleaning (5 min, medium priority)
      reason: Ordered by medium priority among remaining tasks.
  08:40 - 09:00  [Biscuit] Playtime (20 min, low priority)
      reason: Ordered by low priority among remaining tasks.

Explanation:

08:00 - Mochi: Morning feeding (10 min, high priority) — Scheduled at its fixed time (08:00).
08:00 - Biscuit: Morning walk (30 min, high priority) — Scheduled at its fixed time (08:00).
08:30 - Biscuit: Give medication (5 min, high priority) — Ordered by high priority among remaining tasks.
08:35 - Mochi: Litter box cleaning (5 min, medium priority) — Ordered by medium priority among remaining tasks.
08:40 - Biscuit: Playtime (20 min, low priority) — Ordered by low priority among remaining tasks.
```

**Screenshot or video** *(optional)*: not included — the text walkthrough and CLI output above are the primary demo evidence.
