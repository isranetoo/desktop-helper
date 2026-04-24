"""
core.py — Lógica central do organizador de arquivos.

Responsabilidades:
  - Carregar/salvar configuração (config.json)
  - Mover arquivos por extensão ou por data
  - Aplicar regras personalizadas
  - Modo simulação (dry-run)
  - Desfazer última organização
  - Detectar duplicados
  - Logging em arquivo
  - Notificações do sistema
"""

import os
import json
import time
import shutil
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable

# ==========================================
# CONSTANTES
# ==========================================
APP_DIR = Path(__file__).parent
CONFIG_PATH = APP_DIR / "config.json"
UNDO_PATH = APP_DIR / "undo_history.json"
LOGS_DIR = APP_DIR / "logs"

DOWNLOADS_PATH = str(Path.home() / "Downloads")
DESKTOP_PATH = str(Path.home() / "Desktop")

MONTH_NAMES_PT = {
    1: "01-Janeiro", 2: "02-Fevereiro", 3: "03-Marco",
    4: "04-Abril", 5: "05-Maio", 6: "06-Junho",
    7: "07-Julho", 8: "08-Agosto", 9: "09-Setembro",
    10: "10-Outubro", 11: "11-Novembro", 12: "12-Dezembro",
}


# ==========================================
# CONFIGURAÇÃO
# ==========================================
DEFAULT_CONFIG = {
    "categories": {
        "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"],
        "PDFs": [".pdf"],
        "Documentos": [".doc", ".docx", ".txt", ".odt", ".rtf"],
        "Planilhas": [".xls", ".xlsx", ".csv"],
        "Apresentacoes": [".ppt", ".pptx"],
        "Compactados": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "Executaveis": [".exe", ".msi"],
        "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
        "Audios": [".mp3", ".wav", ".flac", ".aac"],
        "Codigos": [".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".java", ".cpp"],
    },
    "ignored_extensions": [".lnk", ".ini", ".url"],
    "ignored_names": ["desktop.ini", "Thumbs.db", ".DS_Store"],
    "custom_rules": [],
    "monitored_folders": [],
    "organize_mode": "extension",
    "date_subfolder": False,
    "notifications_enabled": True,
    "minimize_to_tray": False,
}


def load_config() -> dict:
    """Carrega config.json ou cria com valores padrão."""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            # Mescla com defaults para garantir que chaves novas existam
            for key, value in DEFAULT_CONFIG.items():
                cfg.setdefault(key, value)
            return cfg
        except (json.JSONDecodeError, Exception):
            pass
    save_config(DEFAULT_CONFIG)
    return dict(DEFAULT_CONFIG)


