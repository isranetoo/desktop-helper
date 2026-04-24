# desktop-helper

App desktop em `tkinter` para organizar arquivos com interface moderna.

## Novidades

- Seleção manual de pasta para organizar (`filedialog`).
- Categorias e regras customizáveis via `config.json`.
- Modo simulação (dry-run) antes de mover arquivos.
- Histórico da última execução com botão de desfazer.
- Logs de auditoria em `logs/organizador_YYYY-MM-DD.log`.
- Ignorar nomes/extensões sensíveis (ex: `desktop.ini`).
- Organização por extensão, data ou combinado.
- Detecção simples de duplicados por hash (`SHA-256`).
- Barra de progresso e cards de indicadores (movidos/ignorados/erros).
- Monitoramento de múltiplas pastas.

## Como executar

```bash
pip install watchdog
python organizador_gui.py
```

## Configuração

Edite o arquivo `config.json` para personalizar:

- categorias por extensão;
- extensões/nomes ignorados;
- regras por nome + extensão;
- pasta de duplicados.

## Executável Windows

```bash
pip install pyinstaller
pyinstaller --onefile --windowed organizador_gui.py
```
