# Project Specification

Status: active — first repository-local Base adoption

## Purpose

`Structured-Cell-Automaton` is a Streamlit GUI prototype for structured cell
syntax generation, extraction, evolution, scoring, and visualization.

## Acceptance

1. Existing Streamlit GUI and Domain behavior remains unchanged.
2. `knt doctor` validates the local Project Overlay and Base.
3. `knt base-check` detects changes to common Base files.
4. `knt dev` reaches the existing Streamlit entry point.
5. No Domain file is moved merely to satisfy the Base structure.

## Ownership boundary

- Streamlit UI, Domain algorithms, data files, persistence, and visualization
  remain in the existing repository root.
- KiNoTch Base files and repository operations live under `.kinotch/`.
- The Project Manifest, contracts, and adoption state live under `project/`.
- No generic Web, PWA, or Runtime helper is added to replace the Streamlit
  application.

## Commands

- Setup: `python -m pip install -r requirements.txt`
- Development: `streamlit run sca_gui.py`
- Verify: `knt verify` (no Project test command is currently registered)

## Constraints

The Base does not impose a Web framework, persistence format, visualization
model, or Runtime dependency on this Project. Existing implementation
boundaries remain authoritative.
