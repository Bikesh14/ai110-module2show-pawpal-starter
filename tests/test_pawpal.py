"""Tests for core PawPal+ backend behaviors."""

from datetime import date, time, timedelta

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


def test_sort_by_time_orders_fixed_time_tasks_first():
    scheduler = Scheduler()
    unscheduled = Task(id="t1", title="Play", duration_minutes=10, priority="low")
    early = Task(id="t2", title="Feed", duration_minutes=10, priority="high", fixed_time=time(7, 0))
    late = Task(id="t3", title="Walk", duration_minutes=10, priority="high", fixed_time=time(9, 0))

    result = scheduler.sort_by_time([unscheduled, late, early])

    assert [t.id for t in result] == ["t2", "t3", "t1"]


def test_filter_tasks_by_pet_and_completion():
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="cat")
    biscuit = Pet(name="Biscuit", species="dog")
    mochi.add_task(Task(id="t1", title="Feed", duration_minutes=10, priority="high"))
    done_task = Task(id="t2", title="Litter", duration_minutes=5, priority="low")
    done_task.mark_complete()
    mochi.add_task(done_task)
    biscuit.add_task(Task(id="t3", title="Walk", duration_minutes=30, priority="high"))
    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    scheduler = Scheduler()

    assert [t.id for t in scheduler.filter_tasks(owner, pet_name="Mochi")] == ["t1", "t2"]
    assert [t.id for t in scheduler.filter_tasks(owner, completed=False)] == ["t1", "t3"]
    assert [t.id for t in scheduler.filter_tasks(owner, pet_name="Mochi", completed=True)] == ["t2"]


def test_detect_conflicts_flags_same_time_tasks():
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="cat")
    biscuit = Pet(name="Biscuit", species="dog")
    mochi.add_task(Task(id="t1", title="Feed", duration_minutes=10, priority="high", fixed_time=time(8, 0)))
    biscuit.add_task(Task(id="t2", title="Walk", duration_minutes=30, priority="high", fixed_time=time(8, 0)))
    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    scheduler = Scheduler()
    conflicts = scheduler.detect_conflicts(owner)

    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]


def test_detect_conflicts_ignores_distinct_times():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(Task(id="t1", title="Feed", duration_minutes=10, priority="high", fixed_time=time(8, 0)))
    pet.add_task(Task(id="t2", title="Play", duration_minutes=10, priority="low", fixed_time=time(9, 0)))
    owner.add_pet(pet)

    scheduler = Scheduler()

    assert scheduler.detect_conflicts(owner) == []


def test_mark_complete_on_recurring_task_creates_next_occurrence():
    today = date.today()
    task = Task(
        id="t1",
        title="Feed",
        duration_minutes=10,
        priority="high",
        is_recurring=True,
        recurrence="daily",
        due_date=today,
    )

    next_task = task.mark_complete()

    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == today + timedelta(days=1)


def test_mark_complete_on_non_recurring_task_creates_no_next_occurrence():
    task = Task(id="t1", title="One-off vet visit", duration_minutes=30, priority="high")

    next_task = task.mark_complete()

    assert next_task is None


def test_pet_complete_task_adds_next_occurrence_to_pet():
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(
        Task(
            id="t1",
            title="Feed",
            duration_minutes=10,
            priority="high",
            is_recurring=True,
            recurrence="daily",
            due_date=date.today(),
        )
    )

    pet.complete_task("t1")

    assert len(pet.tasks) == 2
    assert pet.tasks[1].due_date == date.today() + timedelta(days=1)


def test_weekly_recurrence_advances_by_seven_days():
    today = date.today()
    task = Task(
        id="t1",
        title="Grooming",
        duration_minutes=30,
        priority="medium",
        is_recurring=True,
        recurrence="weekly",
        due_date=today,
    )

    next_task = task.mark_complete()

    assert next_task.due_date == today + timedelta(weeks=1)


def test_build_plan_with_no_pets_returns_empty_plan():
    owner = Owner(name="Jordan")
    scheduler = Scheduler()

    assert scheduler.build_plan(owner, available_minutes=120) == []


def test_build_plan_with_pet_that_has_no_tasks():
    owner = Owner(name="Jordan")
    owner.add_pet(Pet(name="Mochi", species="cat"))
    scheduler = Scheduler()

    assert scheduler.build_plan(owner, available_minutes=120) == []


def test_detect_conflicts_with_no_fixed_time_tasks_returns_no_warnings():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")
    pet.add_task(Task(id="t1", title="Play", duration_minutes=10, priority="low"))
    owner.add_pet(pet)

    scheduler = Scheduler()

    assert scheduler.detect_conflicts(owner) == []


def test_sort_by_time_is_stable_for_tasks_at_same_time():
    scheduler = Scheduler()
    first = Task(id="t1", title="Feed", duration_minutes=10, priority="high", fixed_time=time(8, 0))
    second = Task(id="t2", title="Walk", duration_minutes=30, priority="high", fixed_time=time(8, 0))

    result = scheduler.sort_by_time([first, second])

    assert [t.id for t in result] == ["t1", "t2"]
