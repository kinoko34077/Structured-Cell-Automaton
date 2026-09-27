# Issue #3 Extended GUI Session State Implementation Plan

> **For agentic workers:** Follow this plan task-by-task and keep the Issue #3 scope bounded.

## Goal

Make `sca_gui_extended.py` preserve the current experiment across Streamlit
reruns, prevent duplicate emitted syntax entries, and avoid rebuilding
unchanged matplotlib figures. Keep the existing domain algorithms, save
format, UI controls, and visualization appearance unchanged.

## Architecture

- Treat `st.session_state` as the source of truth for generated cells, syntax
  pool, emitted syntax, `MemoryZone`, `OutputZone`, and the visualization
  figure cache.
- Initialize those values once per Streamlit session. The save/load controls
  replace the persisted cell and syntax values in session state.
- Append newly emitted syntax to the session-owned list exactly once; keep the
  local name as an alias only for rendering and domain calls.
- Build each visualization with `use_streamlit=False`, cache the returned
  figure through the existing renderer-signature helper, and display the
  cached figure with `st.pyplot`.

## Tech Stack and Verification

- Python 3.10, Streamlit AppTest, unittest, matplotlib.
- Project verification command: `python -m unittest discover -s project/tests -v`.
- Base verification command: `knt verify` when the local Base tooling is
  available.
- No browser/rendering claim is made from AppTest alone; perceived plotting
  latency and readability remain a manual smoke boundary.

## Global Constraints

- Work only in the dedicated `maintenance/issue-3-extended-gui` branch.
- Do not modify domain algorithms, persistence formats, completed Issues #4,
  #5, or #8, or the existing `sca_gui.py` implementation.
- Preserve the existing control labels, displayed content, and figure
  appearance. Use the existing `project.ui_helpers` cache contract.

## Review Focus

- A rerun caused by an unrelated button must retain the same experiment
  objects and emitted entries.
- The evolution path must not add the same `new_output` list twice.
- Loading state must update session state rather than a transient local.
- Each renderer must invalidate only for the inputs it consumes.
- Empty/no-output states must remain safe and the full existing test suite
  must stay green.

## Tasks

### 1. Add failing regression tests (RED)

- Add AppTest coverage for `sca_gui_extended.py` that asserts generated cells,
  syntax pool, memory/output zones, and emitted state survive a sequential
  rerun.
- Add a focused test for the evolution output contract that asserts each
  emitted SID occurs once in session state after the action.
- Add a focused cache integration test that exercises each renderer cache key
  and verifies an unrelated rerun reuses its figures while changed renderer
  inputs rebuild only the affected figure.
- Run the focused tests and record the expected failures against the current
  implementation before changing production code.

### 2. Implement session-owned extended GUI state (GREEN)

- Add small initialization helpers in `sca_gui_extended.py` for session-owned
  defaults without changing domain behavior.
- Route initial generation, loaded cells/syntaxes, emitted syntax, and both
  zones through those session keys.
- Replace the double append in the evolution action with one mutation of the
  session-owned emitted list. Persist thought-cycle results consistently.

### 3. Implement renderer-specific figure caching (GREEN)

- Add a session-owned visualization cache.
- Use the existing deterministic signature helper with score sensitivity only
  for the score heatmap; keep cluster/genealogy/co-occurrence signatures
  independent of score changes.
- Display cached figures explicitly and keep the visualization functions from
  writing to Streamlit during construction.

### 4. Verify and document

- Run focused tests, the complete Project unittest suite, and `knt verify`.
- Inspect the diff for scope drift and verify the worktree contains no
  generated or temporary tracked changes.
- Update `project/docs/CURRENT_STATE.md` with the Issue #3 implementation and
  the remaining manual plotting/readability boundary.
- Commit and push the coherent change, open a draft PR linked to Issue #3,
  and update the repository Issue/Control evidence without closing the Issue
  until the manual gate is satisfied.
