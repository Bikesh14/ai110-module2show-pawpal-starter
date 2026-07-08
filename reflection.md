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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
