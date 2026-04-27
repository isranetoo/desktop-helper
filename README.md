<p align="center">
  <img src="icons/sortify.png" alt="Logo do Sortify" width="220">
</p>

<h1 align="center">Sortify</h1>

<p align="center">
  Organizador de arquivos para Windows com GUI moderna, CLI, monitoramento em tempo real,
  regras personalizadas, undo persistente, detecção de duplicados e documentação web com MkDocs.
</p>

## Visão Geral

O `Sortify` foi pensado para resolver um problema bem cotidiano: pastas como `Downloads` e `Desktop` viram um depósito de arquivos misturados muito rápido. Em vez de depender de organização manual, a aplicação transforma esse processo em um fluxo configurável e repetível.

O projeto reúne duas portas de entrada:

- uma interface gráfica com `customtkinter`, focada em usabilidade e operação diária;
- uma interface de linha de comando, útil para quem prefere terminal ou quer validar fluxos rapidamente.

Por baixo dessa camada visual, existe um `core.py` com a regra de negócio central: normalização de configuração, roteamento por categoria, regras customizadas, organização em lote, simulação, pilha de undo, logs e busca de duplicados.

## O Que O Projeto Entrega

| Recurso | Como funciona na prática |
|---|---|
| Organização por categoria | Move arquivos conforme a extensão para pastas como `PDFs`, `Imagens`, `Vídeos` e outras |
| Regras personalizadas | Permite priorizar condições como extensão, nome contendo trecho e prefixo do arquivo |
| Simulação | Mostra o que seria movido antes da execução real |
| Organização por data | Pode criar subpastas como `PDFs/2026/Abril/` com base na data de modificação |
| Duplicados | Calcula hash MD5 e move cópias para `Duplicados/` |
| Undo persistente | Guarda o histórico das últimas operações e desfaz a mais recente |
| Monitoramento | Usa `watchdog` para reagir quando novos arquivos entram em pastas monitoradas |
| Agendamento | Executa automaticamente por horário fixo ou intervalo de minutos |
| Logs | Mantém registros em `logs/organizador_YYYY-MM-DD.log` |
| Internacionalização | Estrutura preparada com `locale/` e utilitário `i18n.py` |
| Recursos opcionais | Notificações do sistema e minimização para a bandeja |

## Fluxo Mental Do Sortify

1. Você define categorias e regras.
2. O arquivo entra em uma pasta monitorada ou é processado manualmente.
3. O `core.py` verifica se ele deve ser ignorado.
4. O sistema testa regras personalizadas antes das categorias por extensão.
5. O arquivo é movido para a pasta destino com nome seguro.
6. A ação é salva no histórico para permitir undo.
7. Logs e contadores atualizam o estado da execução.

## Instalação

```bash
git clone https://github.com/isranetoo/desktop-helper.git
cd desktop-helper
pip install -r requirements.txt
```

### Recursos opcionais

Instale também os extras se quiser notificações do sistema e bandeja:

```bash
pip install -r requirements-optional.txt
```

### Dependências de desenvolvimento

```bash
pip install -r requirements-dev.txt
```

## Como Executar

### Interface gráfica

```bash
python organizador_gui.py
```

A GUI traz cinco áreas principais:

- `Dashboard`: visão geral da sessão, progresso e atalhos rápidos;
- `Organizar`: execução manual, simulação, busca de duplicados e undo;
- `Monitorar`: monitoramento de múltiplas pastas e agendamento;
- `Configurações`: edição de categorias e regras em JSON;
- `Logs`: trilha de execução e diagnóstico.

### Interface de linha de comando

```bash
python organizador_cli.py
```

A CLI oferece um menu com ações rápidas para:

- organizar `Downloads`;
- organizar `Desktop`;
- escolher outra pasta;
- simular antes de mover;
- desfazer a última organização;
- encontrar duplicados;
- monitorar `Downloads` em tempo real.

## Configuração

O comportamento do projeto é controlado por `config.json`. A aplicação carrega esse arquivo, valida a estrutura e normaliza vários tipos de entrada automaticamente.

### Exemplo realista

```json
{
  "categories": {
    "Imagens": [".jpg", ".jpeg", ".png", ".webp"],
    "PDFs": [".pdf"],
    "Documentos": [".docx", ".txt", ".md"],
    "Codigos": [".py", ".js", ".ts", ".sql"]
  },
  "ignored_extensions": [".lnk", ".ini", ".url"],
  "ignored_names": ["desktop.ini", "Thumbs.db", ".DS_Store"],
  "custom_rules": [
    {
      "name": "Notas Fiscais",
      "conditions": {
        "extension": ".pdf",
        "name_contains": "nota"
      },
      "destination": "Notas Fiscais"
    }
  ],
  "monitored_folders": [],
  "organize_mode": "extension",
  "date_subfolder": true,
  "notifications_enabled": true,
  "minimize_to_tray": false,
  "scheduled_enabled": false,
  "scheduled_mode": "daily",
  "scheduled_time": "18:00",
  "scheduled_interval_minutes": 60,
  "language": "pt"
}
```

