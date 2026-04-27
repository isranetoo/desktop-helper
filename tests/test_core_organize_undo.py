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
    assert data["version"] == core.UNDO_FILE_VERSION
    assert isinstance(data["entries"], list)
    assert data["entries"][-1]["actions"] == records


def test_undo_supports_multiple_operations(tmp_path: Path, monkeypatch):
    base = tmp_path / "downloads"
    base.mkdir()

    first = base / "primeiro.pdf"
    first.write_text("1", encoding="utf-8")

    undo_file = tmp_path / "undo_history.json"
    monkeypatch.setattr(core, "UNDO_PATH", undo_file)

    cfg = _make_config()
    core.organize_folder(str(base), cfg)
    assert (base / "PDFs" / "primeiro.pdf").exists()

    second = base / "segundo.jpg"
    second.write_text("2", encoding="utf-8")
    core.organize_folder(str(base), cfg)
    assert (base / "Imagens" / "segundo.jpg").exists()

    # desfaz apenas a segunda organização
    restored_second = core.undo_last_organization()
    assert restored_second == 1
    assert (base / "segundo.jpg").exists()
    assert (base / "PDFs" / "primeiro.pdf").exists()

    # desfaz a primeira organização
    restored_first = core.undo_last_organization()
    assert restored_first == 1
    assert (base / "primeiro.pdf").exists()


def test_load_undo_stack_supports_legacy_file(tmp_path: Path, monkeypatch):
    undo_file = tmp_path / "undo_history.json"
    monkeypatch.setattr(core, "UNDO_PATH", undo_file)
    legacy = {
        "timestamp": "2026-04-27T12:00:00",
        "actions": [{"from": "/tmp/a", "to": "/tmp/b"}],
    }
    undo_file.write_text(json.dumps(legacy), encoding="utf-8")

    stack = core.load_undo_stack()
    assert len(stack) == 1
    assert stack[0]["actions"] == legacy["actions"]
