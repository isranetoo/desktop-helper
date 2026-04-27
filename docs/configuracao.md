# Configuração

O coração do comportamento do Sortify está em `config.json`. A aplicação lê esse arquivo ao iniciar, valida a estrutura e normaliza vários dados automaticamente para evitar inconsistências simples.

## Exemplo Completo

```json
{
  "categories": {
    "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"],
    "PDFs": [".pdf"],
    "Documentos": [".doc", ".docx", ".txt", ".odt", ".rtf", ".md"],
    "Planilhas": [".xls", ".xlsx", ".csv"],
    "Apresentacoes": [".ppt", ".pptx"],
    "Compactados": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Executaveis": [".exe", ".msi"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "Audios": [".mp3", ".wav", ".flac"],
    "Codigos": [".py", ".js", ".ts", ".tsx", ".html", ".css", ".sql"]
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
  "monitored_folders": [
    "C:\\Users\\SeuUsuario\\Downloads",
    "C:\\Users\\SeuUsuario\\Desktop"
  ],
  "organize_mode": "extension",
  "date_subfolder": true,
  "notifications_enabled": true,
  "minimize_to_tray": false,
  "scheduled_enabled": true,
  "scheduled_mode": "daily",
  "scheduled_time": "18:00",
  "scheduled_interval_minutes": 60,
  "language": "pt"
}
```

## Como A Validação Funciona

O módulo `core.py` valida a configuração antes de usar ou salvar. Isso traz alguns comportamentos úteis:

- extensões são convertidas para minúsculas;
- extensões sem ponto recebem `.` automaticamente;
- listas inválidas são descartadas;
- regras sem condições válidas são ignoradas;
- horários inválidos de agendamento não são aceitos;
- o arquivo pode cair para o padrão se o JSON estiver corrompido.

## Campos Principais

| Chave | Tipo | O que faz |
|---|---|---|
| `categories` | objeto | Define o mapeamento entre nome da pasta e extensões |
| `ignored_extensions` | lista | Ignora extensões técnicas ou temporárias |
| `ignored_names` | lista | Ignora nomes específicos como `desktop.ini` |
| `custom_rules` | lista | Cria regras com prioridade maior que categorias |
| `monitored_folders` | lista | Lista de pastas usadas pelo monitoramento |
| `organize_mode` | string | Campo validado na configuração; hoje o fluxo prático é orientado por categorias e data opcional |
| `date_subfolder` | booleano | Cria subpastas por ano e mês |
| `notifications_enabled` | booleano | Ativa notificações quando o suporte opcional está instalado |
| `minimize_to_tray` | booleano | Minimiza para a bandeja ao fechar, se `pystray` estiver disponível |
| `scheduled_enabled` | booleano | Liga ou desliga a execução agendada |
| `scheduled_mode` | string | Define `daily` ou `interval` |
| `scheduled_time` | string | Horário `HH:MM` em modo diário |
| `scheduled_interval_minutes` | inteiro | Intervalo de minutos em modo intervalo |
| `language` | string | Idioma do sistema de traduções |

## Categorias

`categories` é um dicionário em que:

- a chave é o nome da pasta destino;
- o valor é a lista de extensões que vão para essa pasta.

Exemplo:

```json
{
  "Imagens": [".jpg", ".jpeg", ".png"],
  "Documentos": [".docx", ".txt", ".md"],
  "Codigos": [".py", ".js", ".ts"]
}
```

### Regras úteis para categorias

- use nomes de pastas claros e estáveis;
- agrupe extensões que você realmente quer manter juntas;
- evite duplicar a mesma extensão em várias categorias;
- lembre que regras customizadas podem sobrescrever esse destino.

## Arquivos Ignorados

O Sortify ignora arquivos especiais por nome, extensão e alguns padrões temporários.

### Ignorados por padrão

- nomes como `desktop.ini`, `Thumbs.db` e `.DS_Store`;
- extensões como `.lnk`, `.ini` e `.url`;
- arquivos temporários terminados com `.crdownload`, `.tmp`, `.part` e `.download`;
- arquivos iniciados com `~`.

Isso evita que o app mova atalhos, arquivos de sistema ou downloads incompletos.

## Regras Personalizadas

As regras em `custom_rules` são avaliadas antes do agrupamento por categoria. Cada regra precisa de:

- `name`: nome da regra;
- `destination`: pasta de destino;
- `conditions`: conjunto de condições.

### Condições suportadas

| Condição | Tipo | Exemplo |
|---|---|---|
| `extension` | string ou lista | `".pdf"` ou `[".pdf", ".xml"]` |
| `name_contains` | string | `"nota"` |
| `name_starts_with` | string | `"IMG_"` |

### Exemplo 1: documentos fiscais

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

### Exemplo 2: screenshots

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

### Exemplo 3: capturas do celular

```json
{
  "name": "Fotos do Celular",
  "destination": "Fotos do Celular",
  "conditions": {
    "extension": [".jpg", ".jpeg"],
    "name_starts_with": "IMG_"
  }
}
```

!!! warning "Prioridade importa"
    Se uma regra personalizada bater, o arquivo não passa mais pela verificação normal de categorias.

## Monitoramento

`monitored_folders` guarda a lista das pastas que a GUI observa com `watchdog`.

Exemplo:

```json
{
  "monitored_folders": [
    "C:\\Users\\SeuUsuario\\Downloads",
    "D:\\Inbox"
  ]
}
```

Na GUI, essa lista também pode ser alimentada pelo botão de adicionar pastas na tela `Monitorar`.

## Subpastas Por Data

Quando `date_subfolder` está como `true`, o Sortify acrescenta uma estrutura de data ao destino com base na data de modificação do arquivo.

Exemplo:

```text
PDFs/
└── 2026/
    └── Abril/
        └── contrato.pdf
```

Essa opção é ótima quando você quer histórico temporal, mas ela aumenta a profundidade da árvore de pastas. Para algumas rotinas, manter `false` pode deixar a navegação mais direta.

## Notificações E Bandeja

| Campo | Requisito adicional | Observação |
|---|---|---|
| `notifications_enabled` | `plyer` | Sem a dependência, a notificação é simplesmente ignorada |
| `minimize_to_tray` | `pystray` e `Pillow` | Sem o suporte opcional, a janela apenas minimiza normalmente |

## Agendamento

O scheduler interno suporta dois modos:

- `daily`: executa em um horário fixo;
- `interval`: executa em um intervalo em minutos.

### Modo diário

```json
{
  "scheduled_enabled": true,
  "scheduled_mode": "daily",
  "scheduled_time": "18:00"
}
```

### Modo por intervalo

```json
{
  "scheduled_enabled": true,
  "scheduled_mode": "interval",
  "scheduled_interval_minutes": 30
}
```

## Idioma

O projeto já possui infraestrutura de i18n em `locale/` e `i18n.py`. O campo `language` controla qual arquivo de idioma será carregado.

Exemplo:

```json
{
  "language": "pt"
}
```

## Boas Práticas De Configuração

1. Comece com poucas categorias.
2. Adicione regras personalizadas apenas quando o agrupamento por extensão não resolver.
3. Use simulação antes de ativar monitoramento e agendamento.
4. Teste o undo depois de qualquer ajuste importante.
5. Se a pasta for crítica, faça um teste em cópia antes de apontar para o diretório real.
