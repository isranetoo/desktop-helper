import hashlib
import json
import os
import shutil
import threading
import time
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


APP_DIR = Path(__file__).resolve().parent
CONFIG_PATH = APP_DIR / "config.json"
LOGS_DIR = APP_DIR / "logs"
HISTORY_PATH = APP_DIR / "last_organization.json"

DOWNLOADS_PATH = Path.home() / "Downloads"
DESKTOP_PATH = Path.home() / "Desktop"
DOCUMENTS_PATH = Path.home() / "Documents"

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
    "ignored_extensions": [".lnk", ".ini", ".tmp", ".part", ".crdownload"],
    "ignored_names": ["desktop.ini"],
    "rules": [
        {
            "if_extension": ".pdf",
            "name_contains": "nota",
            "target": "Notas Fiscais",
        },
        {
            "if_extension": ".jpg",
            "name_contains": "print",
            "target": "Screenshots",
        },
    ],
    "duplicates_folder": "Duplicados",
}


def load_config():
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2, ensure_ascii=False), encoding="utf-8")
        return DEFAULT_CONFIG

    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        loaded = json.load(config_file)

    config = DEFAULT_CONFIG.copy()
    config.update(loaded)
    if "categories" not in config:
        config["categories"] = DEFAULT_CONFIG["categories"]
    return config


def ensure_folder_exists(base_path: Path, folder_name: str) -> Path:
    destination_path = base_path / folder_name
    destination_path.mkdir(parents=True, exist_ok=True)
    return destination_path


def generate_non_conflicting_name(destination_dir: Path, filename: str) -> str:
    base_name, ext = os.path.splitext(filename)
    candidate = filename
    counter = 1

    while (destination_dir / candidate).exists():
        candidate = f"{base_name} ({counter}){ext}"
        counter += 1

    return candidate


