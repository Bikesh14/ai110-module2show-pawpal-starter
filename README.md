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

## 🖥️ Sample Output

Output from running `python main.py`:

```
Today's Schedule for Jordan's pets:

  08:00 - 08:10  [Mochi] Morning feeding (10 min, high priority)
      reason: Scheduled at its fixed time (08:00).
  08:30 - 09:00  [Biscuit] Morning walk (30 min, high priority)
      reason: Scheduled at its fixed time (08:30).
  09:00 - 09:05  [Biscuit] Give medication (5 min, high priority)
      reason: Ordered by high priority among remaining tasks.
  09:05 - 09:10  [Mochi] Litter box cleaning (5 min, medium priority)
      reason: Ordered by medium priority among remaining tasks.
  09:10 - 09:30  [Biscuit] Playtime (20 min, low priority)
      reason: Ordered by low priority among remaining tasks.

Explanation:

08:00 - Mochi: Morning feeding (10 min, high priority) — Scheduled at its fixed time (08:00).
08:30 - Biscuit: Morning walk (30 min, high priority) — Scheduled at its fixed time (08:30).
09:00 - Biscuit: Give medication (5 min, high priority) — Ordered by high priority among remaining tasks.
09:05 - Mochi: Litter box cleaning (5 min, medium priority) — Ordered by medium priority among remaining tasks.
09:10 - Biscuit: Playtime (20 min, low priority) — Ordered by low priority among remaining tasks.
```

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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
