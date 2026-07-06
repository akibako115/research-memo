#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

PROJECT_ROOT_MARKER = ".projectroot"


def find_project_root(start: Path | None = None) -> Path:
    current = (start or Path(__file__)).resolve()
    for parent in (current, *current.parents):
        if (parent / PROJECT_ROOT_MARKER).is_file():
            return parent
    raise FileNotFoundError(f"Could not find {PROJECT_ROOT_MARKER} from {current}")


ROOT = find_project_root()
MANIFEST_PATH = ROOT / "wiki/index/raw_units.json"
RAW_DIR = ROOT / "raw"
SOURCES_DIR = ROOT / "wiki/sources"


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        return {"ignore_files": [".gitkeep"], "grouped_units": []}
    return json.loads(MANIFEST_PATH.read_text())


def frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(errors="ignore")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}

    result: dict[str, object] = {}
    current_list_key: str | None = None
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        list_item = re.match(r"^\s*-\s+(.+?)\s*$", line)
        if list_item and current_list_key:
            result.setdefault(current_list_key, [])
            assert isinstance(result[current_list_key], list)
            result[current_list_key].append(unquote(list_item.group(1)))
            continue

        key_value = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:\s*(.*))?$", line)
        if not key_value:
            current_list_key = None
            continue
        key, value = key_value.group(1), (key_value.group(2) or "").strip()
        if value == "":
            result[key] = []
            current_list_key = key
        else:
            result[key] = unquote(value)
            current_list_key = None
    return result


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def norm_raw(path: str) -> str:
    path = path.strip()
    if path.startswith("./"):
        path = path[2:]
    return path


def key(path: str) -> str:
    return unicodedata.normalize("NFC", path)


def is_inside(path: str, folder: str) -> bool:
    folder = folder.rstrip("/") + "/"
    return path.startswith(folder)


def raw_files(ignore_files: set[str]) -> list[str]:
    files: list[str] = []
    for path in RAW_DIR.rglob("*"):
        if not path.is_file():
            continue
        if path.name in ignore_files:
            continue
        files.append(rel(path))
    return sorted(files)


def source_frontmatters() -> list[tuple[str, dict[str, object]]]:
    result: list[tuple[str, dict[str, object]]] = []
    for path in sorted(SOURCES_DIR.glob("*.md")):
        if path.name in {"README.md", "AGENTS.md"}:
            continue
        result.append((rel(path), frontmatter(path)))
    return result


def main() -> int:
    manifest = load_manifest()
    ignore_files = set(manifest.get("ignore_files", []))
    grouped_units = manifest.get("grouped_units", [])

    groups = []
    for group in grouped_units:
        raw = norm_raw(group["raw"]).rstrip("/") + "/"
        groups.append({**group, "raw": raw})

    files = raw_files(ignore_files)
    sources = source_frontmatters()

    display_paths = {key(file_path): file_path for file_path in files}
    covered_files: dict[str, list[str]] = {}
    covered_groups: dict[str, list[str]] = {}
    warnings: list[str] = []
    missing_raw_refs: list[str] = []

    for source_path, fm in sources:
        raw_value = fm.get("raw")
        if not isinstance(raw_value, str):
            warnings.append(f"{source_path}: missing raw frontmatter")
            continue
        raw_value = norm_raw(raw_value)

        matching_group = next(
            (g for g in groups if raw_value.rstrip("/") + "/" == g["raw"]), None
        )
        if matching_group:
            covered_groups.setdefault(key(matching_group["raw"]), []).append(
                source_path
            )
            scope = fm.get("scope")
            if isinstance(scope, list):
                for item in scope:
                    if not isinstance(item, str):
                        continue
                    file_path = matching_group["raw"] + item.lstrip("/")
                    covered_files.setdefault(key(file_path), []).append(source_path)
            else:
                group_files = [f for f in files if is_inside(f, matching_group["raw"])]
                for file_path in group_files:
                    covered_files.setdefault(key(file_path), []).append(source_path)
            continue

        file_group = next((g for g in groups if is_inside(raw_value, g["raw"])), None)
        if file_group:
            covered_files.setdefault(key(raw_value), []).append(source_path)
            warnings.append(
                f"{source_path}: raw points inside grouped unit {file_group['raw']}; "
                "prefer raw: group folder + scope:"
            )
            continue

        if (ROOT / raw_value).exists():
            covered_files.setdefault(key(raw_value), []).append(source_path)
        else:
            raw_key = key(raw_value)
            if raw_key in display_paths:
                covered_files.setdefault(raw_key, []).append(source_path)
            else:
                missing_raw_refs.append(f"{source_path}: {raw_value}")

    grouped_file_set = set()
    excluded_group_files = set()
    for group in groups:
        group_ignored = set(group.get("ignore_files", []))
        for file_path in files:
            if not is_inside(file_path, group["raw"]):
                continue
            if Path(file_path).name in group_ignored:
                excluded_group_files.add(file_path)
                continue
            grouped_file_set.add(file_path)
    ungrouped_files = [
        f for f in files if f not in grouped_file_set and f not in excluded_group_files
    ]
    uncovered_ungrouped = [f for f in ungrouped_files if key(f) not in covered_files]
    uncovered_grouped = [
        f for f in sorted(grouped_file_set) if key(f) not in covered_files
    ]

    duplicate_refs = {
        display_paths.get(raw, raw): refs
        for raw, refs in sorted(covered_files.items())
        if len(refs) > 1
    }

    print("raw/source lint")
    print(f"- raw files: {len(files)}")
    print(f"- source files: {len(sources)}")
    print(f"- grouped units: {len(groups)}")
    print()

    print("uncovered raw files")
    if uncovered_ungrouped:
        for item in uncovered_ungrouped:
            print(f"- {item}")
    else:
        print("- none")
    print()

    print("uncovered grouped files")
    if uncovered_grouped:
        for item in uncovered_grouped:
            print(f"- {item}")
    else:
        print("- none")
    print()

    print("missing raw references")
    if missing_raw_refs:
        for item in missing_raw_refs:
            print(f"- {item}")
    else:
        print("- none")
    print()

    print("duplicate raw references")
    if duplicate_refs:
        for raw, refs in duplicate_refs.items():
            print(f"- {raw}: {', '.join(refs)}")
    else:
        print("- none")
    print()

    print("warnings")
    if warnings:
        for item in warnings:
            print(f"- {item}")
    else:
        print("- none")

    return 1 if (uncovered_ungrouped or missing_raw_refs or duplicate_refs) else 0


if __name__ == "__main__":
    sys.exit(main())
