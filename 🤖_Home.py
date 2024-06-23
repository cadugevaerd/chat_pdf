import streamlit as st
import utils
import time
from gera_config import *

def estrutura_inicial_principal():
    st.header("🤖 Chat PDF", divider=True)


def estrutura_inicial_sidebar():
    file = st.file_uploader("Selecione um arquivo PDF", type=[".pdf"], accept_multiple_files=True)
    if len(file) > 0:
        st.session_state['carregado'] = True
    else:
        st.session_state['carregado'] = False
        st.session_state['chain'] = None
    #st.write(st.session_state['carregado'])
    #st.write(st.session_state['chain'])
    if st.session_state['chain'] is not None:
        btn_atualizar = st.button("Atualizar ChatBOT",use_container_width=True)
    else:
        btn_atualizar = st.button("Iniciar ChatBOT",use_container_width=True)
        
    return file, btn_atualizar


def inicializar():
    status = valida_config()
    if status:
        time.sleep(1)
        st.rerun()
    else:
        if "primeira_vez" not in st.session_state:
            st.session_state['primeira_vez'] = True
        config = load_config()
        api_key = config['GPT']['key']
        st.session_state['key'] = api_key
        if st.session_state['primeira_vez']:
            if st.session_state['key'] == "":
                st.session_state['primeira_vez'] = False
            else:
                if st.session_state['key'] != "":
                    limpar_gpt()
                    st.session_state['primeira_vez'] = False
                    st.session_state['resposta'] = None
                    st.session_state['chain'] = None
                    st.rerun()
        if api_key == "" or api_key is None:
            st.error("Nenhuma API Key fornecida, acesse a aba de configuração e defina sua chave de API do Chat GPT.")
            st.stop()
    if 'chain' not in st.session_state:
        st.session_state['chain'] = None
    if 'carregado' not in st.session_state:
        st.session_state['carregado'] = False
    if 'paginas' not in st.session_state:
        st.session_state['paginas'] = []
    if 'memory' not in st.session_state:
        st.session_state['memory'] = None
    if 'resposta' not in st.session_state:
        st.session_state['resposta'] = None
        #memory = ConversationBufferMemory(return_messages=True)
        #memory.chat_memory.add_user_message("Oi")
        #memory.chat_memory.add_ai_message("Ola, eu sou uma LLM")
        
        #st.session_state['memory'] = memory

def trata_chat(input):
    if st.session_state['chain'] is None:
        st.error("Nenhum PDF carregado!")
        st.session_state['carregado'] = False
        st.session_state['paginas'] = []
        st.session_state['resposta'] = None
    else:
        chain = st.session_state['chain']
        memory = chain.memory
        mensagens = memory.load_memory_variables({})['chat_history']
        for mensagem in mensagens:
            chat = st.chat_message(mensagem.type)
            chat.markdown(mensagem.content)

        if input:
            chat_human = st.chat_message("human")
            chat_human.markdown(input)
            with st.spinner("Carregando..."):
                resposta = chain.invoke({"question": input})
                st.session_state['resposta'] = resposta
                st.rerun()

def cria_input():
    input_chat = st.chat_input("Converse com o seu PDF:")
    return input_chat
def main():
    try:
        inicializar()
        api_key = st.session_state['key']
        if api_key == "" or api_key is None:
            st.error("Nenhuma API Key fornecida! Acesse a aba de configuração e defina sua chave de API do Chat GPT.")
            st.stop()
        with st.sidebar:
            files, atualizar_btn = estrutura_inicial_sidebar()
            if atualizar_btn:
                if len(files) > 0:
                    with st.status("Carregando...", expanded=True) as status:
                        chat = utils.cria_chain_chat(files,api_key)
                        st.session_state['chain'] = chat
                        status.update(label="Carregado!", state="complete", expanded=False)
                else:
                    st.session_state['chain'] = None
        estrutura_inicial_principal()
        if st.session_state['chain'] is not None and st.session_state['carregado']:
            input = cria_input()
            trata_chat(input)
        else:
            st.error("Nenhum PDF carregado!")
    except Exception as e:
        st.error(e)
    

if __name__ == "__main__":
    main()