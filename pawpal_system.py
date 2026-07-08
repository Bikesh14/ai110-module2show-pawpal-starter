"""Core backend logic for PawPal+: owners, pets, tasks, and scheduling."""

import json
from dataclasses import asdict, dataclass, field, replace
from datetime import date, datetime, time, timedelta
from typing import Optional

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
RECURRENCE_DELTAS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


@dataclass
class Task:
    """A single pet care activity (e.g. walk, feeding, meds)."""

    id: str
    title: str
    duration_minutes: int
    priority: str  # "low" | "medium" | "high"
    category: str = "general"  # e.g. "walk", "feeding", "meds", "grooming", "enrichment"
    fixed_time: Optional[time] = None
    is_recurring: bool = False
    recurrence: Optional[str] = None  # e.g. "daily", "weekly"
    completed: bool = False
    due_date: Optional[date] = None

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task as completed; return the next occurrence if it recurs."""
        self.completed = True
        if self.is_recurring and self.recurrence in RECURRENCE_DELTAS:
            return self.next_occurrence()
        return None

    def mark_incomplete(self) -> None:
        """Reset this task to not completed (e.g. for a new recurring cycle)."""
        self.completed = False

    def next_occurrence(self) -> "Task":
        """Build the next instance of a recurring task, due one cycle later."""
        delta = RECURRENCE_DELTAS[self.recurrence]
        base_date = self.due_date or date.today()
        return replace(
            self,
            id=f"{self.id}-{(base_date + delta).isoformat()}",
            due_date=base_date + delta,
            completed=False,
        )


@dataclass
class Pet:
    """A pet owned by an Owner, with its own list of care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task from this pet's task list by id."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def pending_tasks(self) -> list[Task]:
        """Return this pet's tasks that are not yet completed."""
        return [t for t in self.tasks if not t.completed]

    def complete_task(self, task_id: str) -> Optional[Task]:
        """Mark a task complete by id, adding its next occurrence if it recurs."""
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task is None:
            return None
        next_task = task.mark_complete()
        if next_task is not None:
            self.add_task(next_task)
        return next_task


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs for every task across all of this owner's pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def save_to_json(self, path: str) -> None:
        """Serialize this owner (and all pets/tasks) to a JSON file."""
        data = asdict(self)
        for pet in data["pets"]:
            for task in pet["tasks"]:
                if task["fixed_time"] is not None:
                    task["fixed_time"] = task["fixed_time"].isoformat()
                if task["due_date"] is not None:
                    task["due_date"] = task["due_date"].isoformat()
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_from_json(cls, path: str) -> "Owner":
        """Load an owner (and all pets/tasks) from a JSON file previously written by save_to_json."""
        with open(path) as f:
            data = json.load(f)

        pets = []
        for pet_data in data["pets"]:
            tasks = []
            for task_data in pet_data["tasks"]:
                task_data = dict(task_data)
                if task_data["fixed_time"] is not None:
                    task_data["fixed_time"] = time.fromisoformat(task_data["fixed_time"])
                if task_data["due_date"] is not None:
                    task_data["due_date"] = date.fromisoformat(task_data["due_date"])
                tasks.append(Task(**task_data))
            pets.append(Pet(name=pet_data["name"], species=pet_data["species"], tasks=tasks))

        return cls(name=data["name"], preferences=data["preferences"], pets=pets)


@dataclass
class ScheduledItem:
    """A task placed into a concrete time slot, with the reason it was scheduled there."""

    pet: Pet
    task: Task
    start_time: time
    end_time: time
    reason: str = ""


