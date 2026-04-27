from pathlib import Path

import core


def _make_config():
    return {
        "categories": {"Documentos": [".txt"]},
        "ignored_extensions": [".tmp"],
        "ignored_names": ["desktop.ini"],
        "custom_rules": [],
        "monitored_folders": [],
        "organize_mode": "extension",
        "date_subfolder": False,
        "notifications_enabled": False,
        "minimize_to_tray": False,
    }


def test_find_duplicates_moves_only_duplicate_files(tmp_path: Path):
    base = tmp_path / "workspace"
    base.mkdir()

    (base / "a.txt").write_text("same-content", encoding="utf-8")
    (base / "b.txt").write_text("same-content", encoding="utf-8")
    (base / "c.txt").write_text("different", encoding="utf-8")

    records = core.find_duplicates(str(base), _make_config())
    dup_dir = base / "Duplicados"

    assert len(records) == 1
    assert dup_dir.exists()
    moved_names = {Path(r["to"]).name for r in records}
    assert moved_names == {"b.txt"}
    assert (base / "a.txt").exists()
    assert (base / "c.txt").exists()


def test_find_duplicates_ignores_existing_duplicates_folder(tmp_path: Path):
    base = tmp_path / "workspace"
    base.mkdir()

    (base / "orig.txt").write_text("same-content", encoding="utf-8")
    dup_dir = base / "Duplicados"
    dup_dir.mkdir()
    (dup_dir / "old.txt").write_text("same-content", encoding="utf-8")

    records = core.find_duplicates(str(base), _make_config())

    assert records == []
    assert (dup_dir / "old.txt").exists()
