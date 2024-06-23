import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_core.prompts.prompt import PromptTemplate
from gera_config import load_config
import json


def importa_documento(files):
    if files is not None:
        paginas = []
        for file in files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(file.read())
                temp_file_path = temp_file.name

            loader = PyPDFLoader(temp_file_path)
            paginas.extend(loader.load())
        return paginas
    else:
        return []
    
def split_documents(documents):
    chunk_size = 2500
    chunk_overlap = 250
    separators = ['\n\n', '\n', '.', '?', '!', ' ', '']
    char_split = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
    )
    documents = char_split.split_documents(
    documents
    )
    return documents

def cria_vector_store(documents,api_key):
    embbedding_model = OpenAIEmbeddings(api_key=api_key)
    vector_store = FAISS.from_documents(documents, embbedding_model)
    return vector_store

def cria_chain_chat(files,api_key):
    config = load_config()
    model = config['DEFAULT']['model']
    retrievel_search_type = config['DEFAULT']['retrieval_search_type']
    retrievel_args = json.loads(config['DEFAULT']['retrieval_args'])
    prompt = config['DEFAULT']['prompt']
    docs = importa_documento(files)
    docs = split_documents(docs)
    vector_store = cria_vector_store(docs,api_key)
    chat = ChatOpenAI(model=model,api_key=api_key)
    memory = ConversationBufferMemory(return_messages=True,
                                      memory_key="chat_history",
                                      output_key='answer')
    
    retriever = vector_store.as_retriever(
        search_type = retrievel_search_type,
        search_kwargs = retrievel_args,
    )
    
    prompt_template = PromptTemplate.from_template(prompt)
    
    chat_chain = ConversationalRetrievalChain.from_llm(
        llm = chat,
        memory = memory,
        return_source_documents = True,
        retriever = retriever,
        verbose=True,
        combine_docs_chain_kwargs={"prompt": prompt_template},
    )
    return chat_chain