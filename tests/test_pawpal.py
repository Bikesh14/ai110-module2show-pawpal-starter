"""Tests for core PawPal+ backend behaviors."""

from datetime import time

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_task_status():
    task = Task(id="t1", title="Feed cat", duration_minutes=10, priority="high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="cat")
    assert len(pet.tasks) == 0

    pet.add_task(Task(id="t1", title="Feed cat", duration_minutes=10, priority="high"))

    assert len(pet.tasks) == 1


def test_build_plan_skips_completed_tasks():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")
    task = Task(id="t1", title="Feed cat", duration_minutes=10, priority="high")
    task.mark_complete()
    pet.add_task(task)
    owner.add_pet(pet)

    scheduler = Scheduler(day_start=time(8, 0))
    plan = scheduler.build_plan(owner, available_minutes=60)

    assert plan == []


def test_build_plan_respects_available_minutes():
    owner = Owner(name="Jordan")
    pet = Pet(name="Biscuit", species="dog")
    pet.add_task(Task(id="t1", title="Walk", duration_minutes=30, priority="high"))
    pet.add_task(Task(id="t2", title="Play", duration_minutes=30, priority="low"))
    owner.add_pet(pet)

    scheduler = Scheduler(day_start=time(8, 0))
    plan = scheduler.build_plan(owner, available_minutes=30)

    assert len(plan) == 1
    assert plan[0].task.id == "t1"
