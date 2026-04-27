# Deploy com MkDocs no GitHub Pages

Este projeto está preparado para publicar documentação automaticamente usando GitHub Actions.

## 1) Dependências da documentação

Instale localmente:

```bash
pip install mkdocs mkdocs-material
```

## 2) Visualizar localmente

```bash
mkdocs serve
```

Acesse `http://127.0.0.1:8000`.

## 3) Build local

```bash
mkdocs build
```

## 4) Publicação automática no GitHub Pages

O workflow `.github/workflows/docs.yml` publica a documentação na branch/configuração de Pages do repositório.

### Configuração no GitHub

1. Vá em **Settings > Pages**;
2. Em **Build and deployment**, escolha **GitHub Actions**;
3. Faça push para a branch principal.

Pronto: o deploy será executado automaticamente.
