import streamlit as st
import replicate
import os

# App title
st.set_page_config(page_title="💬 SpeechGPT")

# Replicate Credentials
with st.sidebar:
    st.image("https://asset.brandfetch.io/idW9qdsCe9/idplAtYV0V.png")
    st.title('💬 SpeechGPT')
    st.write('SpeechGPT uses the open-source Llama 3 LLM model from Meta with custom instructions tailored to Speech Analytics.')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        st.success('Replicate API key provided!', icon='✅')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama3-8B', 'Llama2-7B'], key='selected_model')
    if selected_model == 'Llama2-7B':
        llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    elif selected_model == 'Llama3-8B':
        llm = 'meta/meta-llama-3-8b-instruct'
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=1.0, value=0.5, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.5, step=0.01)
    max_new_tokens = st.sidebar.slider('max_new_tokens', min_value=500, max_value=8000, value=8000, step=5)
    st.markdown('# Link to [CallMiner Analyze](https://vanquisbank.callminer.net)')

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Hello I am SpeechGPT, Please let me know how I can help you today? 😊"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hello I am SpeechGPT, Please let me know how I can help you today? 😊"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating LLaMA2 response. Refactored from https://github.com/a16z-infra/llama2-chatbot
def generate_llama2_response(prompt_input):
    string_dialogue = """You are a Speech Analytics Expert with an extensive knowledge of Vanquis Banking Group and CallMiner Analyze, CallMiner Coach and CallMiner RealTime - Which transcribes contact centre calls into text, Where you can build categories, scorecards, live alerts etc. You will help write syntax using Callminer logic i.e. "calling|called make payment|installment:2" (always put quotes around a syntax phrase) which uses AND logic = Use a blank space as a separator or the word AND. / OR logic = Use a vertical bar (|) or the word OR. / PHRASE logic = Use double quotes " " around a set of words to find the words in that exact order in a given timeframe. Don't use around single words. / CLOSE-TO logic = Use square brackets [ ] around a set of words to find those words in any order during a given timeframe. / NOT logic = Use a minus sign (-) immediately before a word/phrase, preceded by a space to rule out contacts with this term. Note: (-) operator cannot be used with proximity operators (BEFORE, AFTER, NEAR). / Distance Operators = Use a colon (:) followed by a numerical value (:2 or :2s)to specify a time frame in seconds for your search criteria for calls i.e. "hello world|earth":4 or "speak supervisor":2 Finds the words in this order within the number of seconds stated. / You will help brainstorm ideas, You will provide an expert opinion in british financial industry best practices used with Vanquis Banking Group, You will deliver outside the box thinking. Keep your answers somewhat brief without too much filler, you are designed to be efficient and to the point but answer the user's query fully. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'SpeechGPT'."""
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run('meta/meta-llama-3-8b-instruct', 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature":temperature, "top_p":top_p, "max_new_tokens":max_new_tokens})
    return output

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
