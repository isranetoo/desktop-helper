# Empacotamento Multiplataforma e Releases

Esta página concentra o fluxo para gerar artefatos para Windows, macOS e Linux, além de publicar releases no GitHub com os botões da landing apontando para os downloads corretos.

## Scripts de build

O projeto agora possui um script unificado em Python e atalhos por plataforma:

- `scripts/build.py`: detecta o SO (ou usa `--target`) e chama a ferramenta correta.
- `build.bat`: atalho para Windows (`python scripts\\build.py --target windows`).
- `scripts/build_macos.sh`: atalho para macOS (`python scripts/build.py --target macos`).
- `scripts/build_linux.sh`: atalho para Linux (`python scripts/build.py --target linux`).

## Ferramentas usadas por plataforma

| Plataforma | Ferramenta | Saída esperada |
|---|---|---|
| Windows | `PyInstaller` | `dist/sortify-windows.exe` |
| macOS | `py2app` | `dist/Sortify-macos.app` (compactar para `Sortify-macos.zip`) |
| Linux | `PyInstaller` + `appimagetool` | `dist/sortify-linux.AppImage` |

> Se `appimagetool` não estiver instalado no Linux, o script gera ao menos `dist/sortify-linux` e mostra aviso.

## Comandos rápidos

### Build automático pelo SO atual

```bash
python scripts/build.py
```

### Build explícito por alvo

```bash
python scripts/build.py --target windows
python scripts/build.py --target macos
python scripts/build.py --target linux
```

## Convenção de nomes dos assets

A landing web foi configurada para baixar assets com os nomes abaixo no **latest release**:

- `sortify-windows.exe`
- `Sortify-macos.zip`
- `sortify-linux.AppImage`

Se você alterar esses nomes no release, atualize também `web/landing/src/App.jsx`.

## Como configurar Releases no GitHub

## 1) Criar tag de versão

```bash
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```

## 2) Criar o release

1. Abra **GitHub > Releases > Draft a new release**.
2. Selecione a tag (`v1.2.0`).
3. Título: `v1.2.0`.
4. Descrição: inclua changelog resumido.
5. Faça upload dos assets com os nomes padronizados.
6. Publique o release.

## 3) Validar links da landing

Após publicar, teste:

- `https://github.com/isranetoo/desktop-helper/releases/latest/download/sortify-windows.exe`
- `https://github.com/isranetoo/desktop-helper/releases/latest/download/Sortify-macos.zip`
- `https://github.com/isranetoo/desktop-helper/releases/latest/download/sortify-linux.AppImage`

Se abrir download, os botões da landing estão corretos.

## Sugestão (opcional): automação com GitHub Actions

Você pode criar workflow de release para:

- build em matriz (`windows-latest`, `macos-latest`, `ubuntu-latest`);
- upload automático dos artefatos;
- publicação automática ao criar tag `v*`.

Isso reduz trabalho manual e evita divergência de nomes dos arquivos.
