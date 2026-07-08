"""CLI demo script: verifies pawpal_system.py logic end-to-end before wiring up the UI."""

from datetime import date, time

from tabulate import tabulate

from pawpal_system import Owner, Pet, Scheduler, Task

CATEGORY_EMOJI = {
    "walk": "🚶",
    "feeding": "🍽️",
    "meds": "💊",
    "grooming": "🧼",
    "enrichment": "🧸",
    "general": "📌",
}


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


def task_row(pet_name: str, task: Task) -> list:
    emoji = CATEGORY_EMOJI.get(task.category, "📌")
    status = "✅ done" if task.completed else "⏳ pending"
    fixed = task.fixed_time.strftime("%H:%M") if task.fixed_time else "—"
    return [pet_name, f"{emoji} {task.title}", fixed, f"{task.duration_minutes} min", task.priority, status]


def print_task_table(rows: list) -> None:
    print(
        tabulate(
            rows,
            headers=["Pet", "Task", "Time", "Duration", "Priority", "Status"],
            tablefmt="github",
        )
    )


def section(title: str) -> None:
    print(f"\n=== {title} ===\n")


def main() -> None:
    owner = build_demo_owner()
    scheduler = Scheduler(day_start=time(8, 0))
    all_pairs = owner.get_all_tasks()

    section("📋 All Tasks (sorted by time)")
    sorted_tasks = scheduler.sort_by_time([task for _, task in all_pairs])
    pet_by_task_id = {task.id: pet.name for pet, task in all_pairs}
    print_task_table([task_row(pet_by_task_id[t.id], t) for t in sorted_tasks])

    section("🔥 All Tasks (sorted by priority)")
    priority_sorted = scheduler.sort_by_priority([task for _, task in all_pairs])
    print_task_table([task_row(pet_by_task_id[t.id], t) for t in priority_sorted])

    section("🐱 Pending Tasks for Mochi")
    pending = scheduler.filter_tasks(owner, pet_name="Mochi", completed=False)
    print_task_table([task_row("Mochi", t) for t in pending])

    section("⚠️  Conflict Check")
    conflicts = scheduler.detect_conflicts(owner)
    if conflicts:
        for warning in conflicts:
            print(f"  ⚠️  {warning}")
    else:
        print("  ✅ No conflicts detected.")

    section("🕒 Next Available Slot")
    slot = scheduler.find_next_available_slot(owner, duration_minutes=15)
    print(f"  Next 15-minute opening: {slot.strftime('%H:%M') if slot else 'none available today'}")

    section("🔁 Completing Mochi's Recurring Feeding Task")
    mochi = owner.pets[0]
    next_task = mochi.complete_task("t1")
    if next_task:
        print(f"  ✅ Completed. Next occurrence '{next_task.title}' created, due {next_task.due_date}.")

    section(f"📅 Today's Schedule for {owner.name}'s Pets")
    plan = scheduler.build_plan(owner, available_minutes=90)
    schedule_rows = [
        [
            f"{item.start_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')}",
            item.pet.name,
            f"{CATEGORY_EMOJI.get(item.task.category, '📌')} {item.task.title}",
            item.task.priority,
            item.reason,
        ]
        for item in plan
    ]
    print(tabulate(schedule_rows, headers=["Time", "Pet", "Task", "Priority", "Reason"], tablefmt="github"))

    section("💬 Explanation")
    print(scheduler.explain(plan))

    section("💾 Persistence")
    owner.save_to_json("data.json")
    reloaded = Owner.load_from_json("data.json")
    print(f"  Saved to data.json and reloaded: {reloaded.name} with {len(reloaded.pets)} pet(s).")


if __name__ == "__main__":
    main()