### Condições aceitas em regras personalizadas

| Chave | Tipo | Exemplo | Observação |
|---|---|---|---|
| `extension` | string ou lista | `".pdf"` ou `[".pdf", ".xml"]` | É normalizada para minúsculas com ponto |
| `name_contains` | string | `"nota"` | Busca trecho no nome do arquivo |
| `name_starts_with` | string | `"IMG_"` | Útil para padrões previsíveis |

### Observações importantes

- Regras personalizadas têm prioridade sobre categorias por extensão.
- `date_subfolder` é o campo que realmente ativa a organização em subpastas por data.
- `organize_mode` existe na configuração e é validado, mas a versão atual opera com organização por categoria e data opcional.
- `minimize_to_tray` depende das dependências opcionais instaladas.

## Exemplo Prático

Se a pasta `Downloads` contiver:

```text
Downloads/
├── nota_abril.pdf
├── screenshot_home.png
├── roteiro.md
└── instalador.exe
```

Com categorias e regras padrão, um resultado possível é:

```text
Downloads/
├── Notas Fiscais/
│   └── 2026/
│       └── Abril/
│           └── nota_abril.pdf
├── Imagens/
│   └── 2026/
│       └── Abril/
│           └── screenshot_home.png
├── Documentos/
│   └── 2026/
│       └── Abril/
│           └── roteiro.md
└── Executaveis/
    └── 2026/
        └── Abril/
            └── instalador.exe
```

## Estrutura Do Projeto

```text
desktop-helper/
├── .github/workflows/docs.yml      # Deploy automático da documentação
├── docs/                           # Páginas do MkDocs
├── icons/                          # Identidade visual do projeto
├── locale/                         # Traduções JSON
├── logs/                           # Logs gerados em tempo de execução
├── tests/                          # Testes automatizados do core
├── CHANGELOG.md                    # Histórico de mudanças
├── LICENSE                         # Licença MIT
├── README.md                       # Visão geral do repositório
├── build.bat                       # Build Windows com PyInstaller
├── config.json                     # Configuração principal
├── core.py                         # Regra de negócio central
├── i18n.py                         # Carregamento de traduções
├── mkdocs.yml                      # Configuração do site de documentação
├── organizador_cli.py              # Entrada em linha de comando
├── organizador_gui.py              # Aplicação desktop com customtkinter
├── organizador_gui.spec            # Arquivo base do PyInstaller
├── requirements-dev.txt            # Ferramentas de desenvolvimento
├── requirements-optional.txt       # Notificações, tray e Pillow
└── requirements.txt                # Dependências base
```

## Documentação Web

O projeto inclui uma documentação expandida em `docs/`, com tema `Material for MkDocs`, navegação por seções e deploy automatizado no GitHub Pages.

### Rodar localmente

```bash
pip install mkdocs mkdocs-material
mkdocs serve
```

### Build local

```bash
mkdocs build
```

## Testes

```bash
pytest
```

Os testes atuais cobrem principalmente:

- ignorar arquivos temporários e nomes especiais;
- roteamento por regras personalizadas;
- validação e normalização de configuração;
- organização com undo;
- pilha de múltiplas operações de desfazer;
- busca de duplicados.

## Build Do Executável

No Windows:

```bash
build.bat
```

O processo gera a aplicação em `dist/`.

Observação: a aplicação usa `icons/sortify.png` e `icons/sortify.ico` em tempo de desenvolvimento. Se você quiser garantir esses assets dentro do executável final, vale revisar o empacotamento no `PyInstaller` para incluir a pasta `icons/`.

## Stack

- Python 3.10+
- `customtkinter`
- `watchdog`
- `pytest`
- `plyer`
- `pystray`
- `Pillow`
- `mkdocs`
- `mkdocs-material`

## Release Checklist

1. Rodar `pytest`.
2. Validar a GUI com `python organizador_gui.py`.
3. Validar monitoramento, simulação, undo e duplicados.
4. Revisar `config.json` e `CHANGELOG.md`.
5. Gerar o build da documentação com `mkdocs build`.

## Licença

Projeto licenciado sob MIT. Veja `LICENSE` para os detalhes.
