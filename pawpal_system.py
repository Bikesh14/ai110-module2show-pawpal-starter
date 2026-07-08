"""Core backend logic for PawPal+: owners, pets, tasks, and scheduling."""

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Optional

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


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

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Reset this task to not completed (e.g. for a new recurring cycle)."""
        self.completed = False


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
