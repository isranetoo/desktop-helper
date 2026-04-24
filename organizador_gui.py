"""
organizador_gui.py — Interface gráfica completa do organizador de arquivos.

Funcionalidades:
  1.  Selecionar pastas manualmente
  2.  Categorias editáveis via config.json
  3.  Modo simulação (dry-run)
  4.  Histórico de ações em arquivo de log
  5.  Desfazer última organização
  6.  Ignorar arquivos específicos
  7.  Organizar por data
  8.  Detecção de duplicados
  9.  Barra de progresso
  10. Contadores no dashboard
  11. Minimizar para bandeja
  12. Preparado para empacotamento (.exe)
  13. Notificações do sistema
  14. Monitorar várias pastas
  15. Regras personalizadas
"""

import os
import sys
import time
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, simpledialog
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import core

# Tenta importar pystray (opcional)
try:
    import pystray
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False


# ==========================================
# HANDLER DO WATCHDOG
# ==========================================
class FolderHandler(FileSystemEventHandler):
    """Monitora uma pasta e organiza arquivos novos automaticamente."""

    def __init__(self, folder_path: str, config: dict, logger, notify: bool = True):
        super().__init__()
        self.folder_path = folder_path
        self.config = config
        self.logger = logger
        self.notify = notify

    def on_created(self, event):
        if event.is_directory:
            return
        time.sleep(2)
        core.move_file(
            event.src_path,
            self.folder_path,
            self.config,
            logger=self.logger,
            notify=self.notify,
        )


