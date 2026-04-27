<div class="hero">
  <div class="hero__copy">
    <p class="hero__eyebrow">Windows • Python • GUI + CLI</p>
    <h1>Sortify</h1>
    <p class="hero__lead">
      Um organizador de arquivos com foco em rotina real: limpa pastas como
      <code>Downloads</code> e <code>Desktop</code>, aplica regras customizadas,
      encontra duplicados, salva histórico para undo e ainda pode monitorar
      mudanças em tempo real.
    </p>
    <div class="hero__actions">
      <a class="md-button md-button--primary" href="guia-rapido/">Começar agora</a>
      <a class="md-button" href="configuracao/">Ver configuração</a>
    </div>
  </div>
  <div class="hero__media">
    <img src="assets/sortify.png" alt="Logo do Sortify">
  </div>
</div>

## O Que Você Encontra Nesta Documentação

<div class="feature-grid">
  <article class="feature-card">
    <h3>Primeiros passos</h3>
    <p>Instalação, execução da GUI e da CLI, dependências opcionais e primeiro uso seguro.</p>
  </article>
  <article class="feature-card">
    <h3>Configuração detalhada</h3>
    <p>Explicação completa de <code>config.json</code>, categorias, regras, monitoramento e agendamento.</p>
  </article>
  <article class="feature-card">
    <h3>Fluxos reais</h3>
    <p>Como usar simulação, undo, duplicados, logs e automações no dia a dia.</p>
  </article>
  <article class="feature-card">
    <h3>Arquitetura</h3>
    <p>Mapa do código para entender como GUI, CLI, core, i18n, testes e deploy de docs se conectam.</p>
  </article>
</div>

## Resumo Do Produto

O Sortify é um utilitário desktop focado em automação de organização de arquivos. Ele foi construído para reduzir trabalho manual e, ao mesmo tempo, manter previsibilidade: antes de executar, você pode simular; depois de executar, você pode desfazer.

Esse equilíbrio entre automação e controle aparece em toda a aplicação:

- a GUI facilita uso diário e configuração visual;
- a CLI mantém o projeto acessível para fluxos rápidos;
- o `core.py` concentra a lógica de negócio;
- o histórico de undo evita medo de "organizar demais";
- os logs ajudam a diagnosticar o que aconteceu em cada execução.

## Destaques Técnicos

<div class="workflow-grid">
  <section class="workflow-step">
    <span>01</span>
    <h3>Regras antes de categorias</h3>
    <p>O sistema testa regras personalizadas antes de cair no agrupamento tradicional por extensão.</p>
  </section>
  <section class="workflow-step">
    <span>02</span>
    <h3>Nomes seguros</h3>
    <p>Se já existir um arquivo com o mesmo nome no destino, o Sortify cria uma variação sem sobrescrever.</p>
  </section>
  <section class="workflow-step">
    <span>03</span>
    <h3>Undo persistente</h3>
    <p>Cada organização gera registros de origem e destino para reversão posterior.</p>
  </section>
  <section class="workflow-step">
    <span>04</span>
    <h3>Operação contínua</h3>
    <p>Com <code>watchdog</code> e scheduler, o projeto também atende cenários de automação recorrente.</p>
  </section>
</div>

## Capacidades Principais

| Área | O que o Sortify faz |
|---|---|
| Organização manual | Organiza `Downloads`, `Desktop` ou qualquer pasta escolhida |
| Simulação | Mostra o destino provável sem mover nada |
| Duplicados | Calcula hash MD5 e separa cópias em `Duplicados/` |
| Undo | Reverte a última operação salva no histórico |
| Monitoramento | Observa novas entradas em pastas cadastradas |
| Agendamento | Executa por horário diário ou intervalo em minutos |
| Logs | Registra operações em arquivo e na tela |
| Configuração | Permite editar categorias e regras via JSON |

## Quando O Projeto Brilha

!!! tip "Cenários em que ele ajuda muito"
    - Quem acumula arquivos em `Downloads` diariamente.
    - Quem recebe muitos PDFs, capturas de tela e instaladores.
    - Quem quer manter uma rotina de organização automática com possibilidade de desfazer.
    - Quem prefere configurar por JSON, mas ainda quer uma GUI amigável para operar.

## Mapa Rápido Das Páginas

| Página | Para que serve |
|---|---|
| `Primeiros passos` | Instalar, executar e validar a primeira organização |
| `Interface e fluxos` | Entender GUI, CLI e os fluxos recomendados |
| `Configuração` | Dominar o `config.json` e os campos relevantes |
| `Automações` | Usar monitoramento, scheduler, duplicados e notificações |
| `Exemplos` | Copiar cenários prontos e adaptar para sua rotina |
| `Arquitetura` | Entender a base de código e o desenho do projeto |
| `Empacotamento e Releases` | Gerar builds para Windows/macOS/Linux e publicar no GitHub Releases |
| `Deploy docs` | Publicar a documentação no GitHub Pages |
| `Solução de problemas` | Resolver erros e dúvidas operacionais comuns |

## Estado Atual Do Projeto

O conjunto principal de recursos já está implementado e testado no núcleo da aplicação. A documentação abaixo foi alinhada ao comportamento real do código, incluindo alguns detalhes importantes:

- regras customizadas têm prioridade sobre categorias;
- `date_subfolder` é o campo que realmente ativa subpastas por data;
- `organize_mode` existe na estrutura da configuração, mas a versão atual opera com categorias e data opcional;
- notificações, bandeja e ícones exigem dependências opcionais e atenção ao empacotamento final.
