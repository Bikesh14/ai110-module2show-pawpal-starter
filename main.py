"""CLI demo script: verifies pawpal_system.py logic end-to-end before wiring up the UI."""

from datetime import date, time

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    owner = Owner(name="Jordan")

    mochi = Pet(name="Mochi", species="cat")
    # Tasks added out of time order on purpose, to exercise sort_by_time().
    mochi.add_task(
        Task(
            id="t2",
            title="Litter box cleaning",
            duration_minutes=5,
            priority="medium",
            category="grooming",
        )
    )
    mochi.add_task(
        Task(
            id="t1",
            title="Morning feeding",
            duration_minutes=10,
            priority="high",
            category="feeding",
            fixed_time=time(8, 0),
            is_recurring=True,
            recurrence="daily",
            due_date=date.today(),
        )
    )

    biscuit = Pet(name="Biscuit", species="dog")
    biscuit.add_task(
        Task(
            id="t5",
            title="Playtime",
            duration_minutes=20,
            priority="low",
            category="enrichment",
        )
    )
    biscuit.add_task(
        Task(
            id="t3",
            title="Morning walk",
            duration_minutes=30,
            priority="high",
            category="walk",
            fixed_time=time(8, 0),  # deliberately conflicts with Mochi's feeding
        )
    )
    biscuit.add_task(
        Task(
            id="t4",
            title="Give medication",
            duration_minutes=5,
            priority="high",
            category="meds",
        )
    )

    owner.add_pet(mochi)
    owner.add_pet(biscuit)
    return owner


def main() -> None:
    owner = build_demo_owner()
    scheduler = Scheduler(day_start=time(8, 0))

    all_tasks = [task for _, task in owner.get_all_tasks()]

    print("All tasks sorted by time:\n")
    for task in scheduler.sort_by_time(all_tasks):
        fixed = task.fixed_time.strftime("%H:%M") if task.fixed_time else "unscheduled"
        print(f"  [{fixed}] {task.title}")

    print("\nPending tasks for Mochi:\n")
    for task in scheduler.filter_tasks(owner, pet_name="Mochi", completed=False):
        print(f"  {task.title}")

    print("\nConflict check:\n")
    conflicts = scheduler.detect_conflicts(owner)
    if conflicts:
        for warning in conflicts:
            print(f"  WARNING: {warning}")
    else:
        print("  No conflicts detected.")

    print("\nCompleting Mochi's recurring feeding task...\n")
    mochi = owner.pets[0]
    next_task = mochi.complete_task("t1")
    if next_task:
        print(f"  Created next occurrence: {next_task.title} due {next_task.due_date}")

    plan = scheduler.build_plan(owner, available_minutes=90)

    print(f"\nToday's Schedule for {owner.name}'s pets:\n")
    for item in plan:
        print(
            f"  {item.start_time.strftime('%H:%M')} - {item.end_time.strftime('%H:%M')}  "
            f"[{item.pet.name}] {item.task.title} "
            f"({item.task.duration_minutes} min, {item.task.priority} priority)"
        )
        print(f"      reason: {item.reason}")

    print("\nExplanation:\n")
    print(scheduler.explain(plan))


if __name__ == "__main__":
    main()
