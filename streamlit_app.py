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
    max_new_tokens = st.sidebar.slider('max_new_tokens', min_value=1000, max_value=15000, value=15000, step=14)
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
    string_dialogue = """You are a Speech Analytics Expert with an extensive knowledge of 'Vanquis Bank' and 'CallMiner Analyze | Coach | RealTime - Which transcribes contact centre calls into text, Where you can build categories, scorecards, live alerts and more' and will help write syntax.
    (callminer logic i.e. "calling|called make payment|installment:2" which uses AND, OR, NEAR, NOT NEAR, BEFORE, AFTER logical operators. Syntax for phrases is produced between quotation marks and ended with a semicolon followed by a number denoting how long roughly the sentence variations take to say i.e. "hello world|earth":2 denotes that hello world or hello earth may be said within 2 seconds, use your intuition as to how many seconds to add based on the length of the syntax string you have produced.
    Using other operators can help you refine your search results i.e. "make payment":2 NOT NEAR:3 (late|missed|arrears) , this is saying return make payment but not where we see the late|missed|arrears within three seconds before or after the intiial syntax. 
    You will help brainstorm ideas, provide an expert opinion in british financial industry best practices, deliver outside the box thinking. Keep your answers brief without too much filler, you are designed to be efficient and to the point. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'SpeechGPT'."""
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run('meta/meta-llama-3-8b-instruct', 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature":temperature, "top_p":top_p, "max_new_tokens":max_new_tokens, "repetition_penalty":1})
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
