import streamlit as st
from gera_config import load_config
from langchain.prompts.prompt import PromptTemplate

def inicializar_debug():
    st.header("🐞 Debug",divider=True)

def montando_prompt():
    config = load_config()
    prompt = config['DEFAULT']['prompt']
    prompt_template = PromptTemplate.from_template(prompt)
    return prompt_template

if __name__ == "__main__":
    inicializar_debug()
    if 'resposta' in st.session_state:
        if st.session_state['resposta'] is None or st.session_state['chain'] is None:
            st.error("Nenhuma resposta gerada!")
        else:
            prompt_template = montando_prompt()
            ultima_resposta = st.session_state['resposta']
            doc_list = ultima_resposta['source_documents']
            contexto_str = "\n\n".join([doc.page_content for doc in doc_list])
            chain = st.session_state['chain']
            memory = chain.memory
            chat_memory = memory.buffer_as_str
            with st.container(border=True):
                prompt = prompt_template.format(context=contexto_str,
                                                chat_history=chat_memory,
                                                question=ultima_resposta['question'])
                st.markdown(prompt)
    else:
        st.error("Nenhuma resposta gerada!")
        