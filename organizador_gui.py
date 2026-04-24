import os
import time
import shutil
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


DOWNLOADS_PATH = os.path.join(os.path.expanduser("~"), "Downloads")
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")


EXTENSION_MAP = {
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
}


def get_destination_folder(filename: str) -> str:
    _, ext = os.path.splitext(filename.lower())

    for folder_name, extensions in EXTENSION_MAP.items():
        if ext in extensions:
            return folder_name

    return "Outros"


def ensure_folder_exists(base_path: str, folder_name: str) -> str:
    destination_path = os.path.join(base_path, folder_name)
    os.makedirs(destination_path, exist_ok=True)
    return destination_path


def generate_non_conflicting_name(destination_dir: str, filename: str) -> str:
    base_name, ext = os.path.splitext(filename)
    candidate = filename
    counter = 1

    while os.path.exists(os.path.join(destination_dir, candidate)):
        candidate = f"{base_name} ({counter}){ext}"
        counter += 1

    return candidate


def move_file(file_path: str, base_destination: str, logger=None) -> None:
    if not os.path.isfile(file_path):
        return

    filename = os.path.basename(file_path)

    ignored_suffixes = (".crdownload", ".tmp", ".part")
    if filename.startswith("~") or filename.endswith(ignored_suffixes):
        return

    folder_name = get_destination_folder(filename)
    destination_dir = ensure_folder_exists(base_destination, folder_name)

    safe_filename = generate_non_conflicting_name(destination_dir, filename)
    destination_file = os.path.join(destination_dir, safe_filename)

    try:
        shutil.move(file_path, destination_file)

        if logger:
            logger(f"✅ {filename} movido para {folder_name}")

    except PermissionError:
        if logger:
            logger(f"⚠️ Arquivo em uso: {filename}")

    except Exception as e:
        if logger:
            logger(f"❌ Erro ao mover {filename}: {e}")


def organize_existing_files(folder_path: str, logger=None) -> None:
    if not os.path.exists(folder_path):
        if logger:
            logger(f"❌ Pasta não encontrada: {folder_path}")
        return

    if logger:
        logger(f"📁 Organizando: {folder_path}")

    count = 0

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        if os.path.isfile(item_path):
            move_file(item_path, folder_path, logger=logger)
            count += 1

    if logger:
        logger(f"✨ Organização concluída. Arquivos analisados: {count}")


class DownloadHandler(FileSystemEventHandler):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger

    def on_created(self, event):
        if event.is_directory:
            return

        time.sleep(2)
        move_file(event.src_path, DOWNLOADS_PATH, logger=self.logger)


class ModernFileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Organizador de Arquivos")
        self.root.geometry("980x640")
        self.root.minsize(900, 580)
        self.root.configure(bg="#0f172a")

        self.observer = None
        self.monitoring = False

        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Main.TFrame",
            background="#0f172a"
        )

        style.configure(
            "Card.TFrame",
            background="#1e293b",
            relief="flat"
        )

        style.configure(
            "Header.TLabel",
            background="#0f172a",
            foreground="#f8fafc",
            font=("Segoe UI", 22, "bold")
        )

        style.configure(
            "SubHeader.TLabel",
            background="#0f172a",
            foreground="#94a3b8",
            font=("Segoe UI", 10)
        )

        style.configure(
            "CardTitle.TLabel",
            background="#1e293b",
            foreground="#f8fafc",
            font=("Segoe UI", 13, "bold")
        )

        style.configure(
            "CardText.TLabel",
            background="#1e293b",
            foreground="#cbd5e1",
            font=("Segoe UI", 10)
        )

        style.configure(
            "Status.TLabel",
            background="#1e293b",
            foreground="#38bdf8",
            font=("Segoe UI", 12, "bold")
        )

        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=10,
            background="#2563eb",
            foreground="#ffffff"
        )

        style.map(
            "Primary.TButton",
            background=[("active", "#1d4ed8")]
        )

        style.configure(
            "Success.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=10,
            background="#16a34a",
            foreground="#ffffff"
        )

        style.map(
            "Success.TButton",
            background=[("active", "#15803d")]
        )

        style.configure(
            "Danger.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=10,
            background="#dc2626",
            foreground="#ffffff"
        )

        style.map(
            "Danger.TButton",
            background=[("active", "#b91c1c")]
        )

        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=10,
            background="#334155",
            foreground="#ffffff"
        )

        style.map(
            "Secondary.TButton",
            background=[("active", "#475569")]
        )

    def _build_ui(self):
        self.main = ttk.Frame(self.root, style="Main.TFrame", padding=24)
        self.main.pack(fill="both", expand=True)

        self._build_header()
        self._build_cards()
        self._build_actions()
        self._build_logs()

    def _build_header(self):
        header_frame = ttk.Frame(self.main, style="Main.TFrame")
        header_frame.pack(fill="x", pady=(0, 22))

        title = ttk.Label(
            header_frame,
            text="Organizador de Arquivos",
            style="Header.TLabel"
        )
        title.pack(anchor="w")

        subtitle = ttk.Label(
            header_frame,
            text="Monitore Downloads, organize arquivos por extensão e limpe sua Área de Trabalho.",
            style="SubHeader.TLabel"
        )
        subtitle.pack(anchor="w", pady=(6, 0))

    def _build_cards(self):
        cards_frame = ttk.Frame(self.main, style="Main.TFrame")
        cards_frame.pack(fill="x", pady=(0, 18))

        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)
        cards_frame.columnconfigure(2, weight=1)

        self.status_card = ttk.Frame(cards_frame, style="Card.TFrame", padding=18)
        self.status_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ttk.Label(
            self.status_card,
            text="Status",
            style="CardTitle.TLabel"
        ).pack(anchor="w")

        self.status_var = tk.StringVar(value="Parado")
        ttk.Label(
            self.status_card,
            textvariable=self.status_var,
            style="Status.TLabel"
        ).pack(anchor="w", pady=(10, 0))

        ttk.Label(
            self.status_card,
            text="Monitoramento da pasta Downloads",
            style="CardText.TLabel"
        ).pack(anchor="w", pady=(8, 0))

        downloads_card = ttk.Frame(cards_frame, style="Card.TFrame", padding=18)
        downloads_card.grid(row=0, column=1, sticky="nsew", padx=10)

        ttk.Label(
            downloads_card,
            text="Downloads",
            style="CardTitle.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            downloads_card,
            text=DOWNLOADS_PATH,
            style="CardText.TLabel",
            wraplength=250
        ).pack(anchor="w", pady=(10, 0))

        desktop_card = ttk.Frame(cards_frame, style="Card.TFrame", padding=18)
        desktop_card.grid(row=0, column=2, sticky="nsew", padx=(10, 0))

        ttk.Label(
            desktop_card,
            text="Desktop",
            style="CardTitle.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            desktop_card,
            text=DESKTOP_PATH,
            style="CardText.TLabel",
            wraplength=250
        ).pack(anchor="w", pady=(10, 0))

    def _build_actions(self):
        actions_card = ttk.Frame(self.main, style="Card.TFrame", padding=18)
        actions_card.pack(fill="x", pady=(0, 18))

        ttk.Label(
            actions_card,
            text="Ações rápidas",
            style="CardTitle.TLabel"
        ).pack(anchor="w", pady=(0, 14))

        buttons_frame = ttk.Frame(actions_card, style="Card.TFrame")
        buttons_frame.pack(fill="x")

        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=1)
        buttons_frame.columnconfigure(3, weight=1)

        self.btn_downloads = ttk.Button(
            buttons_frame,
            text="📁 Organizar Downloads",
            style="Primary.TButton",
            command=self.organize_downloads
        )
        self.btn_downloads.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.btn_desktop = ttk.Button(
            buttons_frame,
            text="🖥️ Organizar Desktop",
            style="Primary.TButton",
            command=self.organize_desktop
        )
        self.btn_desktop.grid(row=0, column=1, padx=8, sticky="ew")

        self.btn_start = ttk.Button(
            buttons_frame,
            text="▶ Iniciar Monitoramento",
            style="Success.TButton",
            command=self.start_monitoring
        )
        self.btn_start.grid(row=0, column=2, padx=8, sticky="ew")

        self.btn_stop = ttk.Button(
            buttons_frame,
            text="■ Parar",
            style="Danger.TButton",
            command=self.stop_monitoring,
            state="disabled"
        )
        self.btn_stop.grid(row=0, column=3, padx=(8, 0), sticky="ew")

    def _build_logs(self):
        logs_card = ttk.Frame(self.main, style="Card.TFrame", padding=18)
        logs_card.pack(fill="both", expand=True)

        top_logs = ttk.Frame(logs_card, style="Card.TFrame")
        top_logs.pack(fill="x", pady=(0, 10))

        ttk.Label(
            top_logs,
            text="Logs do sistema",
            style="CardTitle.TLabel"
        ).pack(side="left")

        ttk.Button(
            top_logs,
            text="Limpar logs",
            style="Secondary.TButton",
            command=self.clear_logs
        ).pack(side="right")

        self.log_text = scrolledtext.ScrolledText(
            logs_card,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#020617",
            fg="#e2e8f0",
            insertbackground="#e2e8f0",
            relief="flat",
            borderwidth=0,
            height=12
        )
        self.log_text.pack(fill="both", expand=True)

        self.log("🚀 Sistema iniciado.")
        self.log("💡 Use os botões acima para organizar ou monitorar seus arquivos.")

    def log(self, message: str):
        def append():
            current_time = time.strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{current_time}] {message}\n")
            self.log_text.see(tk.END)

        self.root.after(0, append)

    def clear_logs(self):
        self.log_text.delete("1.0", tk.END)

    def organize_downloads(self):
        self.log("📁 Iniciando organização da pasta Downloads...")

        threading.Thread(
            target=organize_existing_files,
            args=(DOWNLOADS_PATH, self.log),
            daemon=True
        ).start()

    def organize_desktop(self):
        self.log("🖥️ Iniciando organização da Área de Trabalho...")

        threading.Thread(
            target=organize_existing_files,
            args=(DESKTOP_PATH, self.log),
            daemon=True
        ).start()

    def start_monitoring(self):
        if self.monitoring:
            self.log("⚠️ O monitoramento já está ativo.")
            return

        if not os.path.exists(DOWNLOADS_PATH):
            messagebox.showerror(
                "Erro",
                f"A pasta Downloads não foi encontrada:\n{DOWNLOADS_PATH}"
            )
            return

        try:
            event_handler = DownloadHandler(self.log)

            self.observer = Observer()
            self.observer.schedule(event_handler, DOWNLOADS_PATH, recursive=False)
            self.observer.start()

            self.monitoring = True
            self.status_var.set("Monitorando")
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")

            self.log(f"✅ Monitoramento iniciado em: {DOWNLOADS_PATH}")

        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Não foi possível iniciar o monitoramento.\n\n{e}"
            )

    def stop_monitoring(self):
        if not self.monitoring or self.observer is None:
            self.log("⚠️ Nenhum monitoramento ativo.")
            return

        try:
            self.observer.stop()
            self.observer.join(timeout=2)

            self.observer = None
            self.monitoring = False

            self.status_var.set("Parado")
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")

            self.log("🛑 Monitoramento encerrado.")

        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Não foi possível parar o monitoramento.\n\n{e}"
            )

    def on_close(self):
        if self.observer is not None and self.monitoring:
            try:
                self.observer.stop()
                self.observer.join(timeout=2)
            except Exception:
                pass

        self.root.destroy()


def main():
    root = tk.Tk()
    app = ModernFileOrganizerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()