from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path

from core import Cell, Syntax

SNAPSHOT_SCHEMA = "sca-quicksave-v1"
_SAVE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
_GENERATION_PATTERN = re.compile(r"^[0-9a-f]{32}$")
_WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


class QuicksaveError(RuntimeError):
    pass


class InvalidSaveNameError(QuicksaveError, ValueError):
    pass

class SnapshotIntegrityError(QuicksaveError):
    pass


@dataclass(frozen=True)
class SnapshotSaveResult:
    save_name: str
    generation: str
    manifest_path: Path


def validate_save_name(value: object) -> str:
    if not isinstance(value, str) or not _SAVE_NAME_PATTERN.fullmatch(value):
        raise InvalidSaveNameError(
            "save name must be 1-128 ASCII letters/digits/_/-, starting with a letter or digit"
        )
    if value.upper() in _WINDOWS_RESERVED:
        raise InvalidSaveNameError("save name uses a reserved filesystem name")
    return value


def _resolved_root(save_root: Path | str, *, create: bool = False) -> Path:
    root = Path(save_root).resolve()
    if create:
        root.mkdir(parents=True, exist_ok=True)
    return root


def _safe_child(root: Path, filename: str) -> Path:
    candidate = root / filename
    resolved = candidate.resolve(strict=False)
    if candidate.parent != root or resolved.parent != root:
        raise SnapshotIntegrityError("quicksave path escapes the configured save root")
    return candidate


def manifest_path(save_root: Path | str, save_name: object) -> Path:
    name = validate_save_name(save_name)
    root = _resolved_root(save_root)
    return _safe_child(root, f"{name}_manifest.json")


def generation_paths(save_root: Path | str, save_name: object, generation: object) -> dict[str, Path]:
    name = validate_save_name(save_name)
    if not isinstance(generation, str) or not _GENERATION_PATTERN.fullmatch(generation):
        raise SnapshotIntegrityError("invalid quicksave generation identifier")
    root = _resolved_root(save_root)
    prefix = f"{name}__{generation}"
    return {
        "cells": _safe_child(root, f"{prefix}__cells.jsonl"),
        "syntax": _safe_child(root, f"{prefix}__syntax.jsonl"),
        "meta": _safe_child(root, f"{prefix}__meta.json"),
    }


def _json_line_bytes(items) -> bytes:
    text = "".join(json.dumps(item.__dict__, ensure_ascii=False) + "\n" for item in items)
    return text.encode("utf-8")