def compute_sha256(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def month_folder_name(file_path: Path) -> str:
    modified = datetime.fromtimestamp(file_path.stat().st_mtime)
    month_name = modified.strftime("%m-%B")
    return f"{modified.year}/{month_name}"


def combined_folder_name(file_path: Path, category: str) -> str:
    modified = datetime.fromtimestamp(file_path.stat().st_mtime)
    return f"{category}/{modified.strftime('%Y-%m')}"


class OrganizerEngine:
    def __init__(self, config, logger, progress_callback, counters_callback):
        self.config = config
        self.logger = logger
        self.progress_callback = progress_callback
        self.counters_callback = counters_callback
        self.operation_log = []

    def _matches_rule(self, filename: str, extension: str):
        rules = self.config.get("rules", [])
        lower_name = filename.lower()
        for rule in rules:
            rule_ext = rule.get("if_extension", "").lower()
            name_contains = rule.get("name_contains", "").lower()
            if rule_ext and extension != rule_ext:
                continue
            if name_contains and name_contains not in lower_name:
                continue
            target = rule.get("target")
            if target:
                return target
        return None

    def _category_for_file(self, filename: str):
        _, ext = os.path.splitext(filename.lower())

        ruled_target = self._matches_rule(filename, ext)
        if ruled_target:
            return ruled_target

        for folder_name, extensions in self.config["categories"].items():
            if ext in [entry.lower() for entry in extensions]:
                return folder_name

        return "Outros"

    def _is_ignored(self, filename: str):
        lower_name = filename.lower()
        _, extension = os.path.splitext(lower_name)
        if lower_name in [entry.lower() for entry in self.config.get("ignored_names", [])]:
            return True
        if extension in [entry.lower() for entry in self.config.get("ignored_extensions", [])]:
            return True
        if lower_name.startswith("~"):
            return True
        return False

    def _write_audit_log(self, message: str):
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOGS_DIR / f"organizador_{datetime.now().strftime('%Y-%m-%d')}.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with log_file.open("a", encoding="utf-8") as output:
            output.write(f"[{timestamp}] {message}\n")

    def _target_for_mode(self, file_path: Path, category: str, mode: str):
        if mode == "date":
            return month_folder_name(file_path)
        if mode == "combined":
            return combined_folder_name(file_path, category)
        return category

    def _detect_duplicate(self, source_path: Path, duplicates_dir: Path):
        source_hash = compute_sha256(source_path)
        for candidate in duplicates_dir.glob("*"):
            if not candidate.is_file():
                continue
            if candidate.suffix.lower() != source_path.suffix.lower():
                continue
            if compute_sha256(candidate) == source_hash:
                return True
        return False

    def organize_folder(self, folder_path: Path, mode="extension", dry_run=False):
        if not folder_path.exists():
            self.logger(f"❌ Pasta não encontrada: {folder_path}")
            return

        files = [item for item in folder_path.iterdir() if item.is_file()]
        total_files = len(files)
        moved = 0
        ignored = 0
        errors = 0
        self.operation_log = []

        self.logger(f"📁 Organizando: {folder_path}")

        duplicates_dir_name = self.config.get("duplicates_folder", "Duplicados")
        duplicates_dir = ensure_folder_exists(folder_path, duplicates_dir_name)

        for index, item_path in enumerate(files, start=1):
            filename = item_path.name
            self.progress_callback(index, total_files)

            if self._is_ignored(filename):
                ignored += 1
                self.logger(f"⏭️ Ignorado: {filename}")
                self._write_audit_log(f"IGNORED | file={filename} | reason=ignore-list")
                continue

            category = self._category_for_file(filename)
            target_folder_name = self._target_for_mode(item_path, category, mode)
            destination_dir = ensure_folder_exists(folder_path, target_folder_name)

            destination_file_name = generate_non_conflicting_name(destination_dir, filename)
            destination_file = destination_dir / destination_file_name

            try:
                if self._detect_duplicate(item_path, duplicates_dir):
                    duplicate_target_name = generate_non_conflicting_name(duplicates_dir, filename)
                    duplicate_target = duplicates_dir / duplicate_target_name
                    if dry_run:
                        self.logger(f"🧪 [Simulação] {filename} -> {duplicates_dir_name}")
                    else:
                        shutil.move(str(item_path), str(duplicate_target))
                        self.operation_log.append({"from": str(item_path), "to": str(duplicate_target)})
                    moved += 1
                    self._write_audit_log(
                        f"DUPLICATE | file={filename} | from={item_path} | to={duplicate_target}"
                    )
                    continue

                if dry_run:
                    self.logger(f"🧪 [Simulação] {filename} -> {target_folder_name}")
                else:
                    shutil.move(str(item_path), str(destination_file))
                    self.operation_log.append({"from": str(item_path), "to": str(destination_file)})

                moved += 1
                self._write_audit_log(
                    f"MOVED | file={filename} | from={item_path} | to={destination_file}"
                )
                self.logger(f"✅ {filename} movido para {target_folder_name}")

            except Exception as error:
                errors += 1
                self.logger(f"❌ Erro ao mover {filename}: {error}")
                self._write_audit_log(
                    f"ERROR | file={filename} | from={item_path} | error={error}"
                )

            self.counters_callback(moved, ignored, errors)

        if not dry_run and self.operation_log:
            HISTORY_PATH.write_text(json.dumps(self.operation_log, indent=2, ensure_ascii=False), encoding="utf-8")

        self.counters_callback(moved, ignored, errors)
        self.logger(f"✨ Organização concluída. Arquivos analisados: {total_files}")

    def undo_last_organization(self):
        if not HISTORY_PATH.exists():
            self.logger("⚠️ Não há histórico para desfazer.")
            return

        history = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        if not history:
            self.logger("⚠️ Histórico vazio para desfazer.")
            return

        restored = 0
        errors = 0

        for movement in reversed(history):
            source = Path(movement["from"])
            destination = Path(movement["to"])

            try:
                if destination.exists():
                    source.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(destination), str(source))
                    restored += 1
                    self.logger(f"↩️ Restaurado: {destination.name}")
                    self._write_audit_log(
                        f"UNDO | file={destination.name} | from={destination} | to={source}"
                    )
            except Exception as error:
                errors += 1
                self.logger(f"❌ Erro no desfazer ({destination.name}): {error}")

        HISTORY_PATH.write_text("[]", encoding="utf-8")
        self.logger(f"✅ Desfazer concluído. Restaurados: {restored}. Erros: {errors}.")


