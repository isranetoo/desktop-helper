<p align="center">
    <img src="generated/icons/sortify.png" alt="Capa do Sortify" width="220">
</p>

# Sortify — Organizador de Arquivos

O Sortify é um organizador de arquivos para Windows com interface gráfica moderna e versão em linha de comando. Ele monitora pastas como Downloads, Desktop ou qualquer diretório escolhido pelo usuário, identifica o tipo de cada arquivo e move automaticamente para categorias configuráveis, com suporte a regras personalizadas, detecção de duplicados, agendamento e desfazer.

## Resumo do projeto

Este projeto foi criado para reduzir a bagunça digital do dia a dia. Em vez de mover arquivos manualmente, o Sortify centraliza a organização em um fluxo automatizado: você define categorias, regras e preferências, e a aplicação classifica os arquivos, registra o que foi feito e permite reverter a última operação quando necessário.

## O que ele faz

- Organiza arquivos por extensão ou por estrutura de data.
- Permite criar regras personalizadas com base no nome e no tipo do arquivo.
- Detecta arquivos duplicados por hash e move para uma pasta dedicada.
- Monitora pastas em tempo real com `watchdog`.
- Oferece interface gráfica em `customtkinter` e alternativa via terminal.
- Mantém logs diários e histórico para desfazer organizações.
- Pode exibir notificacoes e rodar minimizado na bandeja do sistema.
- Suporta agendamento diario ou por intervalo de minutos.

## Principais funcionalidades

| Funcionalidade | Descrição |
|---|---|
| Pastas customizáveis | Organize Downloads, Desktop ou qualquer pasta do sistema |
| Categorias editáveis | Defina extensões e destinos no `config.json` ou pela interface |
| Modo simulação | Visualize o que será movido antes de executar |
| Regras personalizadas | Crie regras como `.pdf` + nome contendo `nota` |
| Duplicados | Identifique arquivos repetidos por hash MD5 |
| Organizar por data | Crie subpastas como `PDFs/2026/04-Abril/` |
| Undo | Reverta a última organização com histórico persistente |
| Dashboard | Acompanhe movidos, ignorados, erros e progresso |
| Monitoramento contínuo | Observe várias pastas em tempo real |
| Notificações e tray | Recursos opcionais para uso em segundo plano |
| Build para `.exe` | Gere executável com PyInstaller via `build.bat` |

## Stack e dependências

- Python 3.10+
- `customtkinter` para a interface gráfica
- `watchdog` para monitoramento de arquivos
- `pytest` para testes
- `plyer`, `pystray` e `Pillow` como recursos opcionais

## Instalação

```bash
git clone https://github.com/seu-usuario/desktop-helper.git
cd desktop-helper
pip install -r requirements.txt
```

### Recursos opcionais

Para notificações do sistema e ícone na bandeja:

```bash
pip install -r requirements-optional.txt
```

### Dependências de desenvolvimento

```bash
pip install -r requirements-dev.txt
```

## Como executar

### Interface gráfica

```bash
python organizador_gui.py
```

### Linha de comando

```bash
python organizador_cli.py
```

## Como configurar

O comportamento da aplicação fica em `config.json`. Você pode editar esse arquivo manualmente ou usar os botões de configuração na interface.

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
|---|---|---|
| `extension` | string ou lista | `".pdf"` ou `[".pdf", ".xml"]` |
| `name_contains` | string | `"nota"` |
| `name_starts_with` | string | `"IMG_"` |

## Estrutura do projeto

```text
desktop-helper/
├── config.json                 # Categorias, regras e preferências da aplicação
├── core.py                     # Lógica principal de organização, undo e duplicados
├── organizador_gui.py          # Aplicacao desktop com customtkinter
├── organizador_cli.py          # Interface de linha de comando
├── i18n.py                     # Suporte a tradução
├── locale/                     # Arquivos de idioma
├── generated/icons/            # Ícones e imagem usada na capa do projeto
├── tests/                      # Suíte de testes automatizados
├── requirements.txt            # Dependências base
├── requirements-optional.txt   # Notificações e system tray
├── requirements-dev.txt        # Ferramentas de teste
├── build.bat                   # Build do executável no Windows
└── organizador_gui.spec        # Configuração do PyInstaller
```

## Testes

```bash
pytest
```

## Gerar executável

No Windows:

```bash
build.bat
```

O executável será gerado em `dist/`.

## Release checklist

1. Rodar `pytest`.
2. Validar a GUI com `python organizador_gui.py`.
3. Validar os recursos opcionais, se usados.
4. Atualizar `CHANGELOG.md`.

## Licenca

Projeto licenciado sob MIT. Veja `LICENSE` para mais detalhes.

## Documentação com MkDocs

Este repositório agora inclui documentação em `docs/` com configuração em `mkdocs.yml` e deploy automático para GitHub Pages em `.github/workflows/docs.yml`.

### Rodar localmente

```bash
pip install mkdocs mkdocs-material
mkdocs serve
```
