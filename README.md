<div align="center">

# ⚡ Assistente de Suporte Técnico WEG

### Chatbot RAG para consulta ao manual do *Nobreak Corporate 5 kVA*

![Python](https://img.shields.io/badge/Python-3.10%2B-00579D?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-00579D?style=for-the-badge&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-RAG_Pipeline-00579D?style=for-the-badge&logo=chainlink&logoColor=white)
![NVIDIA](https://img.shields.io/badge/NVIDIA_NIM-Llama_3.1_8B-00579D?style=for-the-badge&logo=nvidia&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-Vector_Store-003F73?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Projeto_Acadêmico-B5650A?style=for-the-badge)

</div>

<br>

> ### ⚠️ AVISO IMPORTANTE
> Este é um **projeto acadêmico/demonstrativo**. O manual técnico (`material.pdf`) usado como base de conhecimento do RAG é **fictício**: produto, especificações, códigos de alarme (`ERR01`–`ERR15`) e FAQ foram criados apenas para fins de exemplo e teste do pipeline.
>
> Este repositório **não é um produto oficial da WEG S.A.**, não possui qualquer afiliação, patrocínio ou endosso da empresa, e a paleta de cores utilizada na interface é apenas uma referência visual inspirada na identidade institucional da marca. **Não utilize as informações geradas pelo chatbot como referência técnica real.**

<br>

## 📌 Sobre este repositório

Este repositório contém um **chatbot de Recuperação Aumentada por Geração (RAG)** construído com **Streamlit**, que responde perguntas técnicas sobre o Nobreak fictício *"WEG Nobreak Corporate 5 kVA"* tendo como **única fonte de conhecimento** o manual técnico em PDF (`material.pdf`) embarcado no projeto.

Na prática, o app (`app.py`):

1. Carrega e indexa o manual técnico em um banco vetorial (**FAISS**);
2. Recupera os trechos mais relevantes do manual a cada pergunta do usuário;
3. Envia esses trechos como contexto para um modelo de linguagem (**Llama 3.1 8B Instruct**, via **NVIDIA AI Endpoints**);
4. Retorna uma resposta em **PT-BR**, restrita estritamente ao conteúdo do manual — caso a informação não exista no documento, o assistente informa isso explicitamente, em vez de inventar uma resposta.

É, essencialmente, um exemplo de aplicação de **suporte técnico assistido por IA**, usando um manual de equipamento como caso de estudo.

<br>

## 🧠 Como funciona — Pipeline RAG

| Etapa | Componente | Configuração (em `app.py`) |
|---|---|---|
| 1. Carregamento do PDF | `PyPDFLoader` | Lê `material.pdf` página a página |
| 2. Divisão em *chunks* | `RecursiveCharacterTextSplitter` | `chunk_size=750`, `chunk_overlap=150` |
| 3. Geração de embeddings | `NVIDIAEmbeddings` | Modelo `nvidia/nv-embedqa-e5-v5` |
| 4. Indexação vetorial | `FAISS` | `vectorstore.as_retriever(k=5)` |
| 5. Engenharia de prompt | `ChatPromptTemplate` | Restringe a resposta ao contexto recuperado |
| 6. Geração da resposta | `ChatNVIDIA` | Modelo `meta/llama-3.1-8b-instruct`, `temperature=0.1`, `max_tokens=1024` |
| 7. Interface | `st.chat_message` / `st.session_state` | Histórico de conversa persistente na sessão |

A indexação é feita uma única vez por sessão através de `@st.cache_resource`, evitando reprocessar o PDF a cada interação.

<br>

## 🗂 Estrutura esperada do projeto

```text
.
├── app.py              # Aplicação Streamlit (UI + pipeline RAG)
├── material.pdf         # Manual técnico (fictício) usado como base de conhecimento
├── .env                 # Variável de ambiente API_KEY (NVIDIA) — não versionar
└── requirements.txt      # Dependências do projeto
```

> **Nota:** o código espera o arquivo na raiz do projeto com o nome exato `material.pdf`. Caso o manual tenha outro nome (por exemplo `manual.pdf`), renomeie-o ou ajuste a variável `nome_arquivo` em `app.py`.

<br>

## ⚙️ Stack técnica

| Camada | Tecnologia |
|---|---|
| Interface | [Streamlit](https://streamlit.io/) |
| Orquestração RAG | [LangChain](https://www.langchain.com/) (`langchain-community`, `langchain-core`, `langchain-text-splitters`) |
| LLM e Embeddings | [NVIDIA AI Endpoints](https://build.nvidia.com/) (`langchain-nvidia-ai-endpoints`) — Llama 3.1 8B Instruct |
| Banco vetorial | [FAISS](https://github.com/facebookresearch/faiss) |
| Variáveis de ambiente | `python-dotenv` |

<br>

## 🚀 Executando localmente

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd <pasta-do-repositorio>

# 2. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure sua chave de API da NVIDIA
echo "API_KEY=sua_chave_aqui" > .env

# 5. Coloque o manual técnico na raiz do projeto como material.pdf

# 6. Execute a aplicação
streamlit run app.py
```

A aplicação ficará disponível em `http://localhost:8501`.

<br>

## 🎨 Identidade visual

A interface utiliza uma paleta inspirada no azul institucional da WEG, aplicada via CSS injetado em `app.py`:

| Elemento | Cor |
|---|---|
| Títulos (`h1`, `h2`, `h3`) | `#00579D` |
| Botões | `#00579D` (hover `#003F73`) |
| Borda da barra lateral | `#00579D` |
| Fundo da barra lateral | `#f4f6f9` |

A barra lateral também exibe o status da conexão com a API, a confirmação de carregamento/vetorização do manual e um botão para limpar o histórico da conversa.

<br>

## 👥 Referências:

**Empresa de referência (projeto):** PowerTech Solutions
**Produto de referência (fictício):** WEG Nobreak Corporate 5 kVA
**Modelo de IA:** Llama 3.1 8B Instruct (NVIDIA AI Endpoints)

<br>

## ⚠️ Limitações conhecidas

- Depende de uma chave de API válida da NVIDIA (`API_KEY` no `.env`) para embeddings e geração de respostas.
- O logo exibido na barra lateral é carregado de uma URL externa (Wikimedia Commons) — requer conexão à internet.
- O índice vetorial é reconstruído em memória a cada novo processo da aplicação (sem persistência em disco).
- O assistente responde **apenas** com base no conteúdo do `material.pdf` carregado; perguntas fora do escopo do manual recebem uma resposta padrão informando a ausência da informação.

<br>

## 📄 Licença / Uso

Projeto de caráter **educacional/demonstrativo**. Sinta-se à vontade para estudar, adaptar e reutilizar o código como referência para outros pipelines de RAG com Streamlit + LangChain + NVIDIA AI Endpoints.

---