# Primeiros Passos

Esta página é o caminho mais curto para sair do zero e chegar à primeira organização de arquivos com segurança.

## 1. Pré-requisitos

- Windows é o foco principal do projeto.
- Python `3.10+`.
- `pip` disponível no terminal.

## 2. Clonar e instalar

```bash
git clone https://github.com/isranetoo/desktop-helper.git
cd desktop-helper
pip install -r requirements.txt
```

### Dependências opcionais

Se você quiser notificações do sistema e suporte à bandeja:

```bash
pip install -r requirements-optional.txt
```

### Dependências de desenvolvimento

```bash
pip install -r requirements-dev.txt
```

## 3. Executar

=== "GUI"

    ```bash
    python organizador_gui.py
    ```

    Recomendado para uso diário. Você terá dashboard, progresso, logs, edição de regras e monitoramento.

=== "CLI"

    ```bash
    python organizador_cli.py
    ```

    Recomendado para testes rápidos, automação manual e ambientes em que você quer interagir só pelo terminal.

## 4. Entender O Primeiro Fluxo

O fluxo inicial mais seguro é este:

1. Abra a GUI.
2. Vá em `Organizar`.
3. Clique em `Simular primeiro`.
4. Escolha uma pasta de teste.
5. Revise os destinos sugeridos nos logs.
6. Confirme a organização real apenas se o resultado fizer sentido.

!!! info "Por que começar pela simulação?"
    Porque ela permite validar categorias, regras e arquivos ignorados antes de qualquer movimentação real.

## 5. Conferir O Arquivo De Configuração

O projeto usa `config.json` como fonte principal de comportamento. Mesmo que você opere pela GUI, vale conhecer a estrutura:

- `categories`: mapeia pastas destino por extensão;
- `custom_rules`: cria exceções mais inteligentes;
- `ignored_extensions` e `ignored_names`: evitam mover lixo técnico;
- `date_subfolder`: cria subpastas por ano e mês;
- `monitored_folders`: define onde o monitoramento atua;
- `scheduled_*`: controla o agendamento automático.

Exemplo mínimo:

```json
{
  "categories": {
    "Imagens": [".jpg", ".png"],
    "PDFs": [".pdf"],
    "Documentos": [".txt", ".docx", ".md"]
  },
  "ignored_extensions": [".lnk", ".ini", ".url"],
  "ignored_names": ["desktop.ini", "Thumbs.db"],
  "custom_rules": [],
  "date_subfolder": false
}
```

## 6. Fazer Um Teste Controlado

Monte uma pasta de teste com alguns arquivos:

```text
teste-sortify/
├── contrato.pdf
├── print.png
├── notas.txt
└── setup.exe
```

Depois rode a simulação ou organização. Com a configuração padrão, um resultado esperado seria:

```text
teste-sortify/
├── PDFs/
│   └── contrato.pdf
├── Imagens/
│   └── print.png
├── Documentos/
│   └── notas.txt
└── Executaveis/
    └── setup.exe
```

## 7. Validar Undo E Duplicados

Dois recursos merecem teste já no começo:

- `Desfazer última organização`: confirma se o histórico foi salvo corretamente.
- `Buscar duplicados`: verifica se cópias reais são movidas para `Duplicados/`.

Essa validação ajuda a ganhar confiança antes de aplicar o fluxo em pastas importantes.

## 8. Rodar Testes Automatizados

```bash
pytest
```

Os testes cobrem principalmente o núcleo:

- filtros de arquivos ignorados;
- regras personalizadas;
- normalização da configuração;
- organização e undo;
- múltiplas entradas na pilha de undo;
- detecção de duplicados.

## 9. Rodar A Documentação Localmente

```bash
pip install mkdocs mkdocs-material
mkdocs serve
```

Depois acesse `http://127.0.0.1:8000`.

## 10. Próximo Passo Recomendado

Depois do primeiro teste, a ordem mais produtiva costuma ser:

1. ajustar `config.json`;
2. revisar a página `Configuração`;
3. ligar monitoramento só depois da simulação estar correta;
4. configurar agendamento quando o fluxo manual já estiver confiável.
