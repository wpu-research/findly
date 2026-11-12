import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from export_findly_conversation import export_conversation


ROOT = Path(__file__).resolve().parents[1]
PROTECTED = {".git", ".agents", ".codex", ".aws"}


def checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_exact(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if checksum(source) != checksum(destination):
            raise FileExistsError(f"Different file already exists: {destination}")
    else:
        shutil.copy2(source, destination)
    if checksum(source) != checksum(destination):
        raise ValueError(f"Copy verification failed: {source}")


def prepare_sources():
    source_folder = Path.home() / "Downloads" / "Findly"
    imported = []
    for source in sorted(source_folder.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(source_folder)
        if source.name == "findy-yatirimci-sunumu-v2.html" and (ROOT / source.name).exists() and checksum(source) == checksum(ROOT / source.name):
            destination = ROOT / source.name
        elif source.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".avif"}:
            destination = ROOT / "assets" / "images" / relative
        elif source.suffix.lower() in {".mp4", ".mov", ".webm", ".mkv"}:
            destination = ROOT / "assets" / "videos" / relative
        else:
            destination = ROOT / "references" / relative
        copy_exact(source, destination)
        imported.append({"source": str(source), "relative_path": destination.relative_to(ROOT).as_posix(), "bytes": destination.stat().st_size, "sha256": checksum(destination)})
    if len(imported) < 10:
        raise ValueError("Expected all ten files from Downloads/Findly")
    previews = Path("/tmp/findy-deck-preview")
    if previews.is_dir():
        for source in sorted(previews.rglob("*")):
            if source.is_file():
                copy_exact(source, ROOT / "validation" / "original" / source.relative_to(previews))
    copy_exact(Path.home() / ".codex" / "RTK.md", ROOT / "docs" / "RTK.md")
    copy_exact(Path.home() / "AGENTS.md", ROOT / "docs" / "original-project-instructions.md")
    (ROOT / "docs" / "source-media-manifest.json").write_text(json.dumps(imported, ensure_ascii=False, indent=2), encoding="utf-8")
    return imported


def move_project(destination):
    destination = destination.absolute()
    if destination == ROOT or ROOT in destination.parents or destination in ROOT.parents:
        raise ValueError("Destination must be a separate sibling project folder")
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError(f"Refusing to merge into nonempty destination: {destination}")
    manifest = []
    for source in sorted(ROOT.rglob("*")):
        relative = source.relative_to(ROOT)
        if relative.parts[0] in PROTECTED or not source.is_file() or source.is_symlink():
            continue
        manifest.append({"path": relative.as_posix(), "bytes": source.stat().st_size, "sha256": checksum(source)})
    destination.mkdir(parents=True, exist_ok=True)
    moved = []
    try:
        for source in sorted(ROOT.iterdir()):
            if source.name in PROTECTED:
                continue
            shutil.move(str(source), str(destination / source.name))
            moved.append(source.name)
        for record in manifest:
            relocated = destination / record["path"]
            if not relocated.is_file() or relocated.stat().st_size != record["bytes"] or checksum(relocated) != record["sha256"]:
                raise ValueError(f"Relocated-file verification failed: {record['path']}")
    except Exception:
        for name in reversed(moved):
            if not (ROOT / name).exists():
                shutil.move(str(destination / name), str(ROOT / name))
        raise
    result = {
        "moved_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(ROOT),
        "destination": str(destination),
        "files_verified": len(manifest),
        "total_bytes": sum(record["bytes"] for record in manifest),
        "protected_source_entries_untouched": sorted(PROTECTED),
        "downloads_sources_preserved": True,
        "files": manifest,
    }
    (destination / "docs" / "migration-manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return {key: value for key, value in result.items() if key != "files"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--destination", type=Path)
    arguments = parser.parse_args()
    if arguments.prepare:
        imported = prepare_sources()
        conversation = export_conversation(ROOT)
        print(json.dumps({"imported_files": len(imported), "conversation": conversation}, ensure_ascii=False, indent=2))
    elif arguments.destination:
        export_conversation(ROOT)
        print(json.dumps(move_project(arguments.destination), ensure_ascii=False, indent=2))
    else:
        parser.error("Choose --prepare or --destination")


if __name__ == "__main__":
    main()
