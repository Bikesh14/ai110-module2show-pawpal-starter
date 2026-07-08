# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

- Add a pet (and its owner's basic info/preferences) to the system.
- Add or edit a care task for a pet (title, duration, priority, and optionally a fixed time or recurrence).
- Generate today's schedule/plan, which picks and orders tasks based on available time and priority, and explains why each task was placed where it was.

**a. Initial design**

My initial UML has five classes:

- **Owner** — holds the owner's name and preferences, and owns a list of `Pet`s.
- **Pet** — holds name, species, and a list of `Task`s; responsible for adding/removing its own tasks.
- **Task** — a data-only class describing one piece of care (title, duration, priority, category, optional fixed time, and recurrence info).
- **Scheduler** — takes a `Pet` and an available-time budget, and is responsible for building an ordered daily plan (`build_plan`) and explaining its choices (`explain`).
- **ScheduledItem** — the output of scheduling: a `Task` paired with a concrete start/end time and a reason string.

I split `Task` (raw data) from `ScheduledItem` (task + computed time slot + reasoning) so the scheduler doesn't have to mutate `Task` objects — it just produces a new list of `ScheduledItem`s, keeping the pet's task list as the source of truth.

**b. Design changes**

While reviewing the skeleton with AI assistance, two potential issues surfaced before any logic was written:

1. There's currently no way to mark a task as "done" for the day, so a recurring task could get rescheduled repeatedly even after completion. I plan to add a `completed_today` flag (or a separate completion log) once I implement scheduling logic.
2. `available_minutes` exists both as a `Scheduler` field and as a parameter to `build_plan`, which is redundant. I'll likely drop the field and only take it as a parameter, since the available time can change per day/run.

No structural classes changed yet — these are refinements I'll make when I move from skeleton to actual logic.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

`Scheduler.build_plan()` considers three constraints, in this order: (1) a task's `fixed_time`, if it has one — fixed-time tasks are placed first and never reordered by priority; (2) `priority` (`high` > `medium` > `low`) for everything without a fixed time; and (3) `available_minutes` — the running time budget, which causes a task to be skipped entirely if it no longer fits, rather than being scheduled anyway.

Fixed time was given the highest precedence because it represents a real-world commitment (a vet appointment, a dog walker's arrival) that the owner can't renegotiate, whereas priority is a preference the scheduler is free to use for the tasks that are actually flexible. Time budget comes last as a hard constraint/cutoff rather than an ordering signal — it doesn't change the order tasks are considered in, it just decides whether a task makes it into the plan at all.

**b. Tradeoffs**

`Scheduler.detect_conflicts()` only flags tasks that share the *exact same* `fixed_time` (e.g. two tasks both at 08:00), rather than checking whether their durations actually overlap (e.g. an 08:00-08:30 walk and an 08:15 feeding). Exact-match comparison is a simple dictionary keyed by `time`, so it's O(n) and easy to reason about, whereas true overlap detection means comparing every pair of time ranges (or sorting and sweeping), which is more code and more ways to get the edge cases wrong (adjacent-but-not-overlapping, one task fully containing another, etc.).

This tradeoff is reasonable for a small pet-care scheduler: task counts per pet per day are tiny, and most real conflicts a pet owner would hit ("I told the dog walker 8am and also blocked the vet for 8am") are exact clashes anyway. The known gap is documented here so it can be revisited if the app grows into finer-grained, minute-level overlap checking.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used across the whole build, phase by phase: brainstorming the initial class list and UML from the README scenario, scaffolding dataclass skeletons before any logic existed, implementing the actual scheduling/sorting/filtering/conflict/recurrence algorithms, wiring the Streamlit UI to the backend, writing and debugging the pytest suite, and finally reviewing the UML and README against the finished code to make sure the docs matched reality. The most effective interactions were the ones scoped to a single concern per phase (design vs. implementation vs. testing vs. polish) rather than one long open-ended conversation — asking narrow, concrete questions like "how should the Scheduler retrieve tasks from the Owner's pets" or "what edge cases should I test for sorting and recurrence" produced more directly usable answers than broad requests like "improve my scheduler."

**b. Judgment and verification**

One place I didn't accept the first version as-is: the original `Scheduler` design coupled `available_minutes` to the `Scheduler` object itself (a field) in addition to passing it into `build_plan()`. That's redundant state — the available time can change every day/run, so it doesn't belong on the long-lived `Scheduler` instance. I flagged this in `reflection.md` during the design phase and later removed the field, keeping `available_minutes` only as a `build_plan()` parameter. I verified the change didn't break anything by rerunning the full pytest suite and the `main.py` CLI demo after each refactor, rather than trusting the diff on inspection alone.

---

## 4. Testing and Verification

**a. What you tested**

16 tests in `tests/test_pawpal.py` cover: task completion (`mark_complete`, task count on a pet), sorting (`sort_by_time` chronological order, unscheduled-last, stability for ties), filtering (`filter_tasks` by pet, by completion, by both), conflict detection (same-time flagged, distinct times ignored, no fixed-time tasks produce no warnings), recurrence (daily → +1 day, weekly → +7 days, non-recurring produces no next occurrence, `Pet.complete_task` actually appends the new occurrence), and scheduling edge cases (no pets, a pet with no tasks, respecting the available-minutes budget, skipping completed tasks). These behaviors were prioritized because they're the "smart" parts of the system — the parts most likely to silently produce a wrong schedule rather than crash outright.

**b. Confidence**

I'd rate my confidence at 4/5. The happy paths and the edge cases I identified are solidly covered and all 16 tests pass. The gap I'm most aware of is duration-overlap conflict detection (currently only exact `fixed_time` matches are caught — see 2b), and I haven't tested what happens with malformed input (e.g. a `recurrence` value outside `"daily"`/`"weekly"`, or a negative `duration_minutes`), since the UI currently constrains those values before they reach the backend. If I had more time I'd add tests for: two recurring tasks completing in the same run, a task whose duration exceeds `available_minutes` entirely, and true time-range overlap (not just identical start times) once that logic is implemented.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the separation between `Task` (raw data) and `ScheduledItem` (a task placed into a concrete time slot with a reason). It meant the scheduler never had to mutate a pet's actual tasks just to produce a plan, which made it straightforward to add sorting, filtering, and conflict detection later as independent read-only operations over the same task list, without any of them stepping on each other.

**b. What you would improve**

I'd redesign conflict detection to check real time-range overlap instead of exact `fixed_time` equality (see section 2b) — it's the most visible gap between what the app promises ("detect conflicts") and what it actually guarantees. I'd also add a small amount of input validation at the `Task` level (e.g. rejecting an unrecognized `recurrence` value or a non-positive `duration_minutes`) instead of relying entirely on the Streamlit form widgets to keep bad values out.

**c. Key takeaway**

Being the "lead architect" with an AI assistant meant my job was mostly deciding what should be true of the system — which constraints matter most, which tradeoffs are acceptable for this scenario's scale, when a suggestion was technically fine but architecturally redundant — while the AI handled turning those decisions into working code quickly. The moments where the design actually improved were the ones where I stopped and asked "does this match what I intended" (e.g. the `available_minutes` duplication) rather than accepting the first working version. Separate, phase-scoped conversations helped this: keeping design brainstorming, implementation, testing, and polish in their own contexts meant each response stayed focused on the actual question instead of re-explaining or re-deciding things that were already settled.
