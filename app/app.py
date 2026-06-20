import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings, ChatNVIDIA

load_dotenv()

# ==========================================
# 1. CONFIGURAÇÃO VISUAL E TEMA WEG
# ==========================================
st.set_page_config(
    page_title="Suporte Técnico WEG",
    page_icon="🔷",
    layout="wide"
)

# Injeção de CSS para as cores da WEG (#00579D)
st.markdown("""
    <style>
    /* Estilização dos cabeçalhos e botões */
    h1, h2, h3 { color: #00579D !important; }
    .stButton>button { background-color: #00579D; color: white; border-radius: 5px; }
    .stButton>button:hover { background-color: #003F73; color: white; }
    
    /* Estilização da Sidebar */
    [data-testid="stSidebar"] { background-color: #f4f6f9; border-right: 2px solid #00579D; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BARRA LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    # URL pública do logo da WEG para deixar profissional
    st.image("weg_logo.svg", width=150)
    st.title("⚙️ Info do Projeto")
    st.markdown("**Empresa:** PowerTech Solutions")
    st.markdown("**Produto:** WEG Nobreak Corporate 5 kVA")
    st.markdown("**Modelo IA:** Llama 3.1 8B (NVIDIA)")
    
    st.divider()
    st.markdown("### Status do Sistema")
    
    # Botão de Limpar Conversa
    if st.button("🗑 Limpar Conversa", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "Olá! Sou o especialista WEG. Como posso ajudar com seu Nobreak hoje?"}]
        st.rerun()

# ==========================================
# 3. VALIDAÇÃO DE API E STATUS
# ==========================================
st.title("Assistente de Suporte Técnico WEG")

nvidia_api_key = os.getenv("API_KEY")

if not nvidia_api_key:
    st.error("Chave API não encontrada no arquivo .env.")
    st.stop()
else:
    st.sidebar.success("IA Conectada")

# ==========================================
# 4. PIPELINE DO RAG E VETORIZAÇÃO
# ==========================================
@st.cache_resource(show_spinner="Processando o Manual WEG...")
def inicializar_rag():
    nome_arquivo = "manual.pdf"

    if not os.path.exists(nome_arquivo):
        st.error(f"Arquivo '{nome_arquivo}' não encontrado.")
        st.stop()
        
    loader = PyPDFLoader(nome_arquivo)
    paginas = loader.load()
    st.sidebar.success("Manual Carregado")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=750,
        chunk_overlap=150,
    )
    docs = text_splitter.split_documents(paginas)

    embeddings = NVIDIAEmbeddings(
        model="nvidia/nv-embedqa-e5-v5",
        api_key=nvidia_api_key,
        model_type="passage"
    )

    vectorstore = FAISS.from_documents(docs, embedding=embeddings)
    st.sidebar.success("Vetorização Concluída")

    return vectorstore.as_retriever(search_kwargs={"k": 5})

retriever = inicializar_rag()

# Configuração do LLM com max_tokens e temperature
llm = ChatNVIDIA(
    model="meta/llama-3.1-8b-instruct",
    api_key=nvidia_api_key,
    base_url="https://integrate.api.nvidia.com/v1",
    temperature=0.1,    # Baixa criatividade para focar no manual
    max_tokens=1024     # Requisito Técnico da Etapa 2
)

# ==========================================
# 5. ENGENHARIA DE PROMPT PROFISSIONAL
# ==========================================
template_prompt = """
Você é um engenheiro especialista em manutenção industrial da WEG.
Sua tarefa é auxiliar técnicos a diagnosticar problemas e consultar procedimentos do WEG Nobreak Corporate 5 kVA.
As informações devem ser obtidas EXCLUSIVAMENTE do manual técnico fornecido no contexto abaixo.

Restrições Críticas:
1. Responda em Português do Brasil (PT-BR) de forma técnica, mas clara.
2. Caso a informação solicitada não exista no manual, informe claramente: "Desculpe, mas esta informação não consta no manual técnico oficial." Não invente dados de hipótese alguma.

Contexto extraído do PDF:
{context}

Pergunta do técnico: {question}
Resposta detalhada:
"""

prompt = ChatPromptTemplate.from_template(template_prompt)

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# ==========================================
# 6. INTERFACE DO CHATBOT
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Sou o especialista WEG. Qual alarme ou procedimento você deseja consultar?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt_usuario := st.chat_input("Ex: Como resolver o código ERR02?"):
    st.session_state.messages.append({"role": "user", "content": prompt_usuario})
    with st.chat_message("user"):
        st.write(prompt_usuario)

    with st.chat_message("assistant"):
        with st.spinner("Analisando diagramas e o manual técnico..."):
            try: # Requisito Técnico da Etapa 2
                resposta = rag_chain.invoke(prompt_usuario)
                st.write(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})
            except Exception as e:
                st.error(f"Erro ao processar a requisição técnica: {e}")    