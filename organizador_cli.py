"""
organizador_cli.py — Versão de linha de comando do organizador.
Usa o mesmo core.py da versão GUI.
"""

import os
import sys
import core


def print_menu():
    print("\n=== ORGANIZADOR DE ARQUIVOS ===")
    print("1. Organizar Downloads")
    print("2. Organizar Desktop")
    print("3. Organizar outra pasta")
    print("4. Simular organização")
    print("5. Desfazer última organização")
    print("6. Buscar duplicados")
    print("7. Monitorar Downloads em tempo real")
    print("8. Sair")


def cli_logger(msg: str):
    print(f"  {msg}")


def cli_progress(current: int, total: int):
    bar_len = 30
    filled = int(bar_len * current / total) if total else 0
    bar = "█" * filled + "░" * (bar_len - filled)
    pct = int(100 * current / total) if total else 0
    print(f"\r  [{bar}] {pct}% ({current}/{total})", end="", flush=True)
    if current == total:
        print()


def main():
    config = core.load_config()

    while True:
        print_menu()
        option = input("\nEscolha: ").strip()

        if option == "1":
            core.organize_folder(core.DOWNLOADS_PATH, config, cli_logger, cli_progress)

        elif option == "2":
            core.organize_folder(core.DESKTOP_PATH, config, cli_logger, cli_progress)

        elif option == "3":
            path = input("Caminho da pasta: ").strip()
            if os.path.isdir(path):
                core.organize_folder(path, config, cli_logger, cli_progress)
            else:
                print("Pasta não encontrada.")

        elif option == "4":
            path = input("Caminho da pasta para simular: ").strip()
            if os.path.isdir(path):
                actions = core.simulate_organization(path, config, cli_logger)
                if actions:
                    resp = input(f"\n{len(actions)} arquivo(s). Executar? (s/n): ").strip().lower()
                    if resp == "s":
                        core.organize_folder(path, config, cli_logger, cli_progress)

        elif option == "5":
            core.undo_last_organization(cli_logger, cli_progress)

        elif option == "6":
            path = input("Caminho da pasta: ").strip()
            if os.path.isdir(path):
                core.find_duplicates(path, config, cli_logger, cli_progress)

        elif option == "7":
            import time
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class CLIHandler(FileSystemEventHandler):
                def on_created(self, event):
                    if event.is_directory:
                        return
                    time.sleep(2)
                    core.move_file(event.src_path, core.DOWNLOADS_PATH, config, cli_logger, notify=True)

            obs = Observer()
            obs.schedule(CLIHandler(), core.DOWNLOADS_PATH, recursive=False)
            obs.start()
            print(f"\nMonitorando: {core.DOWNLOADS_PATH}")
            print("CTRL+C para parar.\n")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                obs.stop()
            obs.join()

        elif option == "8":
            print("Saindo...")
            break

        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
