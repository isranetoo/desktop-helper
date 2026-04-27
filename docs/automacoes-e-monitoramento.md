# Automações E Monitoramento

Esta é a parte da documentação que cobre o lado mais poderoso do Sortify: deixar a organização funcionando com pouca intervenção manual.

## Simulação Antes Da Automação

Antes de ativar qualquer rotina contínua, o melhor caminho é validar a lógica por simulação.

Na prática, a simulação:

- percorre os arquivos da pasta;
- ignora itens temporários ou bloqueados pelas listas de exclusão;
- calcula o destino provável;
- registra as ações planejadas nos logs;
- não move nada.

### Por que isso importa

Em automação, o risco não está só em mover arquivos. O risco está em mover certo demais para a regra errada. A simulação reduz exatamente esse tipo de erro.

## Monitoramento Em Tempo Real

O monitoramento usa `watchdog` para observar pastas cadastradas e reagir quando novos arquivos aparecem.

### Comportamento atual

- apenas novos arquivos criados são processados automaticamente;
- diretórios são ignorados;
- a rotina espera um pequeno intervalo antes de mover, ajudando em casos de arquivos ainda sendo gravados;
- cada arquivo usa o mesmo motor de regras do fluxo manual.

### Configurando pela GUI

1. Abra `Monitorar`.
2. Clique em `Adicionar pasta`.
3. Escolha um diretório.
4. Inicie o monitoramento.
5. Acompanhe o status e os logs.

### Situações ideais para usar

- pasta de `Downloads`;
- área de entrada de documentos;
- diretório que recebe anexos ou exportações de outros sistemas;
- fluxo pessoal de capturas de tela e PDFs.

## Agendamento Automático

Além do modo em tempo real, a aplicação possui scheduler próprio.

### Modo diário

Use quando você quer consolidar organização em um horário previsível, como no fim do expediente.

Exemplo:

```json
{
  "scheduled_enabled": true,
  "scheduled_mode": "daily",
  "scheduled_time": "18:00"
}
```

### Modo intervalo

Use quando a pasta recebe arquivos ao longo do dia e você prefere rodadas periódicas.

Exemplo:

```json
{
  "scheduled_enabled": true,
  "scheduled_mode": "interval",
  "scheduled_interval_minutes": 30
}
```

### Como pensar a escolha

| Cenário | Melhor modo |
|---|---|
| Organização de fim de dia | `daily` |
| Caixa de entrada que enche o tempo todo | `interval` |
| Uso mais previsível e silencioso | `daily` |
| Uso operacional com atualização constante | `interval` |

## Undo

Toda organização bem automatizada precisa de reversão confiável. O Sortify salva um histórico com origem e destino dos arquivos movidos.

### O que o undo faz

- recupera a última operação registrada;
- move os arquivos de volta em ordem reversa;
- limpa diretórios vazios criados pela organização;
- remove a entrada já desfeita da pilha.

### O que isso permite

- testar novas regras com menos medo;
- organizar em etapas;
- corrigir execuções indesejadas sem refazer tudo manualmente.

!!! warning "Escopo do undo"
    O desfazer atua sobre a última entrada salva no histórico. Se você fizer várias operações, a reversão também acontece em camadas, da mais recente para a mais antiga.

## Duplicados

O recurso de duplicados percorre a árvore da pasta de forma recursiva e calcula hash MD5 para encontrar arquivos com conteúdo idêntico.

### Comportamento importante

- a pasta `Duplicados/` é ignorada na própria varredura;
- diretórios como `logs`, `__pycache__` e `.git` também ficam de fora;
- somente os duplicados encontrados depois do primeiro arquivo igual são movidos.

### Resultado esperado

```text
workspace/
├── foto-original.jpg
├── Duplicados/
│   └── copia-foto.jpg
└── documento.pdf
```

## Notificações

As notificações dependem de `plyer`.

### Estratégia atual

- no monitoramento em tempo real, a notificação pode acontecer por arquivo;
- na organização em lote, o sistema prefere notificação-resumo ao final;
- se a dependência não estiver instalada, o app continua funcionando sem quebrar o fluxo.

## Bandeja Do Sistema

Quando `minimize_to_tray` está ativo e as dependências opcionais estão disponíveis:

- fechar a janela pode minimizar para a bandeja;
- o usuário consegue restaurar a interface;
- a aplicação pode continuar ativa em segundo plano.

Se `pystray` não estiver instalado, o app apenas minimiza ou fecha no fluxo padrão.

## Logs

Os logs são a base da observabilidade local do projeto.

### Onde aparecem

- na tela `Logs` da GUI;
- em arquivos diários dentro de `logs/`.

### O que você costuma ver

- início de organização;
- destino de cada arquivo movido;
- itens ignorados;
- erros de permissão;
- início e fim do scheduler;
- detecção de duplicados;
- execução do undo.

## Estratégia Segura Para Ligar Tudo

1. Ajuste e revise `config.json`.
2. Rode simulação.
3. Execute organização manual.
4. Teste o undo.
5. Ative duplicados se fizer sentido para o seu caso.
6. Ligue o monitoramento.
7. Só depois adicione agendamento.

## Padrões De Uso Recomendados

| Perfil | Estratégia |
|---|---|
| Usuário doméstico | Simulação + organização manual + duplicados ocasionais |
| Profissional com muitos PDFs | Regras customizadas + monitoramento em pastas de entrada |
| Operação contínua | Pastas monitoradas + scheduler por intervalo |
| Arquivo histórico | `date_subfolder` ligado + duplicados + logs frequentes |
