# Configuração

A configuração principal fica em `config.json`.

## Exemplo de regra

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

## Condições suportadas

| Chave | Tipo | Exemplo |
|---|---|---|
| `extension` | string ou lista | `.pdf` / `[".pdf", ".xml"]` |
| `name_contains` | string | `nota` |
| `name_starts_with` | string | `IMG_` |
