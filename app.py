import uuid

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

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

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "pet": pet.name,
                "title": task.title,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "category": task.category,
                "fixed_time": task.fixed_time.strftime("%H:%M") if task.fixed_time else "",
                "completed": task.completed,
            }
            for pet, task in all_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Schedule ------------------------------------------------------------
st.subheader("Build Schedule")
available_minutes = st.number_input(
    "Available minutes today", min_value=1, max_value=1440, value=90
)

if st.button("Generate schedule"):
    scheduler = Scheduler()
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
