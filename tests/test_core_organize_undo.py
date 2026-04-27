import json
from pathlib import Path

import core


def _make_config():
    return {
        "categories": {"PDFs": [".pdf"], "Imagens": [".jpg"]},
        "ignored_extensions": [".tmp"],
        "ignored_names": ["desktop.ini"],
        "custom_rules": [],
        "monitored_folders": [],
        "organize_mode": "extension",
        "date_subfolder": False,
        "notifications_enabled": False,
        "minimize_to_tray": False,
    }


def test_organize_folder_and_undo(tmp_path: Path, monkeypatch):
    base = tmp_path / "downloads"
    base.mkdir()
    (base / "a.pdf").write_text("pdf", encoding="utf-8")
    (base / "b.jpg").write_text("img", encoding="utf-8")
    (base / "temp.tmp").write_text("tmp", encoding="utf-8")

    undo_file = tmp_path / "undo_history.json"
    monkeypatch.setattr(core, "UNDO_PATH", undo_file)

    records = core.organize_folder(str(base), _make_config())
    assert len(records) == 2
    assert (base / "PDFs" / "a.pdf").exists()
    assert (base / "Imagens" / "b.jpg").exists()
    assert (base / "temp.tmp").exists()
    assert undo_file.exists()

    restored = core.undo_last_organization()
    assert restored == 2
    assert (base / "a.pdf").exists()
    assert (base / "b.jpg").exists()
    assert not undo_file.exists()


def test_save_undo_history_writes_expected_structure(tmp_path: Path, monkeypatch):
    undo_file = tmp_path / "undo_history.json"
    monkeypatch.setattr(core, "UNDO_PATH", undo_file)
    records = [{"from": "/tmp/a.txt", "to": "/tmp/Docs/a.txt"}]

    core.save_undo_history(records)

    data = json.loads(undo_file.read_text(encoding="utf-8"))
    assert "timestamp" in data
    assert data["actions"] == records
