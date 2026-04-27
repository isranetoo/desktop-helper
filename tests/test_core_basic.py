from pathlib import Path

import core


def test_should_ignore_case_insensitive_name():
    config = {
        "ignored_extensions": [".tmp"],
        "ignored_names": ["Thumbs.db"],
    }

    assert core.should_ignore("THUMBS.DB", config) is True
    assert core.should_ignore("arquivo.tmp", config) is True
    assert core.should_ignore("documento.pdf", config) is False


def test_get_destination_folder_with_custom_rule():
    config = {
        "categories": {"PDFs": [".pdf"]},
        "custom_rules": [
            {
                "name": "Notas",
                "destination": "Notas Fiscais",
                "conditions": {"extension": ".pdf", "name_contains": "nota"},
            }
        ],
    }

    assert core.get_destination_folder("nota_abril.pdf", config) == "Notas Fiscais"
    assert core.get_destination_folder("arquivo.pdf", config) == "PDFs"
    assert core.get_destination_folder("sem_ext", config) == "Outros"


def test_validate_config_normalizes_types():
    config = {
        "categories": {"Imagens": ["JPG", ".PNG", 123]},
        "ignored_extensions": ["tmp", ".PART", None],
        "ignored_names": ["desktop.ini", "", None],
        "custom_rules": [
            {
                "name": "Regra PDF",
                "destination": "Notas",
                "conditions": {"extension": "PDF", "name_contains": "nota"},
            }
        ],
        "date_subfolder": True,
        "notifications_enabled": False,
    }

    validated = core.validate_config(config)

    assert validated["categories"]["Imagens"] == [".jpg", ".png"]
    assert validated["ignored_extensions"] == [".part", ".tmp"]
    assert validated["ignored_names"] == ["desktop.ini"]
    assert validated["custom_rules"][0]["conditions"]["extension"] == ".pdf"
    assert validated["date_subfolder"] is True
    assert validated["notifications_enabled"] is False


def test_load_config_fallback_on_invalid_json(tmp_path: Path, monkeypatch):
    invalid_cfg = tmp_path / "config.json"
    invalid_cfg.write_text("{invalid", encoding="utf-8")

    monkeypatch.setattr(core, "CONFIG_PATH", invalid_cfg)
    loaded = core.load_config()

    assert loaded["categories"]
    assert invalid_cfg.exists()