def _meta_bytes(meta: dict) -> bytes:
    return (json.dumps(meta, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _write_generation_file(path: Path, payload: bytes) -> None:
    try:
        with path.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        raise


def _atomic_write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def _publish_manifest(path: Path, manifest: dict) -> None:
    payload = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    _atomic_write_bytes(path, payload)


def save_snapshot(save_root, save_name, cells, syntaxes, meta_dict) -> SnapshotSaveResult:
    name = validate_save_name(save_name)
    root = _resolved_root(save_root, create=True)
    generation = uuid.uuid4().hex
    paths = generation_paths(root, name, generation)
    payloads = {
        "cells": _json_line_bytes(cells),
        "syntax": _json_line_bytes(syntaxes),
        "meta": _meta_bytes(dict(meta_dict)),
    }
    created: list[Path] = []
    try:
        for component in ("cells", "syntax", "meta"):
            _write_generation_file(paths[component], payloads[component])
            created.append(paths[component])
        manifest = {
            "schema": SNAPSHOT_SCHEMA,
            "save_name": name,
            "generation": generation,
            "sha256": {key: _sha256(value) for key, value in payloads.items()},
        }
        target = manifest_path(root, name)
        _publish_manifest(target, manifest)
        return SnapshotSaveResult(name, generation, target)
    except Exception:
        for path in created:
            path.unlink(missing_ok=True)
        raise


def _decode_lines(payload: bytes, cls, component: str):
    try:
        text = payload.decode("utf-8")
        return [cls(**json.loads(line)) for line in text.splitlines() if line.strip()]
    except (UnicodeError, json.JSONDecodeError, TypeError) as exc:
        raise SnapshotIntegrityError(f"invalid {component} data") from exc


def _decode_meta(payload: bytes) -> dict:
    try:
        data = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise SnapshotIntegrityError("invalid metadata") from exc
    if not isinstance(data, dict):
        raise SnapshotIntegrityError("metadata must be a JSON object")
    return data


def _is_finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _validate_string_list(value: object, label: str) -> None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise SnapshotIntegrityError(f"{label} must be a list of strings")


def _validate_snapshot_semantics(cells, syntaxes, meta: dict) -> None:
    cell_ids: set[str] = set()
    for index, cell in enumerate(cells):
        label = f"cells[{index}]"
        if not isinstance(cell.id, str) or not cell.id:
            raise SnapshotIntegrityError(f"{label}.id must be a non-empty string")
        if cell.id in cell_ids:
            raise SnapshotIntegrityError(f"duplicate Cell id: {cell.id}")
        cell_ids.add(cell.id)

        if (
            not isinstance(cell.position, (list, tuple))
            or len(cell.position) != 2
            or any(not _is_finite_number(value) for value in cell.position)
        ):
            raise SnapshotIntegrityError(
                f"{label}.position must contain exactly two finite numbers"
            )
        if cell.syntax_id is not None and not isinstance(cell.syntax_id, str):
            raise SnapshotIntegrityError(f"{label}.syntax_id must be a string or null")
        if not _is_finite_number(cell.activation):
            raise SnapshotIntegrityError(f"{label}.activation must be a finite number")
        _validate_string_list(cell.meaning_tags, f"{label}.meaning_tags")
        _validate_string_list(cell.history, f"{label}.history")

    syntax_ids: set[str] = set()
    for index, syntax in enumerate(syntaxes):
        label = f"syntax[{index}]"
        if not isinstance(syntax.sid, str) or not syntax.sid:
            raise SnapshotIntegrityError(f"{label}.sid must be a non-empty string")
        if syntax.sid in syntax_ids:
            raise SnapshotIntegrityError(f"duplicate Syntax sid: {syntax.sid}")
        syntax_ids.add(syntax.sid)

        _validate_string_list(syntax.cell_ids, f"{label}.cell_ids")
        missing_cell_ids = [cell_id for cell_id in syntax.cell_ids if cell_id not in cell_ids]
        if missing_cell_ids:
            raise SnapshotIntegrityError(
                f"{label}.cell_ids reference missing Cells: {missing_cell_ids}"
            )
        if not _is_finite_number(syntax.score):
            raise SnapshotIntegrityError(f"{label}.score must be a finite number")
        if syntax.meaning_cluster is not None and not isinstance(syntax.meaning_cluster, str):
            raise SnapshotIntegrityError(
                f"{label}.meaning_cluster must be a string or null"
            )
        if not _is_finite_number(syntax.created_at) or syntax.created_at < 0:
            raise SnapshotIntegrityError(
                f"{label}.created_at must be a non-negative finite number"
            )
        if syntax.parent_sid is not None and not isinstance(syntax.parent_sid, str):
            raise SnapshotIntegrityError(f"{label}.parent_sid must be a string or null")
        _validate_string_list(syntax.tags, f"{label}.tags")
        if (
            not isinstance(syntax.generation_stamp, int)
            or isinstance(syntax.generation_stamp, bool)
            or syntax.generation_stamp < 0
        ):
            raise SnapshotIntegrityError(
                f"{label}.generation_stamp must be a non-negative integer"
            )

    if "total_generations" in meta:
        total_generations = meta["total_generations"]
        if (
            not isinstance(total_generations, int)
            or isinstance(total_generations, bool)
            or total_generations < 0
        ):
            raise SnapshotIntegrityError(
                "metadata.total_generations must be a non-negative integer"
            )


def _load_manifest_snapshot(root: Path, name: str, path: Path):
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SnapshotIntegrityError("invalid quicksave manifest") from exc
    if not isinstance(manifest, dict) or manifest.get("schema") != SNAPSHOT_SCHEMA:
        raise SnapshotIntegrityError("unsupported quicksave manifest")
    if manifest.get("save_name") != name:
        raise SnapshotIntegrityError("quicksave manifest identity mismatch")
    generation = manifest.get("generation")
    paths = generation_paths(root, name, generation)
    hashes = manifest.get("sha256")
    if not isinstance(hashes, dict) or set(hashes) != {"cells", "syntax", "meta"}:
        raise SnapshotIntegrityError("quicksave manifest hashes are incomplete")
    payloads: dict[str, bytes] = {}
    for component, component_path in paths.items():
        try:
            payload = component_path.read_bytes()
        except OSError as exc:
            raise SnapshotIntegrityError(f"missing {component} generation file") from exc
        if _sha256(payload) != hashes.get(component):
            raise SnapshotIntegrityError(f"{component} generation hash mismatch")
        payloads[component] = payload
    cells = _decode_lines(payloads["cells"], Cell, "cells")
    syntaxes = _decode_lines(payloads["syntax"], Syntax, "syntax")
    meta = _decode_meta(payloads["meta"])
    return cells, syntaxes, meta


def _legacy_paths(root: Path, name: str) -> dict[str, Path]:
    return {
        "cells": _safe_child(root, f"{name}_cells.jsonl"),
        "syntax": _safe_child(root, f"{name}_syntax.jsonl"),
        "meta": _safe_child(root, f"{name}_meta.json"),
    }


def _load_legacy_snapshot(root: Path, name: str):
    paths = _legacy_paths(root, name)
    if not paths["cells"].is_file() or not paths["syntax"].is_file():
        raise FileNotFoundError(name)
    cells = load_cells_from_jsonl(paths["cells"])
    syntaxes = load_syntaxes_from_jsonl(paths["syntax"])
    meta = load_metadata(paths["meta"]) if paths["meta"].is_file() else {}
    return cells, syntaxes, meta


def load_snapshot(save_root, save_name):
    name = validate_save_name(save_name)
    root = _resolved_root(save_root)
    target = manifest_path(root, name)
    if target.is_file():
        snapshot = _load_manifest_snapshot(root, name, target)
    else:
        snapshot = _load_legacy_snapshot(root, name)
    _validate_snapshot_semantics(*snapshot)
    return snapshot


def save_cells_to_jsonl(cells, filepath):
    _atomic_write_bytes(Path(filepath), _json_line_bytes(cells))


def load_cells_from_jsonl(filepath):
    path = Path(filepath)
    try:
        return _decode_lines(path.read_bytes(), Cell, "cells")
    except OSError:
        raise


def save_syntaxes_to_jsonl(syntaxes, filepath):
    _atomic_write_bytes(Path(filepath), _json_line_bytes(syntaxes))


def load_syntaxes_from_jsonl(filepath):
    path = Path(filepath)
    try:
        return _decode_lines(path.read_bytes(), Syntax, "syntax")
    except OSError:
        raise


def save_metadata(filepath, meta_dict):
    _atomic_write_bytes(Path(filepath), _meta_bytes(dict(meta_dict)))


def load_metadata(filepath):
    path = Path(filepath)
    try:
        return _decode_meta(path.read_bytes())
    except OSError:
        raise
