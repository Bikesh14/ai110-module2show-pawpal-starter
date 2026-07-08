"""Core backend logic for PawPal+: owners, pets, tasks, and scheduling."""

from dataclasses import dataclass, field
from datetime import time
from typing import Optional


@dataclass
class Task:
    id: str
    title: str
    duration_minutes: int
    priority: str  # "low" | "medium" | "high"
    category: str = "general"  # e.g. "walk", "feeding", "meds", "grooming", "enrichment"
    fixed_time: Optional[time] = None
    is_recurring: bool = False
    recurrence: Optional[str] = None  # e.g. "daily", "weekly"


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_id: str) -> None:
        pass


@dataclass
class Owner:
    name: str
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass


@dataclass
class ScheduledItem:
    task: Task
    start_time: time
    end_time: time
    reason: str = ""


@dataclass
class Scheduler:
    available_minutes: int = 240

    def build_plan(self, pet: Pet, available_minutes: Optional[int] = None) -> list[ScheduledItem]:
        pass

    def explain(self, plan: list[ScheduledItem]) -> str:
        pass
