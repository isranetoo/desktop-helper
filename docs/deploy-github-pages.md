# Deploy Da Documentação No GitHub Pages

O projeto já está preparado para publicar a documentação automaticamente com GitHub Actions.

## Como Está Montado Hoje

O fluxo usa:

- `mkdocs.yml` para configurar o site;
- `docs/` como fonte de conteúdo;
- `.github/workflows/docs.yml` para build e deploy;
- `mkdocs-material` como tema;
- GitHub Pages como destino final.

## Workflow Atual

O workflow:

1. executa em `push` para `main`;
2. também pode ser iniciado manualmente com `workflow_dispatch`;
3. instala Python `3.11`;
4. instala `mkdocs` e `mkdocs-material`;
5. roda `mkdocs build`;
6. publica a pasta `site` no GitHub Pages.

## Pré-requisitos No GitHub

No repositório remoto:

1. abra `Settings > Pages`;
2. em `Build and deployment`, escolha `GitHub Actions`;
3. confirme que a branch principal usada pelo projeto é `main`;
4. faça push das mudanças.

## Rodar Localmente Antes Do Deploy

### Instalar as dependências de docs

```bash
pip install mkdocs mkdocs-material
```

### Subir em modo desenvolvimento

```bash
mkdocs serve
```

### Gerar build local

```bash
mkdocs build
```

Se o build terminar sem erros, a pasta `site/` estará pronta localmente e o workflow remoto deverá reproduzir esse mesmo processo.

## O Que Conferir Antes De Publicar

- páginas novas estão no `nav` do `mkdocs.yml`;
- links internos funcionam;
- o logo em `docs/assets/sortify.png` está disponível;
- o CSS customizado em `docs/assets/stylesheets/extra.css` foi carregado;
- snippets de código renderizam corretamente;
- a URL em `site_url` aponta para o repositório certo.

## Ajustes Comuns

### O site abre, mas sem estilo novo

Verifique se:

- `extra_css` está apontando para o caminho correto;
- o arquivo CSS foi adicionado em `docs/assets/stylesheets/`;
- o cache do navegador não está mostrando uma versão antiga.

### O logo não aparece

Confirme se o arquivo existe em:

```text
docs/assets/sortify.png
```

E se `mkdocs.yml` contém:

```yaml
theme:
  logo: assets/sortify.png
  favicon: assets/sortify.png
```

### O build falha por módulo ausente

Instale novamente:

```bash
pip install mkdocs mkdocs-material
```

## Estrutura Mínima Esperada

```text
desktop-helper/
├── .github/workflows/docs.yml
├── docs/
│   ├── index.md
│   ├── assets/
│   │   ├── sortify.png
│   │   └── stylesheets/
│   │       └── extra.css
│   └── ...
└── mkdocs.yml
```

## Dica Final

Faça sempre um `mkdocs build` local antes de subir. Isso elimina a maior parte dos erros de navegação, caminho de asset e sintaxe Markdown antes mesmo do CI rodar.
