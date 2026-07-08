import os
import uuid

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

DATA_FILE = "data.json"

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time and priority.
"""
)

# Streamlit re-runs this whole script on every interaction, so the Owner must
# live in st.session_state or it would be recreated (and emptied) each time.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner: Owner = st.session_state.owner

st.divider()

# --- Persistence -------------------------------------------------------------
st.subheader("Save / Load")
save_col, load_col = st.columns(2)
with save_col:
    if st.button("💾 Save to data.json"):
        owner.save_to_json(DATA_FILE)
        st.success(f"Saved to {DATA_FILE}")
with load_col:
    if st.button("📂 Load from data.json"):
        if os.path.exists(DATA_FILE):
            st.session_state.owner = Owner.load_from_json(DATA_FILE)
            st.success(f"Loaded from {DATA_FILE}")
            st.rerun()
        else:
            st.warning(f"{DATA_FILE} not found. Save first.")

st.divider()

# --- Owner + Pets -----------------------------------------------------------
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

st.subheader("Pets")

with st.form("add_pet_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        new_pet_name = st.text_input("Pet name", value="")
    with col2:
        new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])
    add_pet_submitted = st.form_submit_button("Add pet")

if add_pet_submitted and new_pet_name.strip():
    owner.add_pet(Pet(name=new_pet_name.strip(), species=new_pet_species))
    st.success(f"Added pet: {new_pet_name.strip()}")

if not owner.pets:
    st.info("No pets yet. Add one above.")
else:
    st.write("Current pets:", ", ".join(f"{p.name} ({p.species})" for p in owner.pets))

st.divider()

# --- Tasks -------------------------------------------------------------------
st.subheader("Tasks")

if owner.pets:
    with st.form("add_task_form", clear_on_submit=True):
        pet_names = [p.name for p in owner.pets]
        selected_pet_name = st.selectbox("Pet", pet_names)
        task_title = st.text_input("Task title", value="Morning walk")
        col1, col2, col3 = st.columns(3)
        with col1:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col2:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        with col3:
            category = st.selectbox(
                "Category", ["walk", "feeding", "meds", "grooming", "enrichment", "general"]
            )
        use_fixed_time = st.checkbox("Fixed time?")
        fixed_time = st.time_input("Time", disabled=not use_fixed_time) if use_fixed_time else None
        add_task_submitted = st.form_submit_button("Add task")

    if add_task_submitted and task_title.strip():
        pet = next(p for p in owner.pets if p.name == selected_pet_name)
        pet.add_task(
            Task(
                id=str(uuid.uuid4()),
                title=task_title.strip(),
                duration_minutes=int(duration),
                priority=priority,
                category=category,
                fixed_time=fixed_time,
            )
        )
        st.success(f"Added task '{task_title.strip()}' for {selected_pet_name}")
else:
    st.info("Add a pet before adding tasks.")

scheduler = Scheduler()
all_tasks = owner.get_all_tasks()

if all_tasks:
    st.write("Current tasks:")

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        filter_pet = st.selectbox("Filter by pet", ["All"] + [p.name for p in owner.pets])
    with filter_col2:
        filter_status = st.selectbox("Filter by status", ["All", "Pending", "Completed"])

    filtered = scheduler.filter_tasks(
        owner,
        pet_name=None if filter_pet == "All" else filter_pet,
        completed=None if filter_status == "All" else filter_status == "Completed",
    )
    # sort_by_time() expects plain Task objects; keep the owning pet alongside for display/actions.
    task_to_pet = {task.id: pet for pet, task in all_tasks}
    sorted_filtered = scheduler.sort_by_time(filtered)

    st.table(
        [
            {
                "pet": task_to_pet[task.id].name,
                "title": task.title,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "category": task.category,
                "fixed_time": task.fixed_time.strftime("%H:%M") if task.fixed_time else "",
                "recurrence": task.recurrence or "",
                "completed": task.completed,
            }
            for task in sorted_filtered
        ]
    )

    with st.expander("Mark a task complete"):
        pending = [t for t in sorted_filtered if not t.completed]
        if pending:
            task_labels = {f"{task_to_pet[t.id].name}: {t.title}": t for t in pending}
            chosen_label = st.selectbox("Task", list(task_labels.keys()))
            if st.button("Mark complete"):
                chosen_task = task_labels[chosen_label]
                pet = task_to_pet[chosen_task.id]
                next_task = pet.complete_task(chosen_task.id)
                if next_task:
                    st.success(
                        f"Completed '{chosen_task.title}'. Next occurrence created for "
                        f"{next_task.due_date}."
                    )
                else:
                    st.success(f"Completed '{chosen_task.title}'.")
                st.rerun()
        else:
            st.info("No pending tasks to complete for this filter.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Conflicts -------------------------------------------------------------
conflicts = scheduler.detect_conflicts(owner)
if conflicts:
    st.subheader("⚠️ Scheduling Conflicts")
    for warning in conflicts:
        st.warning(warning)

st.divider()

# --- Next available slot ----------------------------------------------------
if all_tasks:
    st.subheader("Find Next Available Slot")
    slot_duration = st.number_input("Slot duration (minutes)", min_value=5, max_value=240, value=15)
    if st.button("Find slot"):
        slot = scheduler.find_next_available_slot(owner, duration_minutes=int(slot_duration))
        if slot:
            st.success(f"Next open slot: {slot.strftime('%H:%M')}")
        else:
            st.warning("No open slot of that length remains today.")

    st.divider()

# --- Schedule ------------------------------------------------------------
st.subheader("Build Schedule")
available_minutes = st.number_input(
    "Available minutes today", min_value=1, max_value=1440, value=90
)

if st.button("Generate schedule"):
    plan = scheduler.build_plan(owner, available_minutes=int(available_minutes))

    if not plan:
        st.warning("No tasks could be scheduled. Add pets/tasks or increase available minutes.")
    else:
        st.write("### Today's Schedule")
        for item in plan:
            st.markdown(
                f"**{item.start_time.strftime('%H:%M')} - {item.end_time.strftime('%H:%M')}** "
                f"[{item.pet.name}] {item.task.title} "
                f"({item.task.duration_minutes} min, {item.task.priority} priority)\n\n"
                f"> {item.reason}"
            )

        st.write("### Explanation")
        st.text(scheduler.explain(plan))
