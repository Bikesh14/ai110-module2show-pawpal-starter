"""CLI demo script: verifies pawpal_system.py logic end-to-end before wiring up the UI."""

from datetime import time

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    owner = Owner(name="Jordan")

    mochi = Pet(name="Mochi", species="cat")
    mochi.add_task(
        Task(
            id="t1",
            title="Morning feeding",
            duration_minutes=10,
            priority="high",
            category="feeding",
            fixed_time=time(8, 0),
        )
    )
    mochi.add_task(
        Task(
            id="t2",
            title="Litter box cleaning",
            duration_minutes=5,
            priority="medium",
            category="grooming",
        )
    )

    biscuit = Pet(name="Biscuit", species="dog")
    biscuit.add_task(
        Task(
            id="t3",
            title="Morning walk",
            duration_minutes=30,
            priority="high",
            category="walk",
            fixed_time=time(8, 30),
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
    biscuit.add_task(
        Task(
            id="t5",
            title="Playtime",
            duration_minutes=20,
            priority="low",
            category="enrichment",
        )
    )

    owner.add_pet(mochi)
    owner.add_pet(biscuit)
    return owner


def main() -> None:
    owner = build_demo_owner()
    scheduler = Scheduler(day_start=time(8, 0))
    plan = scheduler.build_plan(owner, available_minutes=90)

    print(f"Today's Schedule for {owner.name}'s pets:\n")
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