def save_config(config: dict) -> None:
    """Salva config.json."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


# ==========================================
# LOGGING EM ARQUIVO
# ==========================================
def setup_file_logger() -> logging.Logger:
    """Configura logger que salva em arquivo diário."""
    LOGS_DIR.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"organizador_{today}.log"

    logger = logging.getLogger("organizador")
    logger.setLevel(logging.DEBUG)

    # Evita handlers duplicados
    if not logger.handlers:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fmt = logging.Formatter("[%(asctime)s] %(levelname)s — %(message)s", "%H:%M:%S")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger


file_logger = setup_file_logger()


# ==========================================
# NOTIFICAÇÕES
# ==========================================
def send_notification(title: str, message: str) -> None:
    """Envia notificação do sistema (Windows/Linux/macOS)."""
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name="Organizador de Arquivos",
            timeout=5,
        )
    except ImportError:
        pass
    except Exception:
        pass


# ==========================================
# RESOLUÇÃO DE DESTINO
# ==========================================
def match_custom_rule(filename: str, config: dict) -> Optional[str]:
    """
    Verifica se o arquivo bate com alguma regra personalizada.
    Retorna o nome da pasta destino ou None.
    """
    _, ext = os.path.splitext(filename.lower())
    name_lower = filename.lower()

    for rule in config.get("custom_rules", []):
        conditions = rule.get("conditions", {})
        match = True

        if "extension" in conditions:
            rule_ext = conditions["extension"]
            if isinstance(rule_ext, list):
                if ext not in rule_ext:
                    match = False
            elif ext != rule_ext:
                match = False

        if "name_contains" in conditions:
            if conditions["name_contains"].lower() not in name_lower:
                match = False

        if "name_starts_with" in conditions:
            if not name_lower.startswith(conditions["name_starts_with"].lower()):
                match = False

        if match:
            return rule.get("destination", "Outros")

    return None


def get_destination_folder(filename: str, config: dict) -> str:
    """Retorna o nome da pasta de destino com base nas regras e extensão."""
    # Primeiro tenta regras personalizadas
    rule_match = match_custom_rule(filename, config)
    if rule_match:
        return rule_match

    # Depois tenta por extensão
    _, ext = os.path.splitext(filename.lower())
    for folder_name, extensions in config.get("categories", {}).items():
        if ext in extensions:
            return folder_name

    return "Outros"


def build_date_subfolder(file_path: str) -> str:
    """Retorna subpasta baseada na data de modificação do arquivo."""
    try:
        mtime = os.path.getmtime(file_path)
        dt = datetime.fromtimestamp(mtime)
        month_name = MONTH_NAMES_PT.get(dt.month, f"{dt.month:02d}")
        return os.path.join(str(dt.year), month_name)
    except Exception:
        return ""


# ==========================================
# UTILITÁRIOS DE ARQUIVO
# ==========================================
def should_ignore(filename: str, config: dict) -> bool:
    """Verifica se o arquivo deve ser ignorado."""
    _, ext = os.path.splitext(filename.lower())

    ignored_exts = config.get("ignored_extensions", [])
    ignored_names = config.get("ignored_names", [])
    temp_suffixes = (".crdownload", ".tmp", ".part", ".download")

    if filename.startswith("~"):
        return True
    if filename in ignored_names:
        return True
    if ext in ignored_exts:
        return True
    if filename.endswith(temp_suffixes):
        return True

    return False


def ensure_folder_exists(base_path: str, folder_name: str) -> str:
    dest = os.path.join(base_path, folder_name)
    os.makedirs(dest, exist_ok=True)
    return dest


def generate_safe_name(destination_dir: str, filename: str) -> str:
    base_name, ext = os.path.splitext(filename)
    candidate = filename
    counter = 1
    while os.path.exists(os.path.join(destination_dir, candidate)):
        candidate = f"{base_name} ({counter}){ext}"
        counter += 1
    return candidate


def file_hash(filepath: str, chunk_size: int = 8192) -> str:
    """Calcula hash MD5 de um arquivo."""
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


# ==========================================
# SIMULAÇÃO
# ==========================================
def simulate_organization(
    folder_path: str,
    config: dict,
    logger: Optional[Callable] = None,
) -> list[dict]:
    """
    Simula a organização sem mover nada.
    Retorna lista de ações planejadas.
    """
    actions = []

    if not os.path.exists(folder_path):
        return actions

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if not os.path.isfile(item_path):
            continue
        if should_ignore(item, config):
            continue

        folder_name = get_destination_folder(item, config)

        # Subpasta por data
        date_sub = ""
        if config.get("date_subfolder"):
            date_sub = build_date_subfolder(item_path)

        if date_sub:
            full_folder = os.path.join(folder_name, date_sub)
        else:
            full_folder = folder_name

        action = {
            "filename": item,
            "from": item_path,
            "destination_folder": full_folder,
            "to": os.path.join(folder_path, full_folder, item),
        }
        actions.append(action)

        if logger:
            logger(f"🔍 {item} → {full_folder}/")

    if logger:
        logger(f"📊 Total: {len(actions)} arquivo(s) seriam movidos.")

    return actions


# ==========================================
# MOVER ARQUIVO
# ==========================================
def move_file(
    file_path: str,
    base_destination: str,
    config: dict,
    logger: Optional[Callable] = None,
    notify: bool = False,
) -> Optional[dict]:
    """
    Move um arquivo para a pasta correta.
    Retorna dict com origem/destino para undo, ou None.
    """
    if not os.path.isfile(file_path):
        return None

    filename = os.path.basename(file_path)

    if should_ignore(filename, config):
        return None

    folder_name = get_destination_folder(filename, config)

    # Subpasta por data
    if config.get("date_subfolder"):
        date_sub = build_date_subfolder(file_path)
        if date_sub:
            folder_name = os.path.join(folder_name, date_sub)

    destination_dir = ensure_folder_exists(base_destination, folder_name)
    safe_filename = generate_safe_name(destination_dir, filename)
    destination_file = os.path.join(destination_dir, safe_filename)

    try:
        shutil.move(file_path, destination_file)

        record = {"from": file_path, "to": destination_file}

        msg = f"✅ {filename} → {folder_name}/"
        if logger:
            logger(msg)
        file_logger.info(f"MOVIDO: {file_path} -> {destination_file}")

        if notify and config.get("notifications_enabled"):
            send_notification("Arquivo organizado", f"{filename} → {folder_name}/")

        return record

    except PermissionError:
        msg = f"⚠️ Arquivo em uso: {filename}"
        if logger:
            logger(msg)
        file_logger.warning(f"EM USO: {file_path}")

    except Exception as e:
        msg = f"❌ Erro ao mover {filename}: {e}"
        if logger:
            logger(msg)
        file_logger.error(f"ERRO: {file_path} — {e}")

    return None


# ==========================================
# ORGANIZAR PASTA COMPLETA
# ==========================================
def organize_folder(
    folder_path: str,
    config: dict,
    logger: Optional[Callable] = None,
    progress_callback: Optional[Callable] = None,
    notify: bool = False,
) -> list[dict]:
    """
    Organiza todos os arquivos de uma pasta.
    Retorna lista de registros para undo.
    """
    if not os.path.exists(folder_path):
        if logger:
            logger(f"❌ Pasta não encontrada: {folder_path}")
        return []

    if logger:
        logger(f"📁 Organizando: {folder_path}")

    files = [
        f for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]
    total = len(files)
    records = []
    moved = 0
    ignored = 0
    errors = 0

    for i, item in enumerate(files):
        item_path = os.path.join(folder_path, item)

        if should_ignore(item, config):
            ignored += 1
            if progress_callback:
                progress_callback(i + 1, total)
            continue

        record = move_file(item_path, folder_path, config, logger=logger, notify=notify)

        if record:
            records.append(record)
            moved += 1
        else:
            if os.path.isfile(item_path):
                errors += 1

        if progress_callback:
            progress_callback(i + 1, total)

    if logger:
        logger(f"✨ Concluído: {moved} movidos, {ignored} ignorados, {errors} erros.")

    # Salvar histórico para undo
    if records:
        save_undo_history(records)

    file_logger.info(
        f"ORGANIZAÇÃO: {folder_path} — {moved} movidos, {ignored} ignorados, {errors} erros"
    )

    return records


# ==========================================
# UNDO
# ==========================================
def save_undo_history(records: list[dict]) -> None:
    """Salva histórico de ações para desfazer."""
    history = {
        "timestamp": datetime.now().isoformat(),
        "actions": records,
    }
    with open(UNDO_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def load_undo_history() -> Optional[dict]:
    """Carrega o histórico de undo."""
    if not UNDO_PATH.exists():
        return None
    try:
        with open(UNDO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def undo_last_organization(
    logger: Optional[Callable] = None,
    progress_callback: Optional[Callable] = None,
) -> int:
    """
    Desfaz a última organização.
    Retorna o número de arquivos restaurados.
    """
    history = load_undo_history()
    if not history:
        if logger:
            logger("⚠️ Nenhum histórico de organização encontrado.")
        return 0

    actions = history.get("actions", [])
    if not actions:
        if logger:
            logger("⚠️ Histórico vazio.")
        return 0

    ts = history.get("timestamp", "desconhecido")
    if logger:
        logger(f"⏪ Desfazendo organização de {ts}...")

    restored = 0
    total = len(actions)

    for i, action in enumerate(reversed(actions)):
        src = action["to"]
        dst = action["from"]

        try:
            if os.path.exists(src):
                dst_dir = os.path.dirname(dst)
                os.makedirs(dst_dir, exist_ok=True)
                shutil.move(src, dst)
                restored += 1
                if logger:
                    logger(f"↩️ {os.path.basename(src)} restaurado")
                file_logger.info(f"UNDO: {src} -> {dst}")
            else:
                if logger:
                    logger(f"⚠️ Arquivo não encontrado: {os.path.basename(src)}")
        except Exception as e:
            if logger:
                logger(f"❌ Erro ao restaurar {os.path.basename(src)}: {e}")
            file_logger.error(f"UNDO ERRO: {src} — {e}")

        if progress_callback:
            progress_callback(i + 1, total)

    # Limpa pastas vazias que sobraram
    _cleanup_empty_dirs(actions)

    # Remove o histórico após desfazer
    if UNDO_PATH.exists():
        UNDO_PATH.unlink()

    if logger:
        logger(f"✨ Restauração concluída: {restored}/{total} arquivos.")

    return restored


def _cleanup_empty_dirs(actions: list[dict]) -> None:
    """Remove pastas vazias criadas pela organização."""
    dirs_to_check = set()
    for action in actions:
        d = os.path.dirname(action["to"])
        dirs_to_check.add(d)
        # Também checa o pai (para subpastas de data)
        parent = os.path.dirname(d)
        dirs_to_check.add(parent)

    for d in sorted(dirs_to_check, key=len, reverse=True):
        try:
            if os.path.isdir(d) and not os.listdir(d):
                os.rmdir(d)
        except Exception:
            pass


# ==========================================
# DETECÇÃO DE DUPLICADOS
# ==========================================
def find_duplicates(
    folder_path: str,
    config: dict,
    logger: Optional[Callable] = None,
    progress_callback: Optional[Callable] = None,
) -> list[dict]:
    """
    Detecta arquivos duplicados por hash MD5.
    Retorna lista de registros movidos para Duplicados/.
    """
    if not os.path.exists(folder_path):
        if logger:
            logger(f"❌ Pasta não encontrada: {folder_path}")
        return []

    if logger:
        logger(f"🔎 Buscando duplicados em: {folder_path}")

    # Coleta todos os arquivos recursivamente
    all_files = []
    for root, _, files in os.walk(folder_path):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.isfile(fp) and not should_ignore(f, config):
                all_files.append(fp)

    total = len(all_files)
    hash_map: dict[str, str] = {}
    duplicates = []
    records = []

    for i, fp in enumerate(all_files):
        if progress_callback:
            progress_callback(i + 1, total)

        try:
            h = file_hash(fp)
        except Exception:
            continue

        if h in hash_map:
            duplicates.append((fp, hash_map[h]))
        else:
            hash_map[h] = fp

    if not duplicates:
        if logger:
            logger("✅ Nenhum duplicado encontrado.")
        return []

    if logger:
        logger(f"⚠️ {len(duplicates)} duplicado(s) encontrado(s).")

    dup_dir = ensure_folder_exists(folder_path, "Duplicados")

    for dup_path, original_path in duplicates:
        filename = os.path.basename(dup_path)
        safe_name = generate_safe_name(dup_dir, filename)
        dest = os.path.join(dup_dir, safe_name)

        try:
            shutil.move(dup_path, dest)
            records.append({"from": dup_path, "to": dest})
            if logger:
                orig_name = os.path.basename(original_path)
                logger(f"📄 {filename} (duplicado de {orig_name}) → Duplicados/")
            file_logger.info(f"DUPLICADO: {dup_path} -> {dest} (original: {original_path})")
        except Exception as e:
            if logger:
                logger(f"❌ Erro ao mover duplicado {filename}: {e}")

    if records:
        save_undo_history(records)

    if logger:
        logger(f"✨ {len(records)} duplicado(s) movido(s) para Duplicados/.")

    return records
