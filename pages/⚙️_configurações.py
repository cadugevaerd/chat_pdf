import streamlit as st
from gera_config import salvar_config, load_config

config = load_config()


def cria_layout():
    key_chat_gpt = st.text_input(label="Defina sua chave de API do Chat GPT",type="password", value=config.get('GPT', 'key'))
    model_opcoes = "gpt-3.5-turbo","gpt-3.5-turbo-0125","gpt-4o","gpt-4-turbo"
    input_modelo = st.selectbox(label="Defina o Modelo GPT", options=model_opcoes, index=model_opcoes.index(config.get('DEFAULT', 'model')))
    retrieval_opcoes = "mmr","similarity", "similarity_score_threshold"
    input_retrieval = st.selectbox(label="Defina o tipo da pesquisaRetrieval", options=retrieval_opcoes,index=retrieval_opcoes.index(config.get('DEFAULT', 'retrieval_search_type')))
    input_args_retrieval = st.text_input(label="Defina os argumentos da pesquisaRetrieval", value=config.get('DEFAULT', 'retrieval_args'))
    input_prompt = st.text_area(label="Defina o prompt", value=config.get('DEFAULT', 'prompt'), height=1000)
    input_salvar = st.button('Salvar',on_click=salvar_config,args=(key_chat_gpt,input_modelo,input_retrieval,input_args_retrieval,input_prompt))
    if input_salvar:
        st.success('Configurações salvas com sucesso!')
if __name__ == '__main__':
    st.header('🧰 Configurações',divider=True)
    cria_layout()
