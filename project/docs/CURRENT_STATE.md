# Current State

Base version: `0.3.8`

Last verified: 2026-09-27 — Issue #8 visualization invalidation and operation feedback maintenance

## Implemented

- Repository-local KiNoTch Base v0.3.8 and Project Overlay
- `web-app` Surface declaration
- Structured Python dependency setup and Streamlit development command
- Existing Streamlit GUI, Domain modules, data, and save paths retained
- Existing Domain files remain at their original root paths; no bulk move was performed
- Project-owned Streamlit AppTest verification for sequential GUI reruns
- Generated cells/syntax pool, `MemoryZone`, `OutputZone`, and emitted syntax state persist within a Streamlit session
- Memory reactivation debug output reads the actual `MemoryZone.pool` representation
- Memory retention age is defined in generations, with a configurable default threshold of 60 generations
- Streamlit session state preserves the current generation counter and stored syntax generation stamps
- The latest `意味タグに変換` result is persisted as plain session-state data (`input`, inferred/expanded tags, and already-linearized reactivated lines) and remains visible across unrelated reruns
- Matplotlib visualization figures are cached in Streamlit session state by deterministic syntax/tag input signatures and re-displayed without rebuilding on unrelated reruns
- Score, generation, and similarity pruning return deterministic removed counts that the UI reports as effect magnitude or explicit no-op
- Evolution actions report completion with either emitted output or an explicit no-emission result

## Default state

- `web-app`: `OVERRIDE` — existing Streamlit GUI is authoritative

## Known constraints

- Domain algorithms, visualization, and persistence semantics remain Project-owned.
- Installing `requirements.txt` remains an explicit local setup action.
- The pruning control uses generation age only; wall-clock timestamps are intentionally not part of this feature.
- Visualization figures are rebuilt only when their relevant syntax/tag input signature changes; browser/device-perceived plotting latency remains a manual smoke boundary.
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

Current AppTest coverage exercises:
- `初回進化・発話` followed by `内的思考ループ実行` across Streamlit reruns without losing memory state;
- natural-language tag conversion/reactivation after a preceding memory-producing operation;
- the last natural-language analysis remaining stored and visibly rendered after an unrelated rerun.
