import os
import time
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# ==========================================
# CONFIGURAÇÕES
# ==========================================
DOWNLOADS_PATH = os.path.join(os.path.expanduser("~"), "Downloads")
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

# Mapeamento de extensões para nomes de pastas
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


# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================
def get_destination_folder(filename: str) -> str:
    """
    Retorna o nome da pasta de destino com base na extensão do arquivo.
    """
    _, ext = os.path.splitext(filename.lower())

    for folder_name, extensions in EXTENSION_MAP.items():
        if ext in extensions:
            return folder_name

    return "Outros"


def ensure_folder_exists(base_path: str, folder_name: str) -> str:
    """
    Garante que a pasta exista e retorna o caminho completo.
    """
    destination_path = os.path.join(base_path, folder_name)
    os.makedirs(destination_path, exist_ok=True)
    return destination_path


def generate_non_conflicting_name(destination_dir: str, filename: str) -> str:
    """
    Se já existir um arquivo com o mesmo nome no destino,
    cria um novo nome automaticamente.
    Exemplo: arquivo.pdf -> arquivo (1).pdf
    """
    base_name, ext = os.path.splitext(filename)
    candidate = filename
    counter = 1

    while os.path.exists(os.path.join(destination_dir, candidate)):
        candidate = f"{base_name} ({counter}){ext}"
        counter += 1

    return candidate


def move_file(file_path: str, base_destination: str) -> None:
    """
    Move um arquivo para a pasta correta com base na extensão.
    """
    if not os.path.isfile(file_path):
        return

    filename = os.path.basename(file_path)

    # Ignora arquivos temporários ou incompletos
    if filename.startswith("~") or filename.endswith(".crdownload") or filename.endswith(".tmp"):
        return

    folder_name = get_destination_folder(filename)
    destination_dir = ensure_folder_exists(base_destination, folder_name)

    safe_filename = generate_non_conflicting_name(destination_dir, filename)
    destination_file = os.path.join(destination_dir, safe_filename)

    try:
        shutil.move(file_path, destination_file)
        print(f"[MOVIDO] {filename} -> {folder_name}")
    except PermissionError:
        print(f"[ERRO] Arquivo em uso: {filename}")
    except Exception as e:
        print(f"[ERRO] Não foi possível mover {filename}: {e}")


def organize_existing_files(folder_path: str) -> None:
    """
    Organiza todos os arquivos já existentes em uma pasta.
    """
    print(f"\nOrganizando arquivos em: {folder_path}\n")

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        # Organiza apenas arquivos, não pastas
        if os.path.isfile(item_path):
            move_file(item_path, folder_path)

    print("Organização concluída.\n")


# ==========================================
# MONITORAMENTO COM WATCHDOG
# ==========================================
class DownloadHandler(FileSystemEventHandler):
    """
    Manipulador de eventos para monitorar novos arquivos em Downloads.
    """

    def on_created(self, event):
        if event.is_directory:
            return

        # Pequena espera para evitar mover arquivo ainda incompleto
        time.sleep(2)
        move_file(event.src_path, DOWNLOADS_PATH)


def start_monitoring_downloads():
    """
    Inicia o monitoramento da pasta Downloads.
    """
    event_handler = DownloadHandler()
    observer = Observer()
    observer.schedule(event_handler, DOWNLOADS_PATH, recursive=False)
    observer.start()

    print(f"Monitorando a pasta: {DOWNLOADS_PATH}")
    print("Pressione CTRL + C para parar.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEncerrando monitoramento...")
        observer.stop()

    observer.join()


# ==========================================
# MENU PRINCIPAL
# ==========================================
def main():
    while True:
        print("=== ORGANIZADOR DE ARQUIVOS ===")
        print("1. Organizar arquivos existentes em Downloads")
        print("2. Monitorar Downloads em tempo real")
        print("3. Limpar/organizar a Área de Trabalho")
        print("4. Sair")

        option = input("Escolha uma opção: ").strip()

        if option == "1":
            organize_existing_files(DOWNLOADS_PATH)

        elif option == "2":
            start_monitoring_downloads()

        elif option == "3":
            organize_existing_files(DESKTOP_PATH)

        elif option == "4":
            print("Saindo do programa...")
            break

        else:
            print("Opção inválida.\n")


if __name__ == "__main__":
    main()