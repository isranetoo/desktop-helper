# Arquitetura

Esta página resume como o projeto está dividido e como a regra de negócio percorre o código.

## Estrutura Geral

```text
desktop-helper/
├── .github/workflows/docs.yml
├── docs/
├── icons/
├── locale/
├── tests/
├── build.bat
├── config.json
├── core.py
├── i18n.py
├── mkdocs.yml
├── organizador_cli.py
├── organizador_gui.py
├── organizador_gui.spec
├── requirements-dev.txt
├── requirements-optional.txt
└── requirements.txt
```

## Responsabilidade De Cada Módulo

| Arquivo | Papel |
|---|---|
| `core.py` | Núcleo do sistema: configuração, regras, simulação, movimento, undo, duplicados e logs |
| `organizador_gui.py` | Aplicação desktop com páginas, botões, progresso, logs e integração com o core |
| `organizador_cli.py` | Menu em terminal usando a mesma regra central |
| `i18n.py` | Carregamento e fallback de traduções |
| `config.json` | Fonte principal de comportamento do app |
| `tests/` | Garantia de comportamento para o núcleo |
| `mkdocs.yml` + `docs/` | Camada de documentação e publicação |

## Fluxo De Execução

### Organização manual

1. GUI ou CLI escolhe uma pasta.
2. O `core.load_config()` carrega e valida a configuração.
3. `core.organize_folder()` lista os arquivos.
4. Cada item passa por `should_ignore()`.
5. O destino é resolvido com `match_custom_rule()` e `get_destination_folder()`.
6. Se `date_subfolder` estiver ativo, `build_date_subfolder()` complementa o caminho.
7. `move_file()` move o arquivo e gera um registro.
8. `save_undo_history()` empilha a operação.

### Simulação

1. A interface chama `simulate_organization()`.
2. O sistema calcula o destino sem mover nada.
3. A lista de ações planejadas é mostrada ao usuário.

### Duplicados

1. `find_duplicates()` percorre a árvore de forma recursiva.
2. Cada arquivo recebe um hash MD5.
3. Os repetidos vão para `Duplicados/`.
4. A movimentação também entra no histórico de undo.

### Undo

1. `load_undo_stack()` carrega a pilha.
2. `undo_last_organization()` pega a última entrada.
3. Os arquivos voltam em ordem reversa.
4. Pastas vazias sobram? `_cleanup_empty_dirs()` tenta removê-las.

## Arquivos Persistidos

| Arquivo | Função |
|---|---|
| `config.json` | Mantém preferências, categorias, regras e automações |
| `undo_history.json` | Guarda a pilha de desfazer |
| `logs/organizador_YYYY-MM-DD.log` | Registra operações do sistema |

## GUI: Como Está Organizada

Em `organizador_gui.py`, a interface é separada em páginas com métodos dedicados:

- `_create_dashboard_page()`
- `_create_organize_page()`
- `_create_monitor_page()`
- `_create_settings_page()`
- `_create_logs_page()`

Essa divisão ajuda a manter a interface mais legível, mesmo concentrando bastante comportamento no mesmo arquivo.

## CLI: Estrutura Simples E Direta

`organizador_cli.py` é propositalmente simples:

- imprime um menu;
- lê a escolha do usuário;
- chama o mesmo `core.py`;
- exibe progresso e mensagens no terminal.

Essa decisão é boa porque evita duplicação de regra de negócio.

## Internacionalização

`i18n.py` carrega traduções a partir de `locale/` e faz fallback para o idioma padrão.

Hoje isso já permite:

- textos parametrizados;
- nomes de mês localizados;
- evolução futura para mais partes da interface.

## Testes

Os testes atuais focam nas partes mais sensíveis do core:

| Arquivo de teste | O que cobre |
|---|---|
| `test_core_basic.py` | ignore rules, destino por regra e normalização de config |
| `test_core_organize_undo.py` | organização, undo, pilha de histórico e compatibilidade legada |
| `test_core_duplicates.py` | duplicados e exclusão da pasta `Duplicados/` |

## Documentação Como Parte Da Arquitetura

A documentação não é um anexo externo. Ela já faz parte do repositório com:

- tema versionado;
- conteúdo versionado;
- workflow de deploy versionado;
- assets de identidade visual versionados.

Isso é valioso porque reduz a distância entre o código real e a explicação do projeto.

## Pontos Fortes Da Estrutura Atual

- um núcleo de negócio compartilhado entre GUI e CLI;
- testes focados nas partes de maior risco;
- configuração simples em JSON;
- documentação estática fácil de publicar;
- base pronta para automação local contínua.

## Pontos Para Evolução Futura

- dividir ainda mais a GUI em módulos menores;
- expor mais opções do `config.json` diretamente na interface;
- empacotar melhor os assets do app no build final;
- expandir testes para scheduler, monitoramento e i18n.
