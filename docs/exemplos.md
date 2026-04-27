# Exemplos

Esta página junta cenários práticos para você adaptar rapidamente ao seu uso real.

## Exemplo 1: Pasta De Downloads Pessoal

### Configuração

```json
{
  "categories": {
    "Imagens": [".jpg", ".jpeg", ".png", ".webp"],
    "PDFs": [".pdf"],
    "Documentos": [".docx", ".txt", ".md"],
    "Compactados": [".zip", ".rar", ".7z"],
    "Executaveis": [".exe", ".msi"]
  },
  "ignored_extensions": [".lnk", ".ini", ".url"],
  "ignored_names": ["desktop.ini", "Thumbs.db"],
  "custom_rules": []
}
```

### Antes

```text
Downloads/
├── ebook.pdf
├── wallpaper.png
├── setup.exe
├── backup.zip
└── lembretes.txt
```

### Depois

```text
Downloads/
├── PDFs/
│   └── ebook.pdf
├── Imagens/
│   └── wallpaper.png
├── Executaveis/
│   └── setup.exe
├── Compactados/
│   └── backup.zip
└── Documentos/
    └── lembretes.txt
```

## Exemplo 2: Documentos Fiscais

### Regra personalizada

```json
{
  "name": "Notas Fiscais",
  "destination": "Notas Fiscais",
  "conditions": {
    "extension": ".pdf",
    "name_contains": "nota"
  }
}
```

### Resultado esperado

- `nota_abril.pdf` vai para `Notas Fiscais/`
- `contrato.pdf` continua em `PDFs/`

Esse padrão é útil quando a extensão sozinha não separa bem o tipo de documento.

## Exemplo 3: Screenshots E Capturas

```json
{
  "name": "Screenshots",
  "destination": "Screenshots",
  "conditions": {
    "extension": ".png",
    "name_contains": "screenshot"
  }
}
```

Ideal para separar prints de tela das outras imagens do sistema.

## Exemplo 4: Organização Por Data

Com `date_subfolder: true`, o destino ganha estrutura temporal.

### Antes

```text
Downloads/
└── relatorio.pdf
```

### Depois

```text
Downloads/
└── PDFs/
    └── 2026/
        └── Abril/
            └── relatorio.pdf
```

Esse modo é muito útil quando você quer manter histórico cronológico sem depender do nome do arquivo.

## Exemplo 5: Duplicados

### Entrada

```text
workspace/
├── a.txt
├── b.txt
└── c.txt
```

Se `a.txt` e `b.txt` tiverem o mesmo conteúdo:

### Saída

```text
workspace/
├── a.txt
├── c.txt
└── Duplicados/
    └── b.txt
```

## Exemplo 6: Undo Em Ação

### Após organizar

```text
Downloads/
├── PDFs/
│   └── contrato.pdf
└── Imagens/
    └── foto.jpg
```

### Após desfazer

```text
Downloads/
├── contrato.pdf
└── foto.jpg
```

O histórico salvo permite recuperar a última operação feita.

## Exemplo 7: Configuração Para Dev

```json
{
  "categories": {
    "Codigos": [".py", ".js", ".ts", ".tsx", ".sql", ".sh"],
    "Documentos": [".md", ".txt"],
    "Compactados": [".zip", ".tar", ".gz"],
    "ISOs": [".iso"]
  },
  "custom_rules": [
    {
      "name": "Specs",
      "destination": "Especificacoes",
      "conditions": {
        "extension": ".pdf",
        "name_contains": "spec"
      }
    }
  ]
}
```

Bom para separar rapidamente código, documentação técnica e pacotes baixados.

## Exemplo 8: Logs Esperados

Durante uma sessão, mensagens como estas fazem sentido:

```text
[14:02:10] 📁 Organizando: C:\Users\SeuUsuario\Downloads
[14:02:11] ✅ contrato.pdf → PDFs/
[14:02:11] ✅ imagem.png → Imagens/
[14:02:12] ✨ Concluído: 2 movidos, 0 ignorados, 0 erros.
```

Se algo der errado, você verá mensagens de aviso ou erro diretamente na GUI e no arquivo diário de log.

## Exemplo 9: Rotina Gradual

Se você está implantando o Sortify em uma máquina que já está bagunçada:

1. organize uma pasta de teste;
2. valide undo;
3. rode a busca de duplicados;
4. só então passe para `Downloads`;
5. depois habilite monitoramento;
6. por último, ligue agendamento.

Essa sequência reduz risco e ajuda a ajustar as regras com calma.
