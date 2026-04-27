"""
organizador_gui.py — Interface gráfica moderna do organizador de arquivos.

Usa customtkinter para visual moderno com cantos arredondados,
sidebar de navegação e melhor experiência do usuário.
"""

import os
import time
import json
import sys
import threading
import ctypes
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Callable

import customtkinter as ctk

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import core
from i18n import get_translator

# Tenta importar pystray (opcional)
try:
    import pystray
    from PIL import Image

    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

# ==========================================
# TEMA E CORES
# ==========================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg_dark": "#0c1017",
    "bg_sidebar": "#111827",
    "bg_card": "#161f2e",
    "bg_card_hover": "#1c2940",
    "bg_input": "#0d1520",
    "border": "#1e293b",
    "accent": "#3b82f6",
    "accent_hover": "#2563eb",
    "green": "#22c55e",
    "green_dim": "#15803d",
    "yellow": "#f59e0b",
    "yellow_dim": "#b45309",
    "red": "#ef4444",
    "red_dim": "#b91c1c",
    "purple": "#8b5cf6",
    "cyan": "#06b6d4",
    "text_primary": "#f1f5f9",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
}

ICON_ICO_PATH = os.path.join("icons", "sortify.ico")
ICON_PNG_PATH = os.path.join("icons", "sortify.png")
APP_USER_MODEL_ID = "com.sortify.desktophelper"


def get_resource_path(relative_path: str) -> str:
    """Resolve caminho para arquivos locais e para bundle do PyInstaller."""
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


def set_windows_app_id() -> None:
    """
    Define um AppUserModelID explícito no Windows.

    Isso ajuda o Windows a aplicar corretamente o ícone no atalho do app e
    também na barra de tarefas, em vez do ícone padrão do Python.
    """
    if os.name != "nt":
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            APP_USER_MODEL_ID
        )
    except (AttributeError, OSError):
        pass


# ==========================================
# TOOLTIP
# ==========================================
class ToolTip:
    """Tooltip leve para widgets."""

    def __init__(self, widget, text: str, delay: int = 400):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._tip_window = None
        self._after_id = None
        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._hide)

    def _schedule(self, event=None):
        self._after_id = self.widget.after(self.delay, self._show)

    def _show(self):
        if self._tip_window:
            return
        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self._tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.configure(bg="#1e293b")
        label = tk.Label(
            tw,
            text=self.text,
            bg="#1e293b",
            fg="#e2e8f0",
            font=("Segoe UI", 9),
            padx=10,
            pady=5,
        )
        label.pack()

    def _hide(self, event=None):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        if self._tip_window:
            self._tip_window.destroy()
            self._tip_window = None


