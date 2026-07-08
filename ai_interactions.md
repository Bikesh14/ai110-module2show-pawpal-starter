# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Implement the four "Optional Extensions" stretch challenges in one pass: (1) a third algorithmic capability — `Scheduler.find_next_available_slot()` — that finds the earliest open gap of a given duration around existing fixed-time tasks; (2) JSON persistence via `Owner.save_to_json()` / `Owner.load_from_json()`; (3) a `Scheduler.sort_by_priority()` variant that sorts by priority first, then time; and (4) CLI output formatting polish using `tabulate` and category emojis in `main.py`.

**What did the agent do?**

- Edited `pawpal_system.py`: added `sort_by_priority()` and `find_next_available_slot()` to `Scheduler`, and `save_to_json()`/`load_from_json()` to `Owner` (handling `time`/`date` serialization to/from ISO strings since `dataclasses.asdict()` doesn't do that automatically).
- Added `tabulate>=0.9` to `requirements.txt` and installed it in the project's `.venv`.
- Rewrote `main.py` to use `tabulate` tables with category emojis (🍽️ feeding, 🚶 walk, 💊 meds, etc.) and status indicators (✅/⏳), and added demo sections exercising the new slot-finder, priority sort, and save/load round trip.
- Wired the same features into `app.py`: Save/Load buttons that read/write `data.json` and replace the session's `Owner`, and a "Find Next Available Slot" control.
- Added `data.json` to `.gitignore` since it's a generated data file, not source.
- Added 6 new tests to `tests/test_pawpal.py` covering `sort_by_priority`, three `find_next_available_slot` scenarios (open slot before a task, gap too small, day fully booked), and a JSON save/load round trip using pytest's `tmp_path` fixture.
- Ran `python -m pytest`, `python main.py`, and booted the Streamlit app (`streamlit run app.py --server.headless true`) with a `curl` health check after every file change to confirm nothing broke.

**What did you have to verify or fix manually?**

I checked that `dataclasses.asdict()` on `Owner` — which is a nested structure of `Owner → Pet → Task` — actually produces JSON-serializable data before trusting the "just add `save_to_json`/`load_from_json`" suggestion; `time` and `date` objects aren't JSON-serializable by default, so I confirmed the agent's fix explicitly converts them to `.isoformat()` strings on save and parses them back with `time.fromisoformat()`/`date.fromisoformat()` on load, rather than assuming a naive `json.dump(asdict(owner))` would work. I verified this by round-tripping a real `Owner` with a recurring, fixed-time task through `save_to_json`/`load_from_json` in a test and asserting the reloaded task's `fixed_time` and `due_date` matched exactly.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
