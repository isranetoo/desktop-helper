# Solução De Problemas

Esta página reúne os problemas mais prováveis ao usar, configurar ou publicar o Sortify.

## O arquivo não foi movido

Verifique estas possibilidades:

- o arquivo está com extensão ou nome incluído nas listas de ignorados;
- ele ainda está em uso por outro programa;
- a regra personalizada enviou para outro destino;
- você rodou simulação, mas não confirmou a execução real.

## O arquivo foi para a pasta errada

Em geral, isso acontece por prioridade de regras.

Lembre:

- regras personalizadas são testadas antes das categorias;
- `name_contains` pode ser amplo demais;
- `name_starts_with` pode capturar mais arquivos do que o esperado.

### Como corrigir

1. rode uma simulação;
2. revise `custom_rules`;
3. ajuste nomes de destino;
4. use undo se a organização já foi executada.

## O undo não encontrou nada para desfazer

Isso normalmente significa uma destas situações:

- ainda não houve organização registrada;
- o histórico já foi desfeito;
- o arquivo `undo_history.json` foi removido;
- a operação anterior não moveu nenhum arquivo.

## Duplicados não foram detectados

Algumas razões possíveis:

- os arquivos têm nomes iguais, mas conteúdo diferente;
- você esperava comparação por nome, mas o app compara por hash;
- o arquivo repetido já estava em `Duplicados/`, pasta que é ignorada pela varredura.

## Notificações não aparecem

Cheque:

```bash
pip install -r requirements-optional.txt
```

Depois confirme se `notifications_enabled` está `true` no `config.json`.

Se `plyer` não estiver disponível, o app continua funcionando sem notificar.

## Minimizar para a bandeja não funciona

Esse recurso depende de:

- `pystray`;
- `Pillow`;
- `minimize_to_tray: true`.

Mesmo com isso, a experiência final pode depender do ambiente Windows e do empacotamento da aplicação.

## O monitoramento não reagiu a um arquivo novo

Verifique:

- se o monitoramento foi realmente iniciado;
- se a pasta está na lista monitorada;
- se o arquivo criado não foi ignorado;
- se o arquivo não ficou bloqueado por outro processo.

## O scheduler não executou

Revise:

- `scheduled_enabled`;
- `scheduled_mode`;
- `scheduled_time` no formato `HH:MM`;
- `scheduled_interval_minutes` com número inteiro maior que zero;
- existência real das pastas monitoradas.

## O `config.json` quebrou

Se o JSON estiver inválido, o sistema pode cair para a configuração padrão ao carregar.

### Como evitar

- valide o JSON antes de salvar;
- faça alterações pequenas por vez;
- teste com simulação logo depois.

## O `mkdocs build` falhou

Instale as dependências:

```bash
pip install mkdocs mkdocs-material
```

Depois rode de novo:

```bash
mkdocs build
```

## O logo não aparece na documentação

Verifique:

- se `docs/assets/sortify.png` existe;
- se `mkdocs.yml` aponta para `assets/sortify.png`;
- se o cache do navegador não está servindo uma versão antiga.

## Os testes não rodam

Instale:

```bash
pip install -r requirements-dev.txt
```

Depois:

```bash
pytest
```

## Há caracteres estranhos no terminal

Em alguns terminais Windows, a exibição de acentos e símbolos pode variar conforme a codificação ativa. Isso costuma afetar mais a visualização no console do que o conteúdo real salvo nos arquivos.

## Dica De Diagnóstico Rápido

Quando algo parecer estranho, a ordem mais eficiente costuma ser:

1. olhar os logs;
2. rodar simulação;
3. revisar `config.json`;
4. testar undo;
5. só então repetir a automação.
