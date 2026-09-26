# Current State

Base version: `0.3.8`

Last verified: 2026-09-26 — behavioral Streamlit AppTest maintenance

## Implemented

- Repository-local KiNoTch Base v0.3.8 and Project Overlay
- `web-app` Surface declaration
- Structured Python dependency setup and Streamlit development command
- Existing Streamlit GUI, Domain modules, data, and save paths retained
- Existing Domain files remain at their original root paths; no bulk move was performed
- Project-owned Streamlit AppTest verification for sequential GUI reruns
- Generated cells/syntax pool, `MemoryZone`, `OutputZone`, and emitted syntax state persist within a Streamlit session
- Memory reactivation debug output reads the actual `MemoryZone.pool` representation

## Default state

- `web-app`: `OVERRIDE` — existing Streamlit GUI is authoritative

## Known constraints

- Domain algorithms, visualization, and persistence semantics remain Project-owned.
- Installing `requirements.txt` remains an explicit local setup action.
- The `時間淘汰（60秒以上経過）` GUI action is currently invalid: it calls nonexistent `MemoryZone.prune_by_age()`, while the available pruning API is generation-based `prune_by_generation()`. Seconds and generations are not equivalent, so this remains open as repository Issue #5 until the intended semantic is defined.
- CI may emit Japanese-font warnings because the Linux runner does not provide the locally assumed `MS Gothic`; these warnings do not fail the current behavioral AppTest suite.

## Next work

1. Preserve the existing Streamlit implementation as a Project override.
2. Resolve Issue #5 only after choosing wall-clock-age or generation-age semantics for the pruning control.
3. Extend Project-specific behavioral tests when another real user path is repaired.
4. Consider further Default adoption only where it removes a real duplicate.

## Verification

- `knt doctor`
- `knt base-check`
- `knt test`
- `knt verify`
- `python -m unittest discover -s project/tests -v`

Current AppTest coverage exercises:
- `初回進化・発話` followed by `内的思考ループ実行` across Streamlit reruns without losing memory state;
- natural-language tag conversion/reactivation after a preceding memory-producing operation.
