# Current State

Base version: `0.3.8`

Last verified: 2026-09-27 — Draft PR #14 / follow-up Issue #15 exact-head verification at `f646ad74fb24026d7a30922e68eb12721120deff`

## Implemented

- Repository-local KiNoTch Base v0.3.8 and Project Overlay
- `web-app` Surface declaration
- Structured Python dependency setup and Streamlit development command
- Existing Streamlit GUI, Domain modules, data, and save paths retained
- Existing Domain files remain at their original root paths; no bulk move was performed
- Project-owned Streamlit AppTest verification for sequential GUI reruns
- Generated cells/syntax pool, `MemoryZone`, `OutputZone`, and emitted syntax state persist within a Streamlit session
- The extended GUI (`sca_gui_extended.py`) keeps generated/loaded cells, syntax, emitted output, `MemoryZone`, and `OutputZone` in session state across reruns
- Memory reactivation debug output reads the actual `MemoryZone.pool` representation
- Memory retention age is defined in generations, with a configurable default threshold of 60 generations
- Streamlit session state preserves the current generation counter and stored syntax generation stamps
- The latest `意味タグに変換` result is persisted as plain session-state data (`input`, inferred/expanded tags, and already-linearized reactivated lines) and remains visible across unrelated reruns
- Matplotlib visualization figures are cached in Streamlit session state by renderer-specific deterministic syntax/tag input signatures and re-displayed without rebuilding on unrelated reruns
- The extended GUI renders cached figures with `use_streamlit=False` and `st.pyplot`, so unrelated control reruns reuse the four renderer-specific figures
- The extended GUI keeps the visible cell-count slider transparent: a changed value remains pending until `セル数を適用` explicitly regenerates the experiment and resets dependent output/cache state
- Extended-GUI visualization builders support `show=False`, so Streamlit-owned cached rendering does not open or block on Matplotlib windows; standalone callers retain the default display behavior
- Score, generation, and similarity pruning return deterministic removed counts that the UI reports as effect magnitude or explicit no-op
- Evolution actions report completion with either emitted output or an explicit no-emission result

## Default state

- `web-app`: `OVERRIDE` — existing Streamlit GUI is authoritative

## Known constraints

- Domain algorithms, visualization, and persistence semantics remain Project-owned.
- Installing `requirements.txt` remains an explicit local setup action.
- The pruning control uses generation age only; wall-clock timestamps are intentionally not part of this feature.
- Visualization figures are rebuilt only when their relevant syntax/tag input signature changes; browser/device-perceived plotting latency remains a manual smoke boundary.
- Changing the extended-GUI cell-count slider does not mutate the current experiment until the explicit apply action is selected.
- Matplotlib figures remain Project-owned and cached only for the current Streamlit session; no persistence or visualization appearance semantics changed.
- CI may emit Japanese-font warnings because the Linux runner does not provide the locally assumed `MS Gothic`; these warnings do not fail the current behavioral AppTest suite.

## Next work

1. Perform browser smoke for perceived plotting latency and figure readability when the environment is available; do not infer it from AppTest.
2. Preserve the existing Streamlit implementation as a Project override.
3. Keep generation-retention policy changes behind the named threshold/helper boundary.
4. Consider further Default adoption only where it removes a real duplicate.
5. Reopen Issue #8 only for a new reproducible regression or explicit requirement.

## Verification

- `knt doctor`
- `knt base-check`
- `knt test`
- `knt verify`
- `python -m unittest discover -s project/tests -v`
- analysis-result continuity TDD: RED `36254170995`; first implementation GREEN `36254348601`
- Issue #8 RED `36261556758`: missing cache helper, missing pruning counts, and missing evolution outcome status
- Issue #8 implementation GREEN `36261759834`: `knt doctor`, setup, and full Project verification passed
- Current-head review follow-up GREEN `36288719942`: renderer-specific signature regression and restored direct test entry point passed at `abf012adb9444aba57034252e8a79d9c9fb98367`
- Merged-main reconciliation: PR #11 merged at `e32e5c9f8d4b142398dfd24fe3f6a39c03e592c9`; main content matches the reviewed candidate and retains the manual browser/readability boundary
- Issue #3 extended GUI focused AppTest and full Project unittest suite: session state, load persistence, duplicate-append regression, and figure-cache reuse pass on the maintenance branch
- Issue #15 RED: cell-count control and renderer side-effect regressions reproduced from PR #14 review
- Issue #15 GREEN: explicit cell-count apply, side-effect-free renderer path, and full Project verification pass on the maintenance branch
- Current branch verification: `python -m unittest discover -s project/tests -v` — 15 passed; `knt.cmd doctor` — OK; `knt.cmd base-check` — OK; `knt.cmd verify` — 15 passed; Python compilation — OK

Current AppTest coverage exercises:
- `初回進化・発話` followed by `内的思考ループ実行` across Streamlit reruns without losing memory state;
- natural-language tag conversion/reactivation after a preceding memory-producing operation;
- the last natural-language analysis remaining stored and visibly rendered after an unrelated rerun.