# ==========================================
# HANDLER DO WATCHDOG
# ==========================================
class FolderHandler(FileSystemEventHandler):
    def __init__(self, folder_path, config, logger, notify=True):
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
class FileOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sortify")
        self.geometry("1100x750")
        self.minsize(900, 600)
        self.configure(fg_color=COLORS["bg_dark"])
        self._apply_window_icon()

        self.config_data = core.load_config()
        self.i18n = get_translator(self.config_data.get("language", "pt"))
        self.tr = self.i18n.get

        # Estado
        self.observers: dict[str, Observer] = {}
        self.monitoring = False
        self.scheduler_running = False
        self.scheduler_thread = None
        self.scheduler_stop_event = threading.Event()
        self.scheduler_last_daily_key = ""
        self.scheduler_last_interval_run = 0.0
        self.scheduler_task_running = False
        self.counter_moved = 0
        self.counter_ignored = 0
        self.counter_errors = 0
        self.tray_icon = None

        # Variáveis de UI
        self.status_text = tk.StringVar(value=self.tr("status_stopped", "Parado"))
        self.progress_var = tk.DoubleVar(value=0)
        self.date_var = tk.BooleanVar(value=self.config_data.get("date_subfolder", False))
        self.scheduled_enabled_var = tk.BooleanVar(
            value=self.config_data.get("scheduled_enabled", False)
        )
        self.scheduled_mode_var = tk.StringVar(
            value=self.config_data.get("scheduled_mode", "daily")
        )
        self.scheduled_time_var = tk.StringVar(
            value=self.config_data.get("scheduled_time", "18:00")
        )
        self.scheduled_interval_var = tk.StringVar(
            value=str(self.config_data.get("scheduled_interval_minutes", 60))
        )

        # Páginas
        self.pages: dict[str, ctk.CTkFrame] = {}
        self.current_page = None
        self.nav_buttons: dict[str, ctk.CTkButton] = {}

        self._build_layout()
        self._show_page("dashboard")
        if self.config_data.get("scheduled_enabled", False):
            self._start_scheduler()

    # ──────────────────────────────────────
    # LAYOUT PRINCIPAL
    # ──────────────────────────────────────
    def _build_layout(self):
        # Grid: sidebar (fixo) + conteúdo (expande)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content_area()

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
            fg_color=COLORS["bg_sidebar"],
            border_width=0,
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # Logo / Branding
        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=20, pady=(28, 8))

        ctk.CTkLabel(
            brand,
            text="⚡ Sortify",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            brand,
            text=self.tr("sidebar_subtitle", "Organizador de Arquivos"),
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(2, 0))

        # Separador
        sep = ctk.CTkFrame(sidebar, height=1, fg_color=COLORS["border"])
        sep.pack(fill="x", padx=20, pady=(20, 16))

        # Navegação
        nav_items = [
            ("dashboard", "📊", self.tr("nav_dashboard", "Dashboard")),
            ("organize", "📁", self.tr("nav_organize", "Organizar")),
            ("monitor", "👁", self.tr("nav_monitor", "Monitorar")),
            ("settings", "⚙️", self.tr("nav_settings", "Configurações")),
            ("logs", "📋", self.tr("nav_logs", "Logs")),
        ]

        for page_id, icon, label in nav_items:
            btn = ctk.CTkButton(
                sidebar,
                text=f"  {icon}  {label}",
                anchor="w",
                height=42,
                corner_radius=10,
                font=ctk.CTkFont(size=13),
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["bg_card"],
                command=lambda pid=page_id: self._show_page(pid),
            )
            btn.pack(fill="x", padx=12, pady=2)
            self.nav_buttons[page_id] = btn

        # Spacer
        spacer = ctk.CTkFrame(sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # Status no rodapé da sidebar
        status_frame = ctk.CTkFrame(sidebar, fg_color=COLORS["bg_card"], corner_radius=12)
        status_frame.pack(fill="x", padx=16, pady=(0, 20))

        status_inner = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_inner.pack(fill="x", padx=14, pady=12)

        ctk.CTkLabel(
            status_inner,
            text=self.tr("status_label", "Status"),
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w")

        self.status_dot = ctk.CTkLabel(
            status_inner,
            text="●  ",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
        )
        self.status_dot.pack(side="left", anchor="w", pady=(2, 0))

        self.status_label = ctk.CTkLabel(
            status_inner,
            textvariable=self.status_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_secondary"],
        )
        self.status_label.pack(side="left", anchor="w", pady=(2, 0))

    def _build_content_area(self):
        self.content = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # Cria todas as páginas
        self._create_dashboard_page()
        self._create_organize_page()
        self._create_monitor_page()
        self._create_settings_page()
        self._create_logs_page()

    def _show_page(self, page_id: str):
        # Esconde página atual
        if self.current_page and self.current_page in self.pages:
            self.pages[self.current_page].grid_remove()

        # Atualiza botões da sidebar
        for pid, btn in self.nav_buttons.items():
            if pid == page_id:
                btn.configure(
                    fg_color=COLORS["accent"],
                    text_color="#ffffff",
                    hover_color=COLORS["accent_hover"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"],
                    hover_color=COLORS["bg_card"],
                )

        # Mostra nova página
        self.pages[page_id].grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.current_page = page_id

    # ──────────────────────────────────────
    # HELPERS DE UI
    # ──────────────────────────────────────
    def _apply_window_icon(self):
        ico_path = get_resource_path(ICON_ICO_PATH)
        png_path = get_resource_path(ICON_PNG_PATH)

        if os.name == "nt" and os.path.exists(ico_path):
            try:
                self.iconbitmap(default=ico_path)
            except tk.TclError:
                pass

        if os.path.exists(png_path):
            try:
                self._app_icon_image = tk.PhotoImage(file=png_path)
                self.iconphoto(True, self._app_icon_image)
            except tk.TclError:
                self._app_icon_image = None

    def _make_page(self, page_id: str) -> ctk.CTkScrollableFrame:
        page = ctk.CTkScrollableFrame(
            self.content,
            fg_color=COLORS["bg_dark"],
            corner_radius=0,
            scrollbar_button_color=COLORS["bg_card"],
            scrollbar_button_hover_color=COLORS["bg_card_hover"],
        )
        self.pages[page_id] = page
        return page

    def _make_card(self, parent, **kwargs) -> ctk.CTkFrame:
        return ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=14,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )

    def _make_section_title(self, parent, icon: str, title: str):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=28, pady=(24, 12))
        ctk.CTkLabel(
            frame,
            text=f"{icon}  {title}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")
        return frame

    def _make_action_button(
        self, parent, text, command, color=None, hover=None, icon_text=None, tooltip=None, width=None
    ):
        fg = color or COLORS["accent"]
        hv = hover or COLORS["accent_hover"]
        display = f"{icon_text}  {text}" if icon_text else text
        btn = ctk.CTkButton(
            parent,
            text=display,
            command=command,
            fg_color=fg,
            hover_color=hv,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            width=width or 0,
        )
        if tooltip:
            ToolTip(btn, tooltip)
        return btn

    # ──────────────────────────────────────
    # PÁGINA: DASHBOARD
    # ──────────────────────────────────────
    def _create_dashboard_page(self):
        page = self._make_page("dashboard")

        # Cabeçalho
        header = ctk.CTkFrame(page, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(24, 6))
        ctk.CTkLabel(
            header,
            text=self.tr("dashboard_title", "Dashboard"),
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=self.tr("dashboard_subtitle", "Visão geral da sessão atual"),
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_muted"],
        ).pack(side="left", padx=(14, 0), pady=(6, 0))

        # Cards de contadores
        cards_frame = ctk.CTkFrame(page, fg_color="transparent")
        cards_frame.pack(fill="x", padx=28, pady=(16, 8))
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1)

        counter_configs = [
            (self.tr("counter_moved", "Movidos"), "counter_moved_lbl", COLORS["green"], self.tr("tip_moved", "Arquivos organizados nesta sessão")),
            (self.tr("counter_ignored", "Ignorados"), "counter_ignored_lbl", COLORS["yellow"], self.tr("tip_ignored", "Arquivos ignorados por extensão/nome")),
            (self.tr("counter_errors", "Erros"), "counter_errors_lbl", COLORS["red"], self.tr("tip_errors", "Erros ao mover arquivos")),
            (self.tr("counter_status", "Status"), "status_card_lbl", COLORS["cyan"], self.tr("tip_status", "Estado do monitoramento")),
        ]

        for col, (label, attr, color, tip) in enumerate(counter_configs):
            card = self._make_card(cards_frame)
            padx = (0, 6) if col == 0 else (6, 0) if col == 3 else 6
            card.grid(row=0, column=col, sticky="nsew", padx=padx, pady=4)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", padx=18, pady=16)

            # Indicador de cor
            dot = ctk.CTkFrame(inner, width=8, height=8, corner_radius=4, fg_color=color)
            dot.pack(anchor="w", pady=(0, 8))

            ctk.CTkLabel(
                inner,
                text=label,
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_muted"],
            ).pack(anchor="w")

            if attr == "status_card_lbl":
                lbl = ctk.CTkLabel(
                    inner,
                    textvariable=self.status_text,
                    font=ctk.CTkFont(size=22, weight="bold"),
                    text_color=color,
                )
            else:
                lbl = ctk.CTkLabel(
                    inner,
                    text="0",
                    font=ctk.CTkFont(size=28, weight="bold"),
                    text_color=color,
                )
                setattr(self, attr, lbl)

            lbl.pack(anchor="w", pady=(4, 0))
            ToolTip(card, tip)

        # Ações rápidas
        self._make_section_title(page, "⚡", self.tr("quick_actions", "Ações rápidas"))

        quick_card = self._make_card(page)
        quick_card.pack(fill="x", padx=28, pady=(0, 8))

        quick_inner = ctk.CTkFrame(quick_card, fg_color="transparent")
        quick_inner.pack(fill="x", padx=18, pady=16)

        btns_data = [
            ("Downloads", self._organize_downloads, COLORS["accent"], COLORS["accent_hover"], "📥", "Organizar pasta Downloads"),
            ("Desktop", self._organize_desktop, COLORS["accent"], COLORS["accent_hover"], "🖥️", "Organizar pasta Desktop"),
            ("Outra pasta", self._organize_custom, COLORS["purple"], "#7c3aed", "📂", "Escolher pasta para organizar"),
            ("Simular", self._simulate, COLORS["yellow_dim"], COLORS["yellow_dim"], "🔍", "Ver o que seria feito sem mover"),
            ("Desfazer", self._undo, "#475569", "#374151", "⏪", "Reverter última organização"),
            ("Duplicados", self._find_duplicates, "#475569", "#374151", "📄", "Encontrar e mover arquivos duplicados"),
        ]

        for i in range(len(btns_data)):
            quick_inner.columnconfigure(i, weight=1)

        for col, (text, cmd, fg, hv, icon, tip) in enumerate(btns_data):
            btn = self._make_action_button(quick_inner, text, cmd, fg, hv, icon, tip)
            padx = (0, 4) if col == 0 else (4, 0) if col == len(btns_data) - 1 else 4
            btn.grid(row=0, column=col, sticky="ew", padx=padx)

        # Progresso
        self._make_section_title(page, "📊", self.tr("progress", "Progresso"))

        prog_card = self._make_card(page)
        prog_card.pack(fill="x", padx=28, pady=(0, 8))

        prog_inner = ctk.CTkFrame(prog_card, fg_color="transparent")
        prog_inner.pack(fill="x", padx=18, pady=16)

        self.progress_bar = ctk.CTkProgressBar(
            prog_inner,
            height=10,
            corner_radius=5,
            fg_color=COLORS["bg_input"],
            progress_color=COLORS["accent"],
            variable=self.progress_var,
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(
            prog_inner,
            text=self.tr("no_task", "Nenhuma tarefa em andamento"),
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
        )
        self.progress_label.pack(anchor="w", pady=(8, 0))

    # ──────────────────────────────────────
    # PÁGINA: ORGANIZAR
    # ──────────────────────────────────────
    def _create_organize_page(self):
        page = self._make_page("organize")

        self._make_section_title(page, "📁", "Organizar Arquivos")

        ctk.CTkLabel(
            page,
            text="Escolha uma pasta para organizar automaticamente por tipo de arquivo.",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", padx=28, pady=(0, 16))

        # Card principal
        card = self._make_card(page)
        card.pack(fill="x", padx=28, pady=(0, 12))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=20)

        # Pastas padrão
        ctk.CTkLabel(
            inner,
            text="Pastas padrão",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 10))

        row1 = ctk.CTkFrame(inner, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 16))

        btn_dl = self._make_action_button(
            row1, "Organizar Downloads", self._organize_downloads,
            icon_text="📥", tooltip="Organizar pasta Downloads", width=220
        )
        btn_dl.pack(side="left", padx=(0, 8))

        btn_dt = self._make_action_button(
            row1, "Organizar Desktop", self._organize_desktop,
            icon_text="🖥️", tooltip="Organizar pasta Desktop", width=220
        )
        btn_dt.pack(side="left", padx=(0, 8))

        # Separador
        ctk.CTkFrame(inner, height=1, fg_color=COLORS["border"]).pack(fill="x", pady=(0, 16))

        # Pasta customizada
        ctk.CTkLabel(
            inner,
            text="Pasta personalizada",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 10))

        custom_row = ctk.CTkFrame(inner, fg_color="transparent")
        custom_row.pack(fill="x", pady=(0, 12))

        self._make_action_button(
            custom_row, "Escolher pasta...", self._organize_custom,
            COLORS["purple"], "#7c3aed", "📂",
            "Selecionar qualquer pasta para organizar", width=200
        ).pack(side="left", padx=(0, 8))

        self._make_action_button(
            custom_row, "Simular primeiro", self._simulate,
            COLORS["yellow_dim"], "#92400e", "🔍",
            "Visualizar ações antes de executar", width=200
        ).pack(side="left", padx=(0, 8))

        # Separador
        ctk.CTkFrame(inner, height=1, fg_color=COLORS["border"]).pack(fill="x", pady=(0, 16))

        # Opções
        ctk.CTkLabel(
            inner,
            text="Opções",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 10))

        opts = ctk.CTkFrame(inner, fg_color="transparent")
        opts.pack(fill="x")

        date_switch = ctk.CTkSwitch(
            opts,
            text="  Criar sub-pastas por data (Ano/Mês)",
            variable=self.date_var,
            command=self._toggle_date_mode,
            font=ctk.CTkFont(size=12),
            progress_color=COLORS["accent"],
        )
        date_switch.pack(anchor="w", pady=4)
        ToolTip(date_switch, "Cria sub-pastas como PDFs/2026/04-Abril/")

        # Card de ferramentas
        tools_title = self._make_section_title(page, "🛠️", "Ferramentas")

        tools_card = self._make_card(page)
        tools_card.pack(fill="x", padx=28, pady=(0, 12))

        tools_inner = ctk.CTkFrame(tools_card, fg_color="transparent")
        tools_inner.pack(fill="x", padx=20, pady=20)

        tools_row = ctk.CTkFrame(tools_inner, fg_color="transparent")
        tools_row.pack(fill="x")

        self._make_action_button(
            tools_row, "Buscar duplicados", self._find_duplicates,
            "#475569", "#374151", "📄",
            "Encontrar e mover arquivos duplicados por hash MD5", width=200
        ).pack(side="left", padx=(0, 8))

        self._make_action_button(
            tools_row, "Desfazer última organização", self._undo,
            COLORS["red_dim"], "#991b1b", "⏪",
            "Reverter todos os arquivos da última organização", width=260
        ).pack(side="left")

    # ──────────────────────────────────────
    # PÁGINA: MONITORAR
    # ──────────────────────────────────────
    def _create_monitor_page(self):
        page = self._make_page("monitor")

        self._make_section_title(page, "👁", "Monitoramento em Tempo Real")

        ctk.CTkLabel(
            page,
            text="Monitore pastas e organize novos arquivos automaticamente.",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", padx=28, pady=(0, 16))

        # Controles
        ctrl_card = self._make_card(page)
        ctrl_card.pack(fill="x", padx=28, pady=(0, 12))

        ctrl_inner = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        ctrl_inner.pack(fill="x", padx=20, pady=16)

        ctrl_row = ctk.CTkFrame(ctrl_inner, fg_color="transparent")
        ctrl_row.pack(fill="x")

        self.btn_start = self._make_action_button(
            ctrl_row, "Iniciar monitoramento", self._start_monitoring,
            COLORS["green"], COLORS["green_dim"], "▶",
            "Começar a monitorar as pastas da lista", width=220
        )
        self.btn_start.pack(side="left", padx=(0, 8))

        self.btn_stop = self._make_action_button(
            ctrl_row, "Parar monitoramento", self._stop_monitoring,
            COLORS["red"], COLORS["red_dim"], "■",
            "Parar todo o monitoramento", width=220
        )
        self.btn_stop.pack(side="left")
        self.btn_stop.configure(state="disabled")

        # Lista de pastas
        folders_title = self._make_section_title(page, "📂", "Pastas monitoradas")

        # Botões de adicionar/remover
        folder_actions = ctk.CTkFrame(page, fg_color="transparent")
        folder_actions.pack(fill="x", padx=28, pady=(0, 8))

        self._make_action_button(
            folder_actions, "Adicionar pasta", self._add_monitored_folder,
            COLORS["accent"], COLORS["accent_hover"], "+", width=180
        ).pack(side="left", padx=(0, 8))

        self._make_action_button(
            folder_actions, "Remover selecionada", self._remove_monitored_folder,
            COLORS["red_dim"], "#991b1b", "−", width=180
        ).pack(side="left")

        # Lista
        list_card = self._make_card(page)
        list_card.pack(fill="x", padx=28, pady=(0, 12))

        list_inner = ctk.CTkFrame(list_card, fg_color="transparent")
        list_inner.pack(fill="both", padx=4, pady=4)

        self.folders_listbox = tk.Listbox(
            list_inner,
            height=6,
            font=("Consolas", 11),
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            selectbackground=COLORS["accent"],
            selectforeground="#ffffff",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            activestyle="none",
        )
        self.folders_listbox.pack(fill="both", padx=10, pady=10)

        # Popula pastas
        default_folders = [core.DOWNLOADS_PATH, core.DESKTOP_PATH]
        saved = self.config_data.get("monitored_folders", [])
        all_folders = list(dict.fromkeys(default_folders + saved))
        for f in all_folders:
            self.folders_listbox.insert(tk.END, f)

        # Agendamento periódico
        self._make_section_title(page, "⏰", "Agendamento Periódico")

        schedule_card = self._make_card(page)
        schedule_card.pack(fill="x", padx=28, pady=(0, 12))

        schedule_inner = ctk.CTkFrame(schedule_card, fg_color="transparent")
        schedule_inner.pack(fill="x", padx=20, pady=16)

        schedule_switch = ctk.CTkSwitch(
            schedule_inner,
            text="  Habilitar organização automática agendada",
            variable=self.scheduled_enabled_var,
            command=self._toggle_scheduled_enabled,
            font=ctk.CTkFont(size=12),
            progress_color=COLORS["accent"],
        )
        schedule_switch.pack(anchor="w", pady=(0, 12))

        mode_row = ctk.CTkFrame(schedule_inner, fg_color="transparent")
        mode_row.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            mode_row,
            text="Modo:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(0, 10))

        self.schedule_mode_menu = ctk.CTkOptionMenu(
            mode_row,
            values=[self.tr("schedule_daily", "Diário"), self.tr("schedule_interval", "Intervalo")],
            command=self._on_schedule_mode_change,
            width=140,
        )
        self.schedule_mode_menu.pack(side="left")

        controls_row = ctk.CTkFrame(schedule_inner, fg_color="transparent")
        controls_row.pack(fill="x", pady=(4, 8))

        self.schedule_time_label = ctk.CTkLabel(
            controls_row,
            text="Hora (HH:MM):",
            text_color=COLORS["text_secondary"],
        )
        self.schedule_time_label.pack(side="left", padx=(0, 8))

        self.schedule_time_entry = ctk.CTkEntry(
            controls_row,
            textvariable=self.scheduled_time_var,
            width=110,
        )
        self.schedule_time_entry.pack(side="left", padx=(0, 16))

        self.schedule_interval_label = ctk.CTkLabel(
            controls_row,
            text="Intervalo (min):",
            text_color=COLORS["text_secondary"],
        )
        self.schedule_interval_label.pack(side="left", padx=(0, 8))

        self.schedule_interval_entry = ctk.CTkEntry(
            controls_row,
            textvariable=self.scheduled_interval_var,
            width=110,
        )
        self.schedule_interval_entry.pack(side="left")

        save_row = ctk.CTkFrame(schedule_inner, fg_color="transparent")
        save_row.pack(fill="x", pady=(8, 0))
        self._make_action_button(
            save_row,
            "Salvar agendamento",
            self._save_schedule_settings,
            COLORS["green"],
            COLORS["green_dim"],
            "💾",
            width=190,
        ).pack(side="left")

        mode_label = self.tr("schedule_daily", "Diário") if self.scheduled_mode_var.get() == "daily" else self.tr("schedule_interval", "Intervalo")
        self.schedule_mode_menu.set(mode_label)
        self._sync_schedule_controls()

    # ──────────────────────────────────────
    # PÁGINA: CONFIGURAÇÕES
    # ──────────────────────────────────────
    def _create_settings_page(self):
        page = self._make_page("settings")

        self._make_section_title(page, "⚙️", "Configurações")

        ctk.CTkLabel(
            page,
            text="Edite as categorias de extensão e regras personalizadas.",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", padx=28, pady=(0, 16))

        # Card: Categorias
        cat_card = self._make_card(page)
        cat_card.pack(fill="x", padx=28, pady=(0, 12))

        cat_inner = ctk.CTkFrame(cat_card, fg_color="transparent")
        cat_inner.pack(fill="x", padx=20, pady=18)

        cat_header = ctk.CTkFrame(cat_inner, fg_color="transparent")
        cat_header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            cat_header,
            text="Categorias por extensão",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        self._make_action_button(
            cat_header, "Salvar categorias", self._save_categories,
            COLORS["green"], COLORS["green_dim"], "💾", width=170
        ).pack(side="right")

        ctk.CTkLabel(
            cat_inner,
            text='Cada chave é o nome da pasta destino. O valor é a lista de extensões.',
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(0, 8))

        self.cat_textbox = ctk.CTkTextbox(
            cat_inner,
            height=200,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
        )
        self.cat_textbox.pack(fill="x")
        self.cat_textbox.insert(
            "1.0",
            json.dumps(self.config_data.get("categories", {}), indent=4, ensure_ascii=False),
        )

        # Card: Regras
        rules_card = self._make_card(page)
        rules_card.pack(fill="x", padx=28, pady=(0, 12))

        rules_inner = ctk.CTkFrame(rules_card, fg_color="transparent")
        rules_inner.pack(fill="x", padx=20, pady=18)

        rules_header = ctk.CTkFrame(rules_inner, fg_color="transparent")
        rules_header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            rules_header,
            text="Regras personalizadas",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        self._make_action_button(
            rules_header, "Salvar regras", self._save_rules,
            COLORS["green"], COLORS["green_dim"], "💾", width=160
        ).pack(side="right")

        ctk.CTkLabel(
            rules_inner,
            text="Regras são aplicadas ANTES das categorias. Condições: extension, name_contains, name_starts_with",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
            wraplength=600,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))

        self.rules_textbox = ctk.CTkTextbox(
            rules_inner,
            height=180,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
        )
        self.rules_textbox.pack(fill="x")
        self.rules_textbox.insert(
            "1.0",
            json.dumps(self.config_data.get("custom_rules", []), indent=4, ensure_ascii=False),
        )

    # ──────────────────────────────────────
    # PÁGINA: LOGS
    # ──────────────────────────────────────
    def _create_logs_page(self):
        page = self._make_page("logs")

        title_frame = self._make_section_title(page, "📋", "Logs do Sistema")

        self._make_action_button(
            title_frame, "Limpar", self._clear_logs,
            "#475569", "#374151", width=100
        ).pack(side="right")

        # Log area
        log_card = self._make_card(page)
        log_card.pack(fill="both", expand=True, padx=28, pady=(0, 16))

        self.log_textbox = ctk.CTkTextbox(
            log_card,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"],
            corner_radius=10,
            border_width=0,
            wrap="word",
            activate_scrollbars=True,
        )
        self.log_textbox.pack(fill="both", expand=True, padx=8, pady=8)
        self.log_textbox.configure(state="disabled")

        self.log("🚀 Sistema iniciado.")
        self.log("💡 Use a sidebar para navegar entre as seções.")

    # ──────────────────────────────────────
    # LOGGING
    # ──────────────────────────────────────
    def log(self, message: str):
        def _append():
            t = time.strftime("%H:%M:%S")
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", f"[{t}]  {message}\n")
            self.log_textbox.see("end")
            self.log_textbox.configure(state="disabled")

        self.after(0, _append)

    def _clear_logs(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

    # ──────────────────────────────────────
    # PROGRESSO
    # ──────────────────────────────────────
    def _set_progress(self, current: int, total: int):
        if total <= 0:
            return
        pct = current / total
        self.after(0, lambda: self.progress_bar.set(pct))
        self.after(
            0,
            lambda: self.progress_label.configure(
                text=self.tr("processing_files", "Processando {current}/{total} arquivos...", current=current, total=total),
                text_color=COLORS["accent"],
            ),
        )

    def _reset_progress(self):
        self.after(0, lambda: self.progress_bar.set(0))
        self.after(
            0,
            lambda: self.progress_label.configure(
                text=self.tr("no_task", "Nenhuma tarefa em andamento"),
                text_color=COLORS["text_muted"],
            ),
        )

    # ──────────────────────────────────────
    # CONTADORES
    # ──────────────────────────────────────
    def _update_counter_display(self):
        self.counter_moved_lbl.configure(text=str(self.counter_moved))
        self.counter_ignored_lbl.configure(text=str(self.counter_ignored))
        self.counter_errors_lbl.configure(text=str(self.counter_errors))

    def _counting_logger(self, message: str):
        self.log(message)
        if message.startswith("✅"):
            self.counter_moved += 1
        elif message.startswith("⚠️"):
            self.counter_ignored += 1
        elif message.startswith("❌"):
            self.counter_errors += 1
        self.after(0, self._update_counter_display)

    def _run_background_task(self, target: Callable[[], None]):
        threading.Thread(target=target, daemon=True).start()

    # ──────────────────────────────────────
    # ORGANIZAÇÃO
    # ──────────────────────────────────────
    def _organize_folder(self, folder_path: str):
        def task():
            core.organize_folder(
                folder_path,
                self.config_data,
                logger=self._counting_logger,
                progress_callback=self._set_progress,
                notify=self.config_data.get("notifications_enabled", False),
            )
            self._reset_progress()

        self._run_background_task(task)

    def _organize_downloads(self):
        self._show_page("logs")
        self._organize_folder(core.DOWNLOADS_PATH)

    def _organize_desktop(self):
        self._show_page("logs")
        self._organize_folder(core.DESKTOP_PATH)

    def _organize_custom(self):
        folder = filedialog.askdirectory(title="Selecionar pasta para organizar")
        if folder:
            self._show_page("logs")
            self._organize_folder(folder)

    # ──────────────────────────────────────
    # SIMULAÇÃO
    # ──────────────────────────────────────
    def _simulate(self):
        folder = filedialog.askdirectory(title="Selecionar pasta para simular")
        if not folder:
            return

        self._show_page("logs")

        def task():
            self.log(f"🔍 Simulação para: {folder}")
            actions = core.simulate_organization(folder, self.config_data, logger=self.log)
            if not actions:
                self.log("📭 Nenhum arquivo para organizar nesta pasta.")
                return
            self.after(0, lambda: self._confirm_simulation(folder, actions))

        self._run_background_task(task)

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
            f"Desfazer última organização?\n\nData: {ts}\nArquivos: {n}",
        )
        if not resp:
            return

        self._show_page("logs")

        def task():
            core.undo_last_organization(
                logger=self.log,
                progress_callback=self._set_progress,
                notify=self.config_data.get("notifications_enabled", False),
            )
            self._reset_progress()

        self._run_background_task(task)

    # ──────────────────────────────────────
    # DUPLICADOS
    # ──────────────────────────────────────
    def _find_duplicates(self):
        folder = filedialog.askdirectory(title="Selecionar pasta para buscar duplicados")
        if not folder:
            return

        self._show_page("logs")

        def task():
            core.find_duplicates(
                folder,
                self.config_data,
                logger=self._counting_logger,
                progress_callback=self._set_progress,
                notify=True,
            )
            self._reset_progress()

        self._run_background_task(task)

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

            handler = FolderHandler(folder, self.config_data, self._counting_logger, notify=True)
            obs = Observer()
            obs.schedule(handler, folder, recursive=False)
            obs.start()
            self.observers[folder] = obs
            started += 1
            self.log(f"👁️ Monitorando: {folder}")

        if started > 0:
            self.monitoring = True
            self.status_text.set(f"Monitorando ({started})")
            self.status_dot.configure(text_color=COLORS["green"])
            self.status_label.configure(text_color=COLORS["green"])
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="normal")
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
        self.status_text.set(self.tr("status_stopped", "Parado"))
        self.status_dot.configure(text_color=COLORS["text_muted"])
        self.status_label.configure(text_color=COLORS["text_secondary"])
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.log("🛑 Monitoramento encerrado.")

    def _add_monitored_folder(self):
        folder = filedialog.askdirectory(title="Adicionar pasta para monitorar")
        if folder and folder not in self._get_monitored_folders():
            self.folders_listbox.insert(tk.END, folder)
            saved = self.config_data.get("monitored_folders", [])
            saved.append(folder)
            self.config_data["monitored_folders"] = saved
            core.save_config(self.config_data)
            self.log(f"➕ Pasta adicionada: {folder}")

    def _remove_monitored_folder(self):
        sel = self.folders_listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Selecione uma pasta na lista para remover.")
            return
        idx = sel[0]
        folder = self.folders_listbox.get(idx)
        self.folders_listbox.delete(idx)
        saved = self.config_data.get("monitored_folders", [])
        if folder in saved:
            saved.remove(folder)
            self.config_data["monitored_folders"] = saved
            core.save_config(self.config_data)
        self.log(f"➖ Pasta removida: {folder}")

    # ──────────────────────────────────────
    # AGENDAMENTO
    # ──────────────────────────────────────
    def _on_schedule_mode_change(self, selected: str):
        mode = "daily" if selected == self.tr("schedule_daily", "Diário") else "interval"
        self.scheduled_mode_var.set(mode)
        self._sync_schedule_controls()

    def _sync_schedule_controls(self):
        is_daily = self.scheduled_mode_var.get() == "daily"
        self.schedule_time_label.configure(
            text_color=COLORS["text_secondary"] if is_daily else COLORS["text_muted"]
        )
        self.schedule_time_entry.configure(state="normal" if is_daily else "disabled")
        self.schedule_interval_label.configure(
            text_color=COLORS["text_secondary"] if not is_daily else COLORS["text_muted"]
        )
        self.schedule_interval_entry.configure(state="normal" if not is_daily else "disabled")

    def _save_schedule_settings(self):
        mode = self.scheduled_mode_var.get()
        if mode not in ("daily", "interval"):
            mode = "daily"

        schedule_time = self.scheduled_time_var.get().strip()
        if len(schedule_time) != 5 or schedule_time[2] != ":":
            messagebox.showerror("Erro", "Hora inválida. Use o formato HH:MM.")
            return
        hh, mm = schedule_time.split(":")
        if not (hh.isdigit() and mm.isdigit() and 0 <= int(hh) <= 23 and 0 <= int(mm) <= 59):
            messagebox.showerror("Erro", "Hora inválida. Use horário 24h (00:00 até 23:59).")
            return

        interval_raw = self.scheduled_interval_var.get().strip()
        if not interval_raw.isdigit() or int(interval_raw) <= 0:
            messagebox.showerror("Erro", "Intervalo inválido. Informe minutos inteiros > 0.")
            return

        self.config_data["scheduled_mode"] = mode
        self.config_data["scheduled_time"] = schedule_time
        self.config_data["scheduled_interval_minutes"] = int(interval_raw)
        self.config_data["scheduled_enabled"] = self.scheduled_enabled_var.get()
        core.save_config(self.config_data)
        self.log("✅ Agendamento salvo.")

        if self.config_data["scheduled_enabled"]:
            self._start_scheduler()
        else:
            self._stop_scheduler()

    def _toggle_scheduled_enabled(self):
        self.config_data["scheduled_enabled"] = self.scheduled_enabled_var.get()
        core.save_config(self.config_data)
        if self.scheduled_enabled_var.get():
            self._start_scheduler()
            self.log("⏰ Agendamento automático ativado.")
        else:
            self._stop_scheduler()
            self.log("🛑 Agendamento automático desativado.")

    def _start_scheduler(self):
        if self.scheduler_running:
            return
        self.scheduler_stop_event.clear()
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        self.log("⏱️ Scheduler iniciado.")

    def _stop_scheduler(self):
        if not self.scheduler_running:
            return
        self.scheduler_stop_event.set()
        self.scheduler_running = False
        self.log("⏹️ Scheduler parado.")

    def _scheduler_loop(self):
        while not self.scheduler_stop_event.wait(15):
            if not self.config_data.get("scheduled_enabled", False):
                continue
            if self.scheduler_task_running:
                continue

            folders = self._get_monitored_folders()
            if not folders:
                continue

            mode = self.config_data.get("scheduled_mode", "daily")
            now = datetime.now()

            if mode == "daily":
                schedule_time = str(self.config_data.get("scheduled_time", "18:00"))
                try:
                    hh, mm = [int(x) for x in schedule_time.split(":")]
                except (ValueError, TypeError):
                    continue
                if now.hour == hh and now.minute == mm:
                    run_key = now.strftime("%Y-%m-%d") + f"-{hh:02d}:{mm:02d}"
                    if run_key != self.scheduler_last_daily_key:
                        self.scheduler_last_daily_key = run_key
                        self._run_scheduled_organization("diário", folders)

            elif mode == "interval":
                interval_minutes = int(self.config_data.get("scheduled_interval_minutes", 60))
                interval_seconds = max(60, interval_minutes * 60)
                elapsed = time.time() - self.scheduler_last_interval_run
                if elapsed >= interval_seconds:
                    self.scheduler_last_interval_run = time.time()
                    self._run_scheduled_organization(f"a cada {interval_minutes} min", folders)

    def _run_scheduled_organization(self, reason: str, folders: list[str]):
        valid_folders = [folder for folder in folders if os.path.exists(folder)]
        if not valid_folders:
            return

        def task():
            self.scheduler_task_running = True
            try:
                self.log(
                    f"⏰ Organização agendada ({reason}) iniciada em {len(valid_folders)} pasta(s)."
                )
                for folder in valid_folders:
                    core.organize_folder(
                        folder,
                        self.config_data,
                        logger=self._counting_logger,
                        progress_callback=self._set_progress,
                        notify=self.config_data.get("notifications_enabled", False),
                    )
                self.log("✅ Organização agendada concluída.")
            finally:
                self.scheduler_task_running = False
                self._reset_progress()

        self._run_background_task(task)

    # ──────────────────────────────────────
    # TOGGLE DATA
    # ──────────────────────────────────────
    def _toggle_date_mode(self):
        self.config_data["date_subfolder"] = self.date_var.get()
        core.save_config(self.config_data)
        state = "ativada" if self.date_var.get() else "desativada"
        self.log(f"📅 Organização por data: {state}")

    # ──────────────────────────────────────
    # SALVAR CATEGORIAS / REGRAS
    # ──────────────────────────────────────
    def _save_categories(self):
        try:
            text = self.cat_textbox.get("1.0", "end")
            new_cats = json.loads(text)
            self.config_data["categories"] = new_cats
            core.save_config(self.config_data)
            self.log("✅ Categorias atualizadas.")
            messagebox.showinfo("Sucesso", "Categorias salvas com sucesso!")
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON inválido", f"Erro de sintaxe:\n{e}")

    def _save_rules(self):
        try:
            text = self.rules_textbox.get("1.0", "end")
            new_rules = json.loads(text)
            if not isinstance(new_rules, list):
                raise ValueError("O JSON precisa ser uma lista [].")
            self.config_data["custom_rules"] = new_rules
            core.save_config(self.config_data)
            self.log(f"✅ {len(new_rules)} regra(s) salva(s).")
            messagebox.showinfo("Sucesso", f"{len(new_rules)} regra(s) salva(s)!")
        except (json.JSONDecodeError, ValueError) as e:
            messagebox.showerror("Erro", str(e))

    # ──────────────────────────────────────
    # SYSTEM TRAY
    # ──────────────────────────────────────
    def _minimize_to_tray(self):
        if not HAS_TRAY:
            self.iconify()
            return

        self.withdraw()
        png_path = get_resource_path(ICON_PNG_PATH)
        if os.path.exists(png_path):
            image = Image.open(png_path)
        else:
            image = Image.new("RGB", (64, 64), COLORS["accent"])

        menu = pystray.Menu(
            pystray.MenuItem("Abrir", self._restore_from_tray),
            pystray.MenuItem("Sair", self._quit_from_tray),
        )
        self.tray_icon = pystray.Icon("sortify", image, "Sortify", menu)
        self._run_background_task(self.tray_icon.run)

    def _restore_from_tray(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.after(0, self.deiconify)

    def _quit_from_tray(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.after(0, self.on_close)

    # ──────────────────────────────────────
    # ENCERRAMENTO
    # ──────────────────────────────────────
    def on_close(self):
        if self.monitoring:
            self._stop_monitoring()
        if self.scheduler_running:
            self._stop_scheduler()
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()


# ==========================================
# MAIN
# ==========================================
def main():
    set_windows_app_id()
    app = FileOrganizerApp()

    def handle_close():
        if app.config_data.get("minimize_to_tray") and HAS_TRAY:
            app._minimize_to_tray()
        else:
            app.on_close()

    app.protocol("WM_DELETE_WINDOW", handle_close)
    app.mainloop()


if __name__ == "__main__":
    main()