class FolderMonitorHandler(FileSystemEventHandler):
    def __init__(self, app, watched_folder):
        super().__init__()
        self.app = app
        self.watched_folder = watched_folder

    def on_created(self, event):
        if event.is_directory:
            return
        time.sleep(2)
        self.app.organize_single_file(Path(event.src_path), self.watched_folder)


class ModernFileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Organizador de Arquivos")
        self.root.geometry("1080x720")
        self.root.minsize(980, 640)
        self.root.configure(bg="#0f172a")

        self.config_data = load_config()
        self.monitored_folders = [DOWNLOADS_PATH, DESKTOP_PATH, DOCUMENTS_PATH]
        self.observers = []
        self.monitoring = False

        self.engine = OrganizerEngine(
            config=self.config_data,
            logger=self.log,
            progress_callback=self.update_progress,
            counters_callback=self.update_counters,
        )

        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Main.TFrame", background="#0f172a")
        style.configure("Card.TFrame", background="#1e293b", relief="flat")
        style.configure("Header.TLabel", background="#0f172a", foreground="#f8fafc", font=("Segoe UI", 22, "bold"))
        style.configure("SubHeader.TLabel", background="#0f172a", foreground="#94a3b8", font=("Segoe UI", 10))
        style.configure("CardTitle.TLabel", background="#1e293b", foreground="#f8fafc", font=("Segoe UI", 13, "bold"))
        style.configure("CardText.TLabel", background="#1e293b", foreground="#cbd5e1", font=("Segoe UI", 10))
        style.configure("Status.TLabel", background="#1e293b", foreground="#38bdf8", font=("Segoe UI", 12, "bold"))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=10, background="#2563eb", foreground="#ffffff")
        style.map("Primary.TButton", background=[("active", "#1d4ed8")])
        style.configure("Success.TButton", font=("Segoe UI", 10, "bold"), padding=10, background="#16a34a", foreground="#ffffff")
        style.map("Success.TButton", background=[("active", "#15803d")])
        style.configure("Danger.TButton", font=("Segoe UI", 10, "bold"), padding=10, background="#dc2626", foreground="#ffffff")
        style.map("Danger.TButton", background=[("active", "#b91c1c")])
        style.configure("Secondary.TButton", font=("Segoe UI", 10, "bold"), padding=10, background="#334155", foreground="#ffffff")
        style.map("Secondary.TButton", background=[("active", "#475569")])

    def _build_ui(self):
        self.main = ttk.Frame(self.root, style="Main.TFrame", padding=24)
        self.main.pack(fill="both", expand=True)

        self._build_header()
        self._build_cards()
        self._build_actions()
        self._build_logs()

    def _build_header(self):
        header_frame = ttk.Frame(self.main, style="Main.TFrame")
        header_frame.pack(fill="x", pady=(0, 18))

        ttk.Label(header_frame, text="Organizador de Arquivos", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            header_frame,
            text="Monitoramento multi-pasta, simulação, desfazer, logs e organização por extensão/data.",
            style="SubHeader.TLabel",
        ).pack(anchor="w", pady=(6, 0))

    def _build_cards(self):
        cards_frame = ttk.Frame(self.main, style="Main.TFrame")
        cards_frame.pack(fill="x", pady=(0, 18))

        for index in range(4):
            cards_frame.columnconfigure(index, weight=1)

        status_card = ttk.Frame(cards_frame, style="Card.TFrame", padding=16)
        status_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ttk.Label(status_card, text="Status", style="CardTitle.TLabel").pack(anchor="w")
        self.status_var = tk.StringVar(value="Parado")
        ttk.Label(status_card, textvariable=self.status_var, style="Status.TLabel").pack(anchor="w", pady=(10, 0))

        moved_card = ttk.Frame(cards_frame, style="Card.TFrame", padding=16)
        moved_card.grid(row=0, column=1, sticky="nsew", padx=8)
        ttk.Label(moved_card, text="Movidos hoje", style="CardTitle.TLabel").pack(anchor="w")
        self.moved_var = tk.StringVar(value="0")
        ttk.Label(moved_card, textvariable=self.moved_var, style="Status.TLabel").pack(anchor="w", pady=(10, 0))

        ignored_card = ttk.Frame(cards_frame, style="Card.TFrame", padding=16)
        ignored_card.grid(row=0, column=2, sticky="nsew", padx=8)
        ttk.Label(ignored_card, text="Ignorados", style="CardTitle.TLabel").pack(anchor="w")
        self.ignored_var = tk.StringVar(value="0")
        ttk.Label(ignored_card, textvariable=self.ignored_var, style="Status.TLabel").pack(anchor="w", pady=(10, 0))

        errors_card = ttk.Frame(cards_frame, style="Card.TFrame", padding=16)
        errors_card.grid(row=0, column=3, sticky="nsew", padx=(8, 0))
        ttk.Label(errors_card, text="Erros", style="CardTitle.TLabel").pack(anchor="w")
        self.errors_var = tk.StringVar(value="0")
        ttk.Label(errors_card, textvariable=self.errors_var, style="Status.TLabel").pack(anchor="w", pady=(10, 0))

    def _build_actions(self):
        actions_card = ttk.Frame(self.main, style="Card.TFrame", padding=18)
        actions_card.pack(fill="x", pady=(0, 18))

        ttk.Label(actions_card, text="Ações rápidas", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))

        options_frame = ttk.Frame(actions_card, style="Card.TFrame")
        options_frame.pack(fill="x", pady=(0, 12))

        self.simulation_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Modo simulação", variable=self.simulation_var).pack(side="left")

        ttk.Label(options_frame, text="Modo:", style="CardText.TLabel").pack(side="left", padx=(12, 4))
        self.mode_var = tk.StringVar(value="extension")
        mode_box = ttk.Combobox(
            options_frame,
            textvariable=self.mode_var,
            state="readonly",
            values=["extension", "date", "combined"],
            width=14,
        )
        mode_box.pack(side="left")

        ttk.Button(
            options_frame,
            text="Selecionar pasta para organizar",
            style="Secondary.TButton",
            command=self.select_and_organize_folder,
        ).pack(side="right")

        buttons_frame = ttk.Frame(actions_card, style="Card.TFrame")
        buttons_frame.pack(fill="x")

        for index in range(4):
            buttons_frame.columnconfigure(index, weight=1)

        ttk.Button(
            buttons_frame,
            text="📁 Organizar Downloads",
            style="Primary.TButton",
            command=lambda: self.organize_path(DOWNLOADS_PATH),
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ttk.Button(
            buttons_frame,
            text="🖥️ Organizar Desktop",
            style="Primary.TButton",
            command=lambda: self.organize_path(DESKTOP_PATH),
        ).grid(row=0, column=1, padx=8, sticky="ew")

        ttk.Button(
            buttons_frame,
            text="↩️ Desfazer última organização",
            style="Danger.TButton",
            command=self.undo_last,
        ).grid(row=0, column=2, padx=8, sticky="ew")

        self.monitor_button = ttk.Button(
            buttons_frame,
            text="▶ Iniciar monitoramento",
            style="Success.TButton",
            command=self.toggle_monitoring,
        )
        self.monitor_button.grid(row=0, column=3, padx=(8, 0), sticky="ew")

        monitored_frame = ttk.Frame(actions_card, style="Card.TFrame")
        monitored_frame.pack(fill="x", pady=(12, 0))

        ttk.Label(monitored_frame, text="Pastas monitoradas:", style="CardText.TLabel").pack(anchor="w")
        self.monitored_var = tk.StringVar(value=self._monitored_label())
        ttk.Label(monitored_frame, textvariable=self.monitored_var, style="CardText.TLabel", wraplength=980).pack(anchor="w", pady=(4, 0))

        ttk.Button(
            monitored_frame,
            text="+ Adicionar pasta para monitorar",
            style="Secondary.TButton",
            command=self.add_monitored_folder,
        ).pack(anchor="w", pady=(8, 0))

        self.progress_var = tk.StringVar(value="Pronto")
        ttk.Label(actions_card, textvariable=self.progress_var, style="CardText.TLabel").pack(anchor="w", pady=(12, 6))
        self.progressbar = ttk.Progressbar(actions_card, mode="determinate")
        self.progressbar.pack(fill="x")

    def _build_logs(self):
        logs_card = ttk.Frame(self.main, style="Card.TFrame", padding=18)
        logs_card.pack(fill="both", expand=True)

        top_logs = ttk.Frame(logs_card, style="Card.TFrame")
        top_logs.pack(fill="x", pady=(0, 10))

        ttk.Label(top_logs, text="Logs do sistema", style="CardTitle.TLabel").pack(side="left")
        ttk.Button(top_logs, text="Limpar logs", style="Secondary.TButton", command=self.clear_logs).pack(side="right")

        self.log_text = scrolledtext.ScrolledText(
            logs_card,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#020617",
            fg="#e2e8f0",
            insertbackground="#e2e8f0",
            relief="flat",
            borderwidth=0,
            height=12,
        )
        self.log_text.pack(fill="both", expand=True)

        self.log("🚀 Sistema iniciado.")
        self.log(f"🧩 Configuração carregada de: {CONFIG_PATH}")

    def _monitored_label(self):
        return ", ".join([str(path) for path in self.monitored_folders])

    def log(self, message: str):
        def append():
            current_time = time.strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{current_time}] {message}\n")
            self.log_text.see(tk.END)

        self.root.after(0, append)

    def clear_logs(self):
        self.log_text.delete("1.0", tk.END)

    def update_progress(self, current, total):
        def apply_update():
            if total == 0:
                self.progressbar["value"] = 0
                self.progress_var.set("Nenhum arquivo para organizar")
                return
            percent = (current / total) * 100
            self.progressbar["value"] = percent
            self.progress_var.set(f"Organizando {current}/{total} arquivos...")

        self.root.after(0, apply_update)

    def update_counters(self, moved, ignored, errors):
        def apply_update():
            self.moved_var.set(str(moved))
            self.ignored_var.set(str(ignored))
            self.errors_var.set(str(errors))

        self.root.after(0, apply_update)

    def organize_path(self, path: Path):
        dry_run = self.simulation_var.get()
        mode = self.mode_var.get()
        self.log(f"📁 Iniciando organização em {path} (modo={mode}, simulação={dry_run})")

        threading.Thread(
            target=self.engine.organize_folder,
            args=(path, mode, dry_run),
            daemon=True,
        ).start()

    def select_and_organize_folder(self):
        selected = filedialog.askdirectory(title="Selecionar pasta para organizar")
        if not selected:
            return
        self.organize_path(Path(selected))

    def undo_last(self):
        threading.Thread(target=self.engine.undo_last_organization, daemon=True).start()

    def add_monitored_folder(self):
        selected = filedialog.askdirectory(title="Selecionar pasta para monitorar")
        if not selected:
            return

        path = Path(selected)
        if path in self.monitored_folders:
            self.log(f"⚠️ Pasta já monitorada: {path}")
            return

        self.monitored_folders.append(path)
        self.monitored_var.set(self._monitored_label())
        self.log(f"✅ Pasta adicionada ao monitoramento: {path}")

    def organize_single_file(self, file_path: Path, base_folder: Path):
        if not file_path.exists() or not file_path.is_file():
            return
        self.engine.organize_folder(base_folder, mode=self.mode_var.get(), dry_run=False)

    def toggle_monitoring(self):
        if self.monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def start_monitoring(self):
        if self.monitoring:
            self.log("⚠️ O monitoramento já está ativo.")
            return

        try:
            for folder in self.monitored_folders:
                if not folder.exists():
                    continue
                handler = FolderMonitorHandler(self, folder)
                observer = Observer()
                observer.schedule(handler, str(folder), recursive=False)
                observer.start()
                self.observers.append(observer)

            self.monitoring = True
            self.status_var.set("Monitorando")
            self.monitor_button.config(text="■ Parar monitoramento", style="Danger.TButton")
            self.log(f"✅ Monitoramento iniciado em {len(self.observers)} pasta(s).")

        except Exception as error:
            messagebox.showerror("Erro", f"Não foi possível iniciar o monitoramento.\n\n{error}")

    def stop_monitoring(self):
        if not self.monitoring:
            self.log("⚠️ Nenhum monitoramento ativo.")
            return

        for observer in self.observers:
            observer.stop()
            observer.join(timeout=2)

        self.observers = []
        self.monitoring = False
        self.status_var.set("Parado")
        self.monitor_button.config(text="▶ Iniciar monitoramento", style="Success.TButton")
        self.log("🛑 Monitoramento encerrado.")

    def on_close(self):
        if self.monitoring:
            self.stop_monitoring()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = ModernFileOrganizerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
