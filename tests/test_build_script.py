import importlib.util
from pathlib import Path


BUILD_SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build.py"
SPEC = importlib.util.spec_from_file_location("sortify_build_script", BUILD_SCRIPT_PATH)
build_script = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(build_script)


def test_resolve_windows_icon_prefers_valid_ico(tmp_path, monkeypatch):
    icons_dir = tmp_path / "icons"
    icons_dir.mkdir()
    (icons_dir / "sortify.ico").write_bytes(build_script.ICO_HEADER + b"fake-ico")
    (icons_dir / "sortify.png").write_bytes(build_script.PNG_HEADER + b"fake-png")

    monkeypatch.setattr(build_script, "ROOT", tmp_path)

    assert build_script.resolve_windows_icon() == "icons/sortify.ico"


def test_resolve_windows_icon_falls_back_to_png_when_ico_is_mislabeled(
    tmp_path, monkeypatch
):
    icons_dir = tmp_path / "icons"
    icons_dir.mkdir()
    (icons_dir / "sortify.ico").write_bytes(build_script.PNG_HEADER + b"not-an-ico")
    (icons_dir / "sortify.png").write_bytes(build_script.PNG_HEADER + b"real-png")

    monkeypatch.setattr(build_script, "ROOT", tmp_path)

    assert build_script.resolve_windows_icon() == "icons/sortify.png"
