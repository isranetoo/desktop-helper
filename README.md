# Desktop Helper — Organizador de Arquivos

Ferramenta para organizar automaticamente arquivos de Downloads, Desktop e qualquer outra pasta do seu computador.

## Funcionalidades

| #  | Funcionalidade | Descrição |
|----|---------------|-----------|
| 1  | Selecionar pastas | Organize qualquer pasta do sistema, não apenas Downloads e Desktop |
| 2  | Categorias editáveis | As extensões e pastas de destino são configuráveis via `config.json` ou pelo editor visual |
| 3  | Modo simulação | Veja o que seria feito antes de mover qualquer arquivo |
| 4  | Log em arquivo | Todas as ações ficam registradas em `logs/organizador_YYYY-MM-DD.log` |
| 5  | Desfazer | Reverta a última organização com um clique |
| 6  | Ignorar arquivos | `desktop.ini`, `.lnk`, `.tmp` e outros são ignorados automaticamente |
| 7  | Organizar por data | Opcionalmente cria sub-pastas por ano/mês (ex: `PDFs/2026/04-Abril/`) |
| 8  | Detectar duplicados | Encontra arquivos duplicados por hash MD5 e move para `Duplicados/` |
| 9  | Barra de progresso | Acompanhe o progresso em tempo real |
| 10 | Dashboard | Contadores de arquivos movidos, ignorados e erros na sessão |
| 11 | Minimizar para bandeja | Roda em segundo plano no system tray (requer `pystray` e `Pillow`) |
| 12 | Executável `.exe` | Script `build.bat` incluso para gerar o executável via PyInstaller |
| 13 | Ícone do aplicativo | Ícone customizado na janela, barra de tarefas e executável (gerado automaticamente em `generated/icons/`) |
| 14 | Notificações | Alertas do sistema quando um arquivo é organizado (requer `plyer`) |
| 15 | Monitorar várias pastas | Adicione quantas pastas quiser ao monitoramento simultâneo |
| 16 | Regras personalizadas | Regras tipo: se é `.pdf` e contém "nota" no nome → `Notas Fiscais/` |
| 17 | Agendamento automático | Programe organização diária (HH:MM) ou por intervalo em minutos |

## Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/desktop-helper.git
cd desktop-helper

# Instale as dependências
pip install -r requirements.txt

# (Opcional) Recursos de notificação e bandeja
pip install -r requirements-optional.txt

# Execute
python organizador_gui.py
```

### Dependências obrigatórias

- `watchdog` — monitoramento de pastas

### Dependências opcionais (recursos extras)

- `plyer` — notificações do sistema
- `pystray` + `Pillow` — minimizar para bandeja do sistema

### Dependências de desenvolvimento

- `pytest` — suíte de testes automatizados (`requirements-dev.txt`)

## Testes

```bash
pip install -r requirements-dev.txt
pytest
```

## Release checklist (resumo)

1. Rodar testes automatizados (`pytest`).
2. Validar execução da GUI (`python organizador_gui.py`).
3. Validar dependências opcionais quando usar notificações/tray (`requirements-optional.txt`).
4. Atualizar `CHANGELOG.md` com o que entrou na versão.

## Gerar executável (.exe)

```bash
# No Windows, basta rodar:
build.bat
```

O executável será criado em `dist/Organizador de Arquivos.exe`.

## Estrutura do projeto

```
desktop-helper/
├── config.json            # Configuração de categorias, regras e preferências
├── core.py                # Lógica de negócio (mover, desfazer, duplicados, etc.)
├── organizador_gui.py     # Interface gráfica (tkinter)
├── requirements.txt       # Dependências Python
├── build.bat              # Script para gerar .exe
├── logs/                  # Logs diários (criado automaticamente)
└── undo_history.json      # Histórico para desfazer (criado automaticamente)
```

## Configuração

Edite `config.json` diretamente ou use os botões **⚙ Categorias** e **📏 Regras** na interface.

### Exemplo de regra personalizada

```json
{
    "name": "Notas Fiscais",
    "conditions": {
        "extension": ".pdf",
        "name_contains": "nota"
    },
    "destination": "Notas Fiscais"
}
```

### Condições disponíveis

| Condição | Tipo | Exemplo |
|----------|------|---------|
| `extension` | string ou lista | `".pdf"` ou `[".pdf", ".xml"]` |
| `name_contains` | string | `"nota"` |
| `name_starts_with` | string | `"IMG_"` |

## Licença

MIT License — veja [LICENSE](LICENSE) para detalhes.
