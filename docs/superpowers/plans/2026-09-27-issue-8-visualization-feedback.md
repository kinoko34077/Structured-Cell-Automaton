# Structured-Cell-Automaton Issue #8 Maintenance Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Preserve existing Streamlit visualization semantics while avoiding redundant graph rebuilds on unrelated reruns and exposing deterministic pruning/evolution outcomes.

**Architecture:** Keep Streamlit session state as the UI source of truth. Cache each rendered Matplotlib figure by a deterministic input signature, re-display the cached figure on unchanged reruns, and rebuild only when relevant syntax/tag inputs change. Make existing MemoryZone mutation methods return removed counts and report those counts from the existing controls; report explicit no-emission outcomes for evolution actions.

**Tech Stack:** Python, Streamlit AppTest, unittest, Matplotlib/NetworkX/Seaborn.

**Spec:** `kinoko34077/devflow#83` and `Structured-Cell-Automaton#8`; repository-owned `project/docs/SPEC.md`.

## Global Constraints

- Do not change SCA algorithms, scoring, memory policy, pruning thresholds, or visualization appearance.
- Preserve the existing Streamlit Project Overlay and root-domain file locations.
- Keep the natural-language analysis session-state repair unchanged.
- Verification must include the focused regression suite and the repository `knt verify`/unittest boundary.
- Browser-perceived plotting latency remains a manual boundary; do not claim it from unit/AppTest evidence.

## Review Focus

- Same visualization signature across an unrelated rerun must call the expensive builder once and still display the cached figure.
- A changed syntax/tag signature must invalidate only the affected cached figure.
- Empty/no-op pruning must be reported as zero/no-op rather than generic success.
- Evolution that completes without emission must be visible as no-emission, without changing emission thresholds.
- Existing emitted-output, analysis continuity, and generation-retention behavior must remain intact.

### Task 1: Visualization cache boundary

**Files:**
- Create: `project/ui_helpers.py`
- Modify: `sca_gui.py`
- Modify: `viz/cluster_map.py`
- Modify: `viz/genealogy_plot.py`
- Modify: `viz/cooccurrence_net.py`
- Modify: `viz/score_heatmap.py`
- Test: `project/tests/test_visualization_cache.py`

- [ ] Write a failing cache-helper test proving an unchanged signature reuses the first figure and a changed signature rebuilds.
- [ ] Run that focused test and verify it fails because the helper is absent.
- [ ] Implement the smallest session-cache helper and route each existing visualization through a signature-specific cache in `sca_gui.py`; have the existing renderer functions return their already-created figure while preserving their current display behavior.
- [ ] Run the focused cache test and the existing Streamlit state tests; verify GREEN and no analysis-continuity regressions.

### Task 2: Deterministic operation feedback

**Files:**
- Modify: `core/memory_zone.py`
- Modify: `sca_gui.py`
- Test: `project/tests/test_memory_pruning.py`
- Test: `project/tests/test_streamlit_state.py`

- [ ] Add RED assertions for removed counts from score/generation/similarity pruning and visible evolution/no-emission feedback.
- [ ] Run the focused tests and verify they fail on the current `None`/generic-feedback behavior.
- [ ] Return removed counts from the existing mutation methods, pass through the existing generation helper, and report effect magnitude or explicit no-op/no-emission status without changing thresholds or algorithms.
- [ ] Run the focused tests and the full repository unittest boundary; verify GREEN.

### Task 3: Documentation and verification

**Files:**
- Modify: `project/docs/CURRENT_STATE.md`

- [ ] Record the accepted behavior and remaining manual browser boundary.
- [ ] Run `knt doctor`, `knt base-check`, `knt test`, and `knt verify` (or the manifest-equivalent unittest commands) on the exact candidate head.
- [ ] Review the exact diff for scope, then open a PR referencing `Structured-Cell-Automaton#8` with RED/GREEN evidence.

