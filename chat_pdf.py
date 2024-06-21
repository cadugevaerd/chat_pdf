import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
import tempfile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_huggingface import HuggingFaceEndpoint
from langchain_huggingface.chat_models.huggingface import ChatHuggingFace
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()


with st.spinner("Carregando..."):
    embbedding_model = OpenAIEmbeddings(model='text-embedding-ada-002')
    chat = ChatOpenAI(model="gpt-3.5-turbo")

def upload_pdf():
    files = st.sidebar.file_uploader("Selecione o PDF", type="pdf", accept_multiple_files=True)
    if files:
        paginas = []
        for file in files:
            # Cria um arquivo temporário para salvar o conteúdo do PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(file.read())
                temp_file_path = temp_file.name
            
            # Carrega o PDF usando o caminho do arquivo temporário
            loader = PyPDFLoader(temp_file_path)
            paginas.extend(loader.load())
        
        st.session_state["paginas"] = paginas
        st.session_state['vector_store'] = None
        st.session_state['retriever'] = None
        split_text()
        vector_store_ini()
    else:
        st.session_state["paginas"] = []
        st.session_state['paginas_splitadas'] = []
        st.session_state['vector_store'] = None
        st.session_state['retriever'] = None
        
        
def split_text():
    if 'paginas' in st.session_state:
        if len(st.session_state["paginas"]) > 0:
            chunk_size = 500
            chunk_overlap = 50
            doc_split = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=['\n\n', '\n', '.', '?', '!', ' ', '']
            )
            documents = doc_split.split_documents(st.session_state["paginas"])
            st.session_state['paginas_splitadas'] = documents
        else:
            st.session_state['paginas_splitadas'] = []
def chat_pdf():
    if 'vector_store' in st.session_state and st.session_state['vector_store'] is not None:
        input_text = st.chat_input("prompt:")
        if input_text:
            human_chat = st.chat_message('human')
            human_chat.markdown(input_text)
            ai_chat = st.chat_message('ai')
            with st.spinner("Carregando..."):
                retriever = st.session_state['retriever']
                #st.write('retriever',retriever)
                #st.write('vector_store',st.session_state['vector_store'])
                #st.write('paginas_splitadas',st.session_state['paginas_splitadas'])
                if retriever:
                    chat_chain = RetrievalQA.from_chain_type(
                        retriever=retriever,
                        llm=chat,
                    )
                    resposta = chat_chain.invoke(input_text)
                    result_text = resposta.get('result', '')
                    ai_chat.write(result_text)
                    #try:
                    #    resposta = chat_chain({"query": input_text})
                    #except:

    else:
        st.error("Nenhum PDF carregado!")

def consulta_retriever():
    if 'vector_store' in st.session_state and st.session_state['vector_store'] is not None:
        metadata_info = [
            AttributeInfo(name="source", description="a fonte do documento", type="string"),
            AttributeInfo(name="page", description="The page number of the document", type="integer")
        ]
        document_description = "Documentos PDFs para análises"
        vector_store = st.session_state['vector_store']
        retriever = SelfQueryRetriever.from_llm(
            chat,
            vector_store,
            document_description,
            metadata_info,
        )
        st.session_state['retriever'] = retriever
    else:
        st.session_state['retriever'] = None
        

def inicializar():
    if 'paginas' not in st.session_state:
        st.session_state["paginas"] = []
    if 'paginas_splitadas' not in st.session_state:
        st.session_state['paginas_splitadas'] = []
    if 'vector_store' not in st.session_state:
        st.session_state['vector_store'] = None
    if 'retriever' not in st.session_state:
        st.session_state['retriever'] = None

def vector_store_ini():
    if 'paginas_splitadas' in st.session_state and len(st.session_state['paginas_splitadas']) > 0:
        vector_store = Chroma.from_documents(
            documents=st.session_state['paginas_splitadas'],
            embedding=embbedding_model,
        )
        st.session_state['vector_store'] = vector_store
    else:
        st.session_state['vector_store'] = None
        

def main():
    st.title("Chat PDF")
    inicializar()
    upload_pdf()
    split_text()
    vector_store_ini()
    consulta_retriever()
    chat_pdf()
    
    
if __name__ == "__main__":
    main()