# ==========================================
# APLICAÇÃO PRINCIPAL
# ==========================================
class FileOrganizerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sortify")
        self.root.geometry("1180x820")
        self.root.minsize(1024, 720)
        self.root.configure(bg="#0b1220")

        self.config = core.load_config()

        # Estado de monitoramento: {folder_path: Observer}
        self.observers: dict[str, Observer] = {}
        self.monitoring = False

        # Contadores da sessão
        self.counter_moved = 0
        self.counter_ignored = 0
        self.counter_errors = 0

        # Tray
        self.tray_icon = None

        self._setup_style()
        self._build_ui()
        self._update_counter_display()

    # ──────────────────────────────────────
    # ESTILOS
    # ──────────────────────────────────────
    def _setup_style(self):
        s = ttk.Style()
        s.theme_use("clam")

        bg_main = "#0b1220"
        bg_card = "#111b2e"
        bg_card_soft = "#17243d"
        fg_title = "#f3f6ff"
        fg_sub = "#9db0ce"
        fg_body = "#c9d6ec"
        accent = "#4f8cff"
        purple = "#7c3aed"
        green = "#10b981"

        s.configure("Main.TFrame", background=bg_main)
        s.configure("Card.TFrame", background=bg_card, relief="flat", borderwidth=0)
        s.configure("SoftCard.TFrame", background=bg_card_soft, relief="flat", borderwidth=0)

        s.configure("Header.TLabel", background=bg_main, foreground=fg_title,
                     font=("Segoe UI", 42, "bold"))
        s.configure("SubHeader.TLabel", background=bg_main, foreground=fg_sub,
                     font=("Segoe UI", 12))
        s.configure("CardTitle.TLabel", background=bg_card, foreground=fg_title,
                     font=("Segoe UI", 14, "bold"))
        s.configure("CardText.TLabel", background=bg_card, foreground=fg_body,
                     font=("Segoe UI", 11))
        s.configure("Status.TLabel", background=bg_card, foreground=accent,
                     font=("Segoe UI", 12, "bold"))
        s.configure("CounterValue.TLabel", background=bg_card, foreground=fg_title,
                     font=("Segoe UI", 24, "bold"))
        s.configure("CounterLabel.TLabel", background=bg_card, foreground=fg_sub,
                     font=("Segoe UI", 10))
        s.configure("HeroTag.TLabel", background=bg_main, foreground=fg_sub,
                    font=("Segoe UI", 20, "bold"))
        s.configure("HeroGreen.TLabel", background=bg_main, foreground=green,
                    font=("Segoe UI", 17, "bold"))
        s.configure("HeroBlue.TLabel", background=bg_main, foreground=accent,
                    font=("Segoe UI", 17, "bold"))
        s.configure("HeroPurple.TLabel", background=bg_main, foreground=purple,
                    font=("Segoe UI", 17, "bold"))
        s.configure("HeroLight.TLabel", background=bg_main, foreground=fg_title,
                    font=("Segoe UI", 17, "bold"))

        for name, bg_color, bg_active in [
            ("Primary.TButton",   "#2563eb", "#1d4ed8"),
            ("Success.TButton",   "#16a34a", "#15803d"),
            ("Danger.TButton",    "#dc2626", "#b91c1c"),
            ("Secondary.TButton", "#243554", "#304668"),
            ("Warning.TButton",   "#d97706", "#b45309"),
            ("Info.TButton",      "#5b39d6", "#4f2ec4"),
        ]:
            s.configure(name, font=("Segoe UI", 10, "bold"), padding=9,
                        background=bg_color, foreground="#ffffff")
            s.map(name, background=[("active", bg_active)])

        s.configure("Horizontal.TProgressbar",
                    background="#2563eb", troughcolor="#17243d", thickness=8)

    # ──────────────────────────────────────
    # CONSTRUÇÃO DA UI
    # ──────────────────────────────────────
    def _build_ui(self):
        # Container com scroll
        canvas = tk.Canvas(self.root, bg="#0b1220", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        self.main = ttk.Frame(canvas, style="Main.TFrame", padding=24)

        self.main.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.main, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self._build_hero()
        self._build_counters()
        self._build_actions_row1()
        self._build_actions_row2()
        self._build_monitored_folders()
        self._build_progress()
        self._build_logs()

    def _build_hero(self):
        frame = ttk.Frame(self.main, style="Main.TFrame")
        frame.pack(fill="x", pady=(0, 18))

        left = ttk.Frame(frame, style="Main.TFrame")
        left.pack(side="left", fill="x", expand=True)

        icon = tk.Canvas(left, width=190, height=140, bg="#0b1220", highlightthickness=0)
        icon.pack(side="left", padx=(0, 14))
        icon.create_rectangle(18, 38, 165, 116, outline="", fill="#1d4ed8")
        icon.create_rectangle(24, 48, 171, 122, outline="", fill="#2563eb")
        icon.create_rectangle(48, 46, 97, 66, outline="", fill="#3b82f6")
        icon.create_line(86, 89, 118, 109, 160, 63, fill="#f8fafc", width=12, smooth=True)

        title_box = ttk.Frame(left, style="Main.TFrame")
        title_box.pack(side="left", fill="y")
        ttk.Label(title_box, text="Sortify", style="Header.TLabel").pack(anchor="w")

        subtitle = ttk.Frame(title_box, style="Main.TFrame")
        subtitle.pack(anchor="w", pady=(2, 0))
        ttk.Label(subtitle, text="Organiza.", style="HeroGreen.TLabel").pack(side="left")
        ttk.Label(subtitle, text=" Simplifica.", style="HeroBlue.TLabel").pack(side="left")
        ttk.Label(subtitle, text=" Liberta seu espaço.", style="HeroLight.TLabel").pack(side="left")

        badge = ttk.Frame(frame, style="SoftCard.TFrame", padding=14)
        badge.pack(side="right")
        ttk.Label(badge, text="Identidade visual atualizada", style="SubHeader.TLabel").pack(anchor="e")
        ttk.Label(badge, text="Visual moderno + escuro", style="HeroTag.TLabel").pack(anchor="e")

    def _build_counters(self):
        """Cards de contadores: movidos, ignorados, erros, status."""
        frame = ttk.Frame(self.main, style="Main.TFrame")
        frame.pack(fill="x", pady=(0, 14))

        for i in range(4):
            frame.columnconfigure(i, weight=1)

        data = [
            ("Movidos", "counter_moved_var",   "#22c55e"),
            ("Ignorados", "counter_ignored_var", "#f59e0b"),
            ("Erros", "counter_errors_var",     "#ef4444"),
            ("Status", "status_var",            "#38bdf8"),
        ]

        for col, (label, var_name, color) in enumerate(data):
            card = ttk.Frame(frame, style="Card.TFrame", padding=14)
            padx = (0, 8) if col == 0 else (8, 0) if col == 3 else 8
            card.grid(row=0, column=col, sticky="nsew", padx=padx)

            if var_name == "status_var":
                sv = tk.StringVar(value="Parado")
                setattr(self, var_name, sv)
                ttk.Label(card, textvariable=sv, style="Status.TLabel").pack(anchor="w")
            else:
                sv = tk.StringVar(value="0")
                setattr(self, var_name, sv)
                lbl = ttk.Label(card, textvariable=sv, style="CounterValue.TLabel")
                lbl.pack(anchor="w")
                lbl.configure(foreground=color)

            ttk.Label(card, text=label, style="CounterLabel.TLabel").pack(anchor="w", pady=(4, 0))

    def _build_actions_row1(self):
        """Primeira fileira de botões: organizar, simular, desfazer."""
        card = ttk.Frame(self.main, style="Card.TFrame", padding=14)
        card.pack(fill="x", pady=(0, 10))

        ttk.Label(card, text="Organização", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))

        bf = ttk.Frame(card, style="Card.TFrame")
        bf.pack(fill="x")
        for i in range(6):
            bf.columnconfigure(i, weight=1)

        ttk.Button(bf, text="📁 Downloads", style="Primary.TButton",
                   command=self._organize_downloads).grid(row=0, column=0, padx=(0, 6), sticky="ew")

        ttk.Button(bf, text="🖥️ Desktop", style="Primary.TButton",
                   command=self._organize_desktop).grid(row=0, column=1, padx=6, sticky="ew")

        ttk.Button(bf, text="📂 Outra pasta...", style="Info.TButton",
                   command=self._organize_custom).grid(row=0, column=2, padx=6, sticky="ew")

        ttk.Button(bf, text="🔍 Simular", style="Warning.TButton",
                   command=self._simulate).grid(row=0, column=3, padx=6, sticky="ew")

        ttk.Button(bf, text="⏪ Desfazer", style="Secondary.TButton",
                   command=self._undo).grid(row=0, column=4, padx=6, sticky="ew")

        ttk.Button(bf, text="📄 Duplicados", style="Secondary.TButton",
                   command=self._find_duplicates).grid(row=0, column=5, padx=(6, 0), sticky="ew")

    def _build_actions_row2(self):
        """Segunda fileira: monitoramento, config, tray."""
        card = ttk.Frame(self.main, style="Card.TFrame", padding=14)
        card.pack(fill="x", pady=(0, 10))

        ttk.Label(card, text="Monitoramento e Configuração", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))

        bf = ttk.Frame(card, style="Card.TFrame")
        bf.pack(fill="x")
        for i in range(5):
            bf.columnconfigure(i, weight=1)

        self.btn_start = ttk.Button(
            bf, text="▶ Iniciar Monitor", style="Success.TButton",
            command=self._start_monitoring,
        )
        self.btn_start.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        self.btn_stop = ttk.Button(
            bf, text="■ Parar Monitor", style="Danger.TButton",
            command=self._stop_monitoring, state="disabled",
        )
        self.btn_stop.grid(row=0, column=1, padx=6, sticky="ew")

        ttk.Button(bf, text="⚙ Categorias", style="Secondary.TButton",
                   command=self._edit_categories).grid(row=0, column=2, padx=6, sticky="ew")

        ttk.Button(bf, text="📏 Regras", style="Secondary.TButton",
                   command=self._edit_rules).grid(row=0, column=3, padx=6, sticky="ew")

        # Checkbox organizar por data
        self.date_var = tk.BooleanVar(value=self.config.get("date_subfolder", False))
        date_cb = tk.Checkbutton(
            bf, text="📅 Sub-pastas por data", variable=self.date_var,
            command=self._toggle_date_mode,
            bg="#111b2e", fg="#c9d6ec", selectcolor="#243554",
            activebackground="#111b2e", activeforeground="#c9d6ec",
            font=("Segoe UI", 10), anchor="w",
        )
        date_cb.grid(row=0, column=4, padx=(6, 0), sticky="ew")

    def _build_monitored_folders(self):
        """Lista de pastas sendo monitoradas."""
        card = ttk.Frame(self.main, style="Card.TFrame", padding=14)
        card.pack(fill="x", pady=(0, 10))

        top = ttk.Frame(card, style="Card.TFrame")
        top.pack(fill="x", pady=(0, 8))

        ttk.Label(top, text="Pastas monitoradas", style="CardTitle.TLabel").pack(side="left")

        ttk.Button(top, text="+ Adicionar", style="Info.TButton",
                   command=self._add_monitored_folder).pack(side="right", padx=(8, 0))
        ttk.Button(top, text="- Remover", style="Danger.TButton",
                   command=self._remove_monitored_folder).pack(side="right")

        self.folders_listbox = tk.Listbox(
            card, height=4, font=("Consolas", 10),
            bg="#0a1427", fg="#e2e8f0", selectbackground="#2563eb",
            relief="flat", borderwidth=0,
        )
        self.folders_listbox.pack(fill="x")

        # Popula com Downloads + Desktop + salvas
        default_folders = [core.DOWNLOADS_PATH, core.DESKTOP_PATH]
        saved = self.config.get("monitored_folders", [])
        all_folders = list(dict.fromkeys(default_folders + saved))

        for f in all_folders:
            self.folders_listbox.insert(tk.END, f)

    def _build_progress(self):
        """Barra de progresso."""
        frame = ttk.Frame(self.main, style="Main.TFrame")
        frame.pack(fill="x", pady=(0, 10))

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            frame, variable=self.progress_var,
            maximum=100, style="Horizontal.TProgressbar",
        )
        self.progress_bar.pack(fill="x")

        self.progress_label = ttk.Label(frame, text="", style="SubHeader.TLabel")
        self.progress_label.pack(anchor="w", pady=(4, 0))

    def _build_logs(self):
        """Área de logs do sistema."""
        card = ttk.Frame(self.main, style="Card.TFrame", padding=14)
        card.pack(fill="both", expand=True)

        top = ttk.Frame(card, style="Card.TFrame")
        top.pack(fill="x", pady=(0, 8))

        ttk.Label(top, text="Logs do sistema", style="CardTitle.TLabel").pack(side="left")

        ttk.Button(top, text="Limpar", style="Secondary.TButton",
                   command=self._clear_logs).pack(side="right")

        self.log_text = scrolledtext.ScrolledText(
            card, wrap=tk.WORD, font=("Consolas", 10),
            bg="#0a1427", fg="#e2e8f0", insertbackground="#e2e8f0",
            relief="flat", borderwidth=0, height=10,
        )
        self.log_text.pack(fill="both", expand=True)

        self.log("🚀 Sistema iniciado.")
        self.log("💡 Use os botões acima para organizar seus arquivos.")

    # ──────────────────────────────────────
    # LOGGING
    # ──────────────────────────────────────
    def log(self, message: str):
        def _append():
            t = time.strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{t}] {message}\n")
            self.log_text.see(tk.END)
        self.root.after(0, _append)

    def _clear_logs(self):
        self.log_text.delete("1.0", tk.END)

    # ──────────────────────────────────────
    # PROGRESSO
    # ──────────────────────────────────────
    def _set_progress(self, current: int, total: int):
        if total <= 0:
            return
        pct = (current / total) * 100
        self.root.after(0, lambda: self.progress_var.set(pct))
        self.root.after(0, lambda: self.progress_label.configure(
            text=f"Processando {current}/{total} arquivos..."
        ))

    def _reset_progress(self):
        self.root.after(0, lambda: self.progress_var.set(0))
        self.root.after(0, lambda: self.progress_label.configure(text=""))

    # ──────────────────────────────────────
    # CONTADORES
    # ──────────────────────────────────────
    def _update_counter_display(self):
        self.counter_moved_var.set(str(self.counter_moved))
        self.counter_ignored_var.set(str(self.counter_ignored))
        self.counter_errors_var.set(str(self.counter_errors))

    def _counting_logger(self, message: str):
        """Logger que também atualiza contadores."""
        self.log(message)
        if message.startswith("✅"):
            self.counter_moved += 1
        elif message.startswith("⚠️"):
            self.counter_ignored += 1
        elif message.startswith("❌"):
            self.counter_errors += 1
        self.root.after(0, self._update_counter_display)

    # ──────────────────────────────────────
    # ORGANIZAÇÃO
    # ──────────────────────────────────────
    def _organize_folder(self, folder_path: str):
        def task():
            core.organize_folder(
                folder_path,
                self.config,
                logger=self._counting_logger,
                progress_callback=self._set_progress,
                notify=self.config.get("notifications_enabled", False),
            )
            self._reset_progress()
        threading.Thread(target=task, daemon=True).start()

    def _organize_downloads(self):
        self._organize_folder(core.DOWNLOADS_PATH)

    def _organize_desktop(self):
        self._organize_folder(core.DESKTOP_PATH)

    def _organize_custom(self):
        folder = filedialog.askdirectory(title="Selecionar pasta para organizar")
        if folder:
            self._organize_folder(folder)

    # ──────────────────────────────────────
    # SIMULAÇÃO
    # ──────────────────────────────────────
    def _simulate(self):
        folder = filedialog.askdirectory(title="Selecionar pasta para simular")
        if not folder:
            return

        def task():
            self.log(f"🔍 Simulação para: {folder}")
            actions = core.simulate_organization(folder, self.config, logger=self.log)
            if not actions:
                self.log("📭 Nenhum arquivo para organizar nesta pasta.")
                return
            # Pergunta se quer executar
            self.root.after(0, lambda: self._confirm_simulation(folder, actions))

        threading.Thread(target=task, daemon=True).start()

    def _confirm_simulation(self, folder: str, actions: list):
        resp = messagebox.askyesno(
            "Executar?",
            f"{len(actions)} arquivo(s) seriam movidos.\nDeseja executar a organização?",
        )
        if resp:
            self._organize_folder(folder)

    # ──────────────────────────────────────
    # DESFAZER
    # ──────────────────────────────────────
    def _undo(self):
        history = core.load_undo_history()
        if not history:
            messagebox.showinfo("Desfazer", "Nenhuma organização recente para desfazer.")
            return

        n = len(history.get("actions", []))
        ts = history.get("timestamp", "")
        resp = messagebox.askyesno(
            "Desfazer",
            f"Desfazer última organização?\n\n"
            f"Data: {ts}\n"
            f"Arquivos: {n}",
        )
        if not resp:
            return

        def task():
            core.undo_last_organization(
                logger=self.log,
                progress_callback=self._set_progress,
            )
            self._reset_progress()

        threading.Thread(target=task, daemon=True).start()

    # ──────────────────────────────────────
    # DUPLICADOS
    # ──────────────────────────────────────
    def _find_duplicates(self):
        folder = filedialog.askdirectory(title="Selecionar pasta para buscar duplicados")
        if not folder:
            return

        def task():
            core.find_duplicates(
                folder, self.config,
                logger=self._counting_logger,
                progress_callback=self._set_progress,
            )
            self._reset_progress()

        threading.Thread(target=task, daemon=True).start()

    # ──────────────────────────────────────
    # MONITORAMENTO
    # ──────────────────────────────────────
    def _get_monitored_folders(self) -> list[str]:
        return list(self.folders_listbox.get(0, tk.END))

    def _start_monitoring(self):
        if self.monitoring:
            self.log("⚠️ Monitoramento já está ativo.")
            return

        folders = self._get_monitored_folders()
        if not folders:
            messagebox.showwarning("Aviso", "Adicione pelo menos uma pasta para monitorar.")
            return

        started = 0
        for folder in folders:
            if not os.path.exists(folder):
                self.log(f"⚠️ Pasta não encontrada: {folder}")
                continue

            handler = FolderHandler(folder, self.config, self._counting_logger, notify=True)
            obs = Observer()
            obs.schedule(handler, folder, recursive=False)
            obs.start()
            self.observers[folder] = obs
            started += 1
            self.log(f"👁️ Monitorando: {folder}")

        if started > 0:
            self.monitoring = True
            self.status_var.set(f"Monitorando ({started})")
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")
        else:
            messagebox.showerror("Erro", "Nenhuma pasta válida para monitorar.")

    def _stop_monitoring(self):
        if not self.monitoring:
            return

        for folder, obs in self.observers.items():
            try:
                obs.stop()
                obs.join(timeout=2)
            except Exception:
                pass

        self.observers.clear()
        self.monitoring = False
        self.status_var.set("Parado")
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.log("🛑 Monitoramento encerrado.")

    def _add_monitored_folder(self):
        folder = filedialog.askdirectory(title="Adicionar pasta para monitorar")
        if folder and folder not in self._get_monitored_folders():
            self.folders_listbox.insert(tk.END, folder)
            # Salva no config
            saved = self.config.get("monitored_folders", [])
            saved.append(folder)
            self.config["monitored_folders"] = saved
            core.save_config(self.config)
            self.log(f"➕ Pasta adicionada: {folder}")

    def _remove_monitored_folder(self):
        sel = self.folders_listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Selecione uma pasta na lista para remover.")
            return
        idx = sel[0]
        folder = self.folders_listbox.get(idx)
        self.folders_listbox.delete(idx)
        # Remove do config
        saved = self.config.get("monitored_folders", [])
        if folder in saved:
            saved.remove(folder)
            self.config["monitored_folders"] = saved
            core.save_config(self.config)
        self.log(f"➖ Pasta removida: {folder}")

    # ──────────────────────────────────────
    # TOGGLE DATA
    # ──────────────────────────────────────
    def _toggle_date_mode(self):
        self.config["date_subfolder"] = self.date_var.get()
        core.save_config(self.config)
        state = "ativada" if self.date_var.get() else "desativada"
        self.log(f"📅 Organização por data: {state}")

    # ──────────────────────────────────────
    # EDITOR DE CATEGORIAS
    # ──────────────────────────────────────
    def _edit_categories(self):
        win = tk.Toplevel(self.root)
        win.title("Editar categorias")
        win.geometry("600x500")
        win.configure(bg="#0f172a")
        win.transient(self.root)
        win.grab_set()

        ttk.Label(win, text="Categorias (config.json)", style="Header.TLabel").pack(
            anchor="w", padx=16, pady=(16, 4))

        ttk.Label(
            win,
            text="Edite o JSON abaixo. Cada chave é o nome da pasta e o valor é a lista de extensões.",
            style="SubHeader.TLabel",
        ).pack(anchor="w", padx=16, pady=(0, 10))

        text = scrolledtext.ScrolledText(
            win, wrap=tk.WORD, font=("Consolas", 11),
            bg="#020617", fg="#e2e8f0", insertbackground="#e2e8f0",
            relief="flat", borderwidth=0,
        )
        text.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        text.insert("1.0", json.dumps(self.config.get("categories", {}), indent=4, ensure_ascii=False))

        def save():
            try:
                new_cats = json.loads(text.get("1.0", tk.END))
                self.config["categories"] = new_cats
                core.save_config(self.config)
                self.log("✅ Categorias atualizadas.")
                win.destroy()
            except json.JSONDecodeError as e:
                messagebox.showerror("JSON inválido", f"Erro de sintaxe:\n{e}", parent=win)

        btn_frame = ttk.Frame(win, style="Main.TFrame")
        btn_frame.pack(fill="x", padx=16, pady=(0, 16))
        ttk.Button(btn_frame, text="Salvar", style="Success.TButton", command=save).pack(side="right")
        ttk.Button(btn_frame, text="Cancelar", style="Secondary.TButton",
                   command=win.destroy).pack(side="right", padx=(0, 8))

    # ──────────────────────────────────────
    # EDITOR DE REGRAS
    # ──────────────────────────────────────
    def _edit_rules(self):
        win = tk.Toplevel(self.root)
        win.title("Regras personalizadas")
        win.geometry("650x550")
        win.configure(bg="#0f172a")
        win.transient(self.root)
        win.grab_set()

        ttk.Label(win, text="Regras personalizadas", style="Header.TLabel").pack(
            anchor="w", padx=16, pady=(16, 4))

        ttk.Label(
            win,
            text=(
                "Regras são aplicadas ANTES das categorias por extensão.\n"
                "Condições possíveis: extension, name_contains, name_starts_with\n"
                'Exemplo: {"name": "Notas", "conditions": {"extension": ".pdf", "name_contains": "nota"}, "destination": "Notas Fiscais"}'
            ),
            style="SubHeader.TLabel",
        ).pack(anchor="w", padx=16, pady=(0, 10))

        text = scrolledtext.ScrolledText(
            win, wrap=tk.WORD, font=("Consolas", 11),
            bg="#020617", fg="#e2e8f0", insertbackground="#e2e8f0",
            relief="flat", borderwidth=0,
        )
        text.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        text.insert("1.0", json.dumps(
            self.config.get("custom_rules", []), indent=4, ensure_ascii=False
        ))

        def save():
            try:
                new_rules = json.loads(text.get("1.0", tk.END))
                if not isinstance(new_rules, list):
                    raise ValueError("O JSON precisa ser uma lista [].")
                self.config["custom_rules"] = new_rules
                core.save_config(self.config)
                self.log(f"✅ {len(new_rules)} regra(s) salva(s).")
                win.destroy()
            except (json.JSONDecodeError, ValueError) as e:
                messagebox.showerror("Erro", str(e), parent=win)

        btn_frame = ttk.Frame(win, style="Main.TFrame")
        btn_frame.pack(fill="x", padx=16, pady=(0, 16))
        ttk.Button(btn_frame, text="Salvar", style="Success.TButton", command=save).pack(side="right")
        ttk.Button(btn_frame, text="Cancelar", style="Secondary.TButton",
                   command=win.destroy).pack(side="right", padx=(0, 8))

    # ──────────────────────────────────────
    # SYSTEM TRAY
    # ──────────────────────────────────────
    def _minimize_to_tray(self):
        if not HAS_TRAY:
            self.root.iconify()
            return

        self.root.withdraw()

        image = Image.new("RGB", (64, 64), "#2563eb")
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill="#ffffff")
        draw.rectangle([20, 20, 44, 44], fill="#2563eb")

        menu = pystray.Menu(
            pystray.MenuItem("Abrir", self._restore_from_tray),
            pystray.MenuItem("Sair", self._quit_from_tray),
        )

        self.tray_icon = pystray.Icon("organizador", image, "Organizador de Arquivos", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _restore_from_tray(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.root.after(0, self.root.deiconify)

    def _quit_from_tray(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self.on_close)

    # ──────────────────────────────────────
    # ENCERRAMENTO
    # ──────────────────────────────────────
    def on_close(self):
        if self.monitoring:
            self._stop_monitoring()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.destroy()


# ==========================================
# MAIN
# ==========================================
def main():
    root = tk.Tk()
    app = FileOrganizerApp(root)

    # Minimizar para tray via botão fechar (se habilitado no config)
    def handle_close():
        if app.config.get("minimize_to_tray") and HAS_TRAY:
            app._minimize_to_tray()
        else:
            app.on_close()

    root.protocol("WM_DELETE_WINDOW", handle_close)
    root.mainloop()


if __name__ == "__main__":
    main()