@dataclass
class Scheduler:
    """The 'brain' that retrieves tasks from an Owner's pets and builds a daily plan."""

    day_start: time = time(8, 0)

    def build_plan(self, owner: Owner, available_minutes: int) -> list[ScheduledItem]:
        """Build an ordered daily plan across all of the owner's pets within a time budget."""
        candidates = [
            (pet, task) for pet, task in owner.get_all_tasks() if not task.completed
        ]

        def sort_key(pair: tuple[Pet, Task]) -> tuple:
            _, task = pair
            has_fixed_time = task.fixed_time is None
            return (
                has_fixed_time,
                task.fixed_time or time(0, 0),
                PRIORITY_ORDER.get(task.priority, 3),
            )

        candidates.sort(key=sort_key)

        plan: list[ScheduledItem] = []
        remaining_minutes = available_minutes
        cursor = datetime.combine(datetime.min.date(), self.day_start)

        for pet, task in candidates:
            if task.duration_minutes > remaining_minutes:
                continue

            start_dt = (
                datetime.combine(datetime.min.date(), task.fixed_time)
                if task.fixed_time
                else cursor
            )
            end_dt = start_dt + timedelta(minutes=task.duration_minutes)

            reason = self._build_reason(task)
            plan.append(
                ScheduledItem(
                    pet=pet,
                    task=task,
                    start_time=start_dt.time(),
                    end_time=end_dt.time(),
                    reason=reason,
                )
            )

            remaining_minutes -= task.duration_minutes
            if not task.fixed_time:
                cursor = end_dt
            elif end_dt > cursor:
                cursor = end_dt

        return plan

    def _build_reason(self, task: Task) -> str:
        """Explain why a task was placed where it was."""
        if task.fixed_time:
            return f"Scheduled at its fixed time ({task.fixed_time.strftime('%H:%M')})."
        return f"Ordered by {task.priority} priority among remaining tasks."

    def explain(self, plan: list[ScheduledItem]) -> str:
        """Return a human-readable explanation of a full plan."""
        if not plan:
            return "No tasks were scheduled."
        lines = [
            f"{item.start_time.strftime('%H:%M')} - {item.pet.name}: {item.task.title} "
            f"({item.task.duration_minutes} min, {item.task.priority} priority) — {item.reason}"
            for item in plan
        ]
        return "\n".join(lines)

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by fixed_time (HH:MM); tasks with no fixed time sort last."""
        return sorted(
            tasks,
            key=lambda task: (task.fixed_time is None, task.fixed_time or time(0, 0)),
        )

    def filter_tasks(
        self,
        owner: Owner,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list[Task]:
        """Filter tasks across an owner's pets by pet name and/or completion status."""
        pairs = owner.get_all_tasks()
        if pet_name is not None:
            pairs = [(pet, task) for pet, task in pairs if pet.name == pet_name]
        if completed is not None:
            pairs = [(pet, task) for pet, task in pairs if task.completed == completed]
        return [task for _, task in pairs]

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority first (high > medium > low), then by fixed_time."""
        return sorted(
            tasks,
            key=lambda task: (
                PRIORITY_ORDER.get(task.priority, 3),
                task.fixed_time is None,
                task.fixed_time or time(0, 0),
            ),
        )

    def find_next_available_slot(
        self, owner: Owner, duration_minutes: int, day_end: time = time(20, 0)
    ) -> Optional[time]:
        """Find the earliest open time slot (of at least duration_minutes) around existing fixed-time tasks."""
        busy = sorted(
            (
                (task.fixed_time, task.duration_minutes)
                for _, task in owner.get_all_tasks()
                if task.fixed_time is not None and not task.completed
            )
        )

        cursor = datetime.combine(datetime.min.date(), self.day_start)
        day_end_dt = datetime.combine(datetime.min.date(), day_end)

        for fixed_time, busy_duration in busy:
            busy_start = datetime.combine(datetime.min.date(), fixed_time)
            if busy_start < cursor:
                # Overlaps a slot already claimed by an earlier task; skip past it.
                cursor = max(cursor, busy_start + timedelta(minutes=busy_duration))
                continue
            gap_minutes = (busy_start - cursor).total_seconds() / 60
            if gap_minutes >= duration_minutes:
                return cursor.time()
            cursor = busy_start + timedelta(minutes=busy_duration)

        if (day_end_dt - cursor).total_seconds() / 60 >= duration_minutes:
            return cursor.time()
        return None

    def detect_conflicts(self, owner: Owner) -> list[str]:
        """Return warning messages for tasks with the same fixed_time (same or different pets)."""
        warnings: list[str] = []
        timed = [
            (pet, task) for pet, task in owner.get_all_tasks() if task.fixed_time is not None
        ]
        by_time: dict[time, list[tuple[Pet, Task]]] = {}
        for pet, task in timed:
            by_time.setdefault(task.fixed_time, []).append((pet, task))

        for fixed_time, entries in by_time.items():
            if len(entries) < 2:
                continue
            names = ", ".join(f"{pet.name}: {task.title}" for pet, task in entries)
            warnings.append(
                f"Conflict at {fixed_time.strftime('%H:%M')} — {names}"
            )
        return warnings
