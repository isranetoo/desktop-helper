<p align="center">
    <img src="generated/icons/sortify.png" alt="Capa do Sortify" width="220">
</p>

# Sortify — Organizador de Arquivos

O Sortify e um organizador de arquivos para Windows com interface grafica moderna e versao em linha de comando. Ele monitora pastas como Downloads, Desktop ou qualquer diretorio escolhido pelo usuario, identifica o tipo de cada arquivo e move automaticamente para categorias configuraveis, com suporte a regras personalizadas, deteccao de duplicados, agendamento e desfazer.

## Resumo do projeto

Este projeto foi criado para reduzir a bagunca digital do dia a dia. Em vez de mover arquivos manualmente, o Sortify centraliza a organizacao em um fluxo automatizado: voce define categorias, regras e preferencias, e a aplicacao classifica os arquivos, registra o que foi feito e permite reverter a ultima operacao quando necessario.

## O que ele faz

- Organiza arquivos por extensao ou por estrutura de data.
- Permite criar regras personalizadas com base no nome e no tipo do arquivo.
- Detecta arquivos duplicados por hash e move para uma pasta dedicada.
- Monitora pastas em tempo real com `watchdog`.
- Oferece interface grafica em `customtkinter` e alternativa via terminal.
- Mantem logs diarios e historico para desfazer organizacoes.
- Pode exibir notificacoes e rodar minimizado na bandeja do sistema.
- Suporta agendamento diario ou por intervalo de minutos.

## Principais funcionalidades

| Funcionalidade | Descricao |
|---|---|
| Pastas customizaveis | Organize Downloads, Desktop ou qualquer pasta do sistema |
| Categorias editaveis | Defina extensoes e destinos no `config.json` ou pela interface |
| Modo simulacao | Visualize o que sera movido antes de executar |
| Regras personalizadas | Crie regras como `.pdf` + nome contendo `nota` |
| Duplicados | Identifique arquivos repetidos por hash MD5 |
| Organizar por data | Crie subpastas como `PDFs/2026/04-Abril/` |
| Undo | Reverta a ultima organizacao com historico persistente |
| Dashboard | Acompanhe movidos, ignorados, erros e progresso |
| Monitoramento continuo | Observe varias pastas em tempo real |
| Notificacoes e tray | Recursos opcionais para uso em segundo plano |
| Build para `.exe` | Gere executavel com PyInstaller via `build.bat` |

## Stack e dependencias

- Python 3.10+
- `customtkinter` para a interface grafica
- `watchdog` para monitoramento de arquivos
- `pytest` para testes
- `plyer`, `pystray` e `Pillow` como recursos opcionais

## Instalacao

```bash
git clone https://github.com/seu-usuario/desktop-helper.git
cd desktop-helper
pip install -r requirements.txt
```

### Recursos opcionais

Para notificacoes do sistema e icone na bandeja:

```bash
pip install -r requirements-optional.txt
```

### Dependencias de desenvolvimento

```bash
pip install -r requirements-dev.txt
```

## Como executar

### Interface grafica

```bash
python organizador_gui.py
```

### Linha de comando

```bash
python organizador_cli.py
```

## Como configurar

O comportamento da aplicacao fica em `config.json`. Voce pode editar esse arquivo manualmente ou usar os botoes de configuracao na interface.

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

### Condicoes disponiveis

| Condicao | Tipo | Exemplo |
|---|---|---|
| `extension` | string ou lista | `".pdf"` ou `[".pdf", ".xml"]` |
| `name_contains` | string | `"nota"` |
| `name_starts_with` | string | `"IMG_"` |

## Estrutura do projeto

```text
desktop-helper/
├── config.json                 # Categorias, regras e preferencias da aplicacao
├── core.py                     # Logica principal de organizacao, undo e duplicados
├── organizador_gui.py          # Aplicacao desktop com customtkinter
├── organizador_cli.py          # Interface de linha de comando
├── i18n.py                     # Suporte a traducao
├── locale/                     # Arquivos de idioma
├── generated/icons/            # Icones e imagem usada na capa do projeto
├── tests/                      # Suite de testes automatizados
├── requirements.txt            # Dependencias base
├── requirements-optional.txt   # Notificacoes e system tray
├── requirements-dev.txt        # Ferramentas de teste
├── build.bat                   # Build do executavel no Windows
└── organizador_gui.spec        # Configuracao do PyInstaller
```

## Testes

```bash
pytest
```

## Gerar executavel

No Windows:

```bash
build.bat
```

O executavel sera gerado em `dist/`.

## Release checklist

1. Rodar `pytest`.
2. Validar a GUI com `python organizador_gui.py`.
3. Validar os recursos opcionais, se usados.
4. Atualizar `CHANGELOG.md`.

## Licenca

Projeto licenciado sob MIT. Veja `LICENSE` para mais detalhes.
