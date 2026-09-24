# 🤖 Agente Corporativo de IA

Agente de IA desenvolvido em Python e Streamlit para responder perguntas com base em documentos da empresa.
O agente também mostra as fontes utilizadas em cada resposta.

## Como funciona

O usuário pode:

* Fazer perguntas sobre os documentos;
* Ver os documentos disponíveis;
* Reindexar os documentos;
* Ver as fontes utilizadas nas respostas;
* Limpar o histórico da conversa.

O funcionamento básico é:

```text
Usuário
   ↓
Streamlit
   ↓
app.py
   ↓
Base de conhecimento (RAG)
   ↓
OCI Generative AI
   ↓
Resposta + fontes
```

## Estrutura

```text
agente-corporativo/
├── app.py
├── src/
│   ├── config.py
│   ├── loaders.py
│   └── rag.py
├── requirements.txt
├── .env.example
├── Dockerfile
└── README.md
```

### app.py

É o arquivo principal do projeto.

Nele estão:

* A interface do Streamlit;
* O chat com o usuário;
* O histórico das mensagens;
* A consulta à base de conhecimento;
* A exibição das respostas;
* A exibição das fontes.

### src/

Contém os arquivos responsáveis pela configuração, leitura dos documentos e funcionamento do RAG.

### requirements.txt

Contém as bibliotecas utilizadas pelo projeto.

Para instalar:

```bash
pip install -r requirements.txt
```

### .env.example

Contém um exemplo das configurações necessárias para utilizar a OCI Generative AI.

As informações reais devem ser colocadas no arquivo `.env`.

## Documentos

O agente pode utilizar diferentes tipos de documentos como fonte de informação, como:

* PDF
* Word
* Excel
* PowerPoint
* Markdown
* CSV
* JSON
* HTML

Os documentos são processados e utilizados para criar a base de conhecimento.

## Configuração

Primeiro, crie um ambiente virtual:

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

Depois instale as dependências:

```bash
pip install -r requirements.txt
```

Crie o arquivo `.env`:

```bash
cp .env.example .env
```

## Executando

Para iniciar a aplicação:

```bash
streamlit run app.py
```

Na primeira execução, os documentos são indexados automaticamente.

## Exemplos de perguntas

O agente pode responder perguntas como:

```text
Quantos dias de férias posso fracionar?

Qual é o procedimento para solicitar férias?

Quais são as regras de trabalho remoto?

Como funciona o processo de reembolso?
```

As respostas são baseadas nos documentos disponíveis na base de conhecimento.


## Tecnologias utilizadas

* Python
* Streamlit
* RAG
* Docker


A aplicação será disponibilizada na porta `8501`.
### NAO CONSEGUI COLOCAR UMA FOTO OU IMAGEM RODANDO NA ORACLE CLOUD
Tentei criar uma conta mas n conseguia de forma alguma, ate colocando cartao de credito e n foi