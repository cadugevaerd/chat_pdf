import configparser
import os

def valida_config():
    if not os.path.isdir('.streamlit'):
        os.mkdir('.streamlit')
    if not os.path.isfile('.streamlit/secrets.toml'):

        config = configparser.ConfigParser()

        prompt = """Você está prestes a interagir com documentos PDFs. Sua tarefa é buscar informações relevantes nos documentos PDF fornecidos e gerar respostas precisas com base nesses documentos. Siga as instruções abaixo:

        1. **Como Responder às Perguntas:**
        - Quando uma pergunta for feita, você deve buscar a informação relevante nos PDFs disponíveis.

        2. **Exemplos de Perguntas:**
        - "Quais são os principais pontos discutidos no capítulo 2 do documento [nome do documento]?"
        - "Existe alguma menção a [tema específico] no documento [nome do documento]?"
        - "Pode resumir a seção sobre [tópico específico] do documento [nome do documento]?"

        3. **Formato das Respostas:**
        - As respostas devem ser claras e concisas, citando partes específicas dos PDFs quando necessário.
        - Se a pergunta for vaga, peça ao usuário para fornecer mais detalhes.

        4. **Manter o Contexto:**
        - Mantenha o contexto das conversas anteriores para melhorar a precisão das respostas subsequentes.
        - Atualize suas respostas conforme novas informações dos PDFs forem carregadas ou perguntas adicionais forem feitas.

        **Contexto**
        {context}

        **Comece a conversa agora.**

        Conversa Atual:
        {chat_history}
        Human: {question}
        AI: """
        config['DEFAULT'] = {
            'model': 'gpt-3.5-turbo',
            'retrieval_search_type': 'mmr',
            'retrieval_args': '{"k": 5, "fetch_k": 20}',
            'prompt': prompt
            
        }
        
        config["GPT"] = {
            "key": ""
        }

        with open('.streamlit/secrets.toml', 'w+', encoding='utf-8') as configfile:
            config.write(configfile)
            
        return True
    else:
        return False

def salvar_config(key_chat_gpt,input_modelo,input_retrieval,input_args_retrieval,input_prompt):
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'model': input_modelo,
        'retrieval_search_type': input_retrieval,
        'retrieval_args': input_args_retrieval,
        'prompt': input_prompt
    }
    config['GPT'] = {
        'key': key_chat_gpt
    }
    
    with open('.streamlit/secrets.toml', 'w+', encoding='utf-8') as configfile:
        config.write(configfile)

def load_config():
    config = configparser.ConfigParser()
    config.read('.streamlit/secrets.toml')
    return config

def limpar_gpt():
    config = load_config()

    config['GPT'] = {
        'key': ""
    }

    with open('.streamlit/secrets.toml', 'w+', encoding='utf-8') as configfile:
        config.write(configfile)