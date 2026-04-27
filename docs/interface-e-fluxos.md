# Interface E Fluxos

Esta página explica como a experiência do usuário foi organizada hoje entre GUI e CLI, e como transformar isso em um fluxo de uso confiável.

## Visão Geral Da GUI

A aplicação gráfica foi construída com `customtkinter` e organizada em cinco páginas principais:

| Área | Papel |
|---|---|
| `Dashboard` | Resume a sessão, mostra contadores, status, progresso e atalhos rápidos |
| `Organizar` | Executa organização manual, simulação, busca de duplicados e undo |
| `Monitorar` | Gerencia monitoramento contínuo e agendamento automático |
| `Configurações` | Edita categorias e regras personalizadas em JSON |
| `Logs` | Centraliza o histórico da sessão para leitura rápida |

## Dashboard

O `Dashboard` é a tela de operação imediata. Ele concentra:

- status atual do app;
- contadores de arquivos movidos, ignorados e erros;
- ações rápidas para `Downloads`, `Desktop`, pasta customizada, simulação e ferramentas.

### Quando usar

- quando você quer executar uma ação rápida sem navegar por muitas telas;
- quando deseja acompanhar uma sessão atual de organização;
- quando precisa observar progresso e mensagens em tempo real.

## Página Organizar

Aqui fica o fluxo principal de trabalho manual.

### Blocos da página

| Bloco | O que faz |
|---|---|
| `Pastas padrão` | Organiza `Downloads` ou `Desktop` com um clique |
| `Pasta personalizada` | Permite escolher qualquer diretório |
| `Simular primeiro` | Exibe o que seria feito antes da execução real |
| `Criar sub-pastas por data` | Ativa a organização por ano e mês |
| `Buscar duplicados` | Procura cópias por hash MD5 |
| `Desfazer última organização` | Reverte a última operação salva |

### Fluxo recomendado

1. Teste em uma pasta controlada.
2. Rode a simulação.
3. Ajuste categorias ou regras se o resultado não agradar.
4. Execute a organização real.
5. Se algo sair diferente do esperado, use o undo.

## Página Monitorar

Essa tela atende quem quer o Sortify rodando de forma mais contínua.

### Recursos presentes

| Recurso | Descrição |
|---|---|
| Lista de pastas monitoradas | Mantém diretórios observados pela aplicação |
| Iniciar monitoramento | Liga `watchdog` para reagir a novos arquivos |
| Parar monitoramento | Encerra os observers ativos |
| Agendamento automático | Executa organização diária ou por intervalo |

### Como o monitoramento funciona

- a aplicação observa eventos de criação de arquivo;
- diretórios não são processados, apenas arquivos;
- existe uma pequena espera antes do movimento, para reduzir conflitos com arquivos ainda sendo gravados;
- os destinos seguem as mesmas regras do fluxo manual.

## Página Configurações

É uma tela voltada para quem quer controle fino.

### O que pode ser editado hoje

- categorias por extensão;
- regras personalizadas;
- persistência em `config.json`.

### Como a experiência funciona

O app mostra o JSON atual dentro de caixas de texto editáveis. Quando você salva:

- o conteúdo é validado;
- a configuração é normalizada;
- o arquivo `config.json` é regravado.

!!! info "Ponto importante"
    Hoje a GUI expõe diretamente a configuração de categorias e regras. Campos como idioma, notificações e bandeja ainda fazem mais sentido por edição manual do `config.json`.

## Página Logs

Os logs da sessão ajudam a responder perguntas importantes:

- quais arquivos foram movidos;
- quais foram ignorados;
- se houve erro de permissão;
- quantos itens foram processados;
- quando uma tarefa começou e terminou.

Essa tela é especialmente útil em:

- simulações;
- monitoramento contínuo;
- agendamento;
- undo;
- diagnóstico de duplicados.

## CLI

A versão de terminal reutiliza o mesmo `core.py`, então a lógica de organização é a mesma. O que muda é o canal de interação.

### Menu atual

| Opção | Ação |
|---|---|
| `1` | Organizar `Downloads` |
| `2` | Organizar `Desktop` |
| `3` | Organizar outra pasta |
| `4` | Simular organização |
| `5` | Desfazer última organização |
| `6` | Buscar duplicados |
| `7` | Monitorar `Downloads` em tempo real |
| `8` | Sair |

### Quando a CLI faz mais sentido

- para testar rapidamente;
- para usar em servidores ou VMs com menos interface;
- para validar o comportamento do `core.py` sem abrir a GUI;
- para usuários que preferem menus simples de terminal.

## Fluxos Recomendados

### Fluxo 1: primeira configuração segura

1. Ajuste `config.json`.
2. Rode a simulação em uma pasta de teste.
3. Execute a organização real.
4. Teste o undo.
5. Só então aplique em `Downloads` ou `Desktop`.

### Fluxo 2: operação diária

1. Use a GUI para organizar manualmente os diretórios principais.
2. Acompanhe o progresso e os contadores.
3. Consulte logs se houver dúvida.

### Fluxo 3: automação contínua

1. Cadastre pastas em `Monitorar`.
2. Valide o comportamento com poucos arquivos.
3. Ative o monitoramento em tempo real.
4. Depois, se quiser, ligue o scheduler.

### Fluxo 4: limpeza de acervo antigo

1. Escolha uma pasta grande e rode simulação.
2. Organize em lote.
3. Rode a busca de duplicados.
4. Revise a pasta `Duplicados/`.
5. Use o undo se necessário.

## O Que Vale Saber Antes De Automatizar

- arquivos em uso podem falhar ao mover;
- regras muito genéricas podem mandar arquivos para destinos inesperados;
- subpastas por data aumentam bastante a profundidade da estrutura;
- o histórico de undo desfaz a última operação salva, então vale operar com etapas conscientes.
