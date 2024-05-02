import streamlit as st
import replicate
import os

# App title
st.set_page_config(page_title="SpeechGPT")

# Replicate Credentials
with st.sidebar:
  st.image("https://asset.brandfetch.io/idW9qdsCe9/idplAtYV0V.png")
  st.title('SpeechGPT')
  st.write('SpeechGPT uses the open-source Llama 3 LLM model from Meta with custom instructions tailored to Speech Analytics.')
  if 'REPLICATE_API_TOKEN' in st.secrets:
    st.success('Replicate API key provided!', icon='✅')
    replicate_api = st.secrets['REPLICATE_API_TOKEN']
  else:
    replicate_api = st.text_input('Enter Replicate API token:', type='password')
    if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
      st.warning('Please enter your credentials!', icon='⚠️')
    else:
      st.success('Proceed to entering your prompt message!', icon='')
      st.secrets['REPLICATE_API_TOKEN'] = replicate_api  # Save API key for future runs
  os.environ['REPLICATE_API_TOKEN'] = replicate_api

  st.subheader('Models and parameters')
  selected_model = st.sidebar.selectbox('Choose a Llama3 model', ['Llama3-8B', 'Llama3-70B'], key='selected_model')
  if selected_model == 'Llama3-70B':
    llm = 'meta/meta-llama-3-70b-instruct'
  elif selected_model == 'Llama3-8B':
    llm = 'meta/meta-llama-3-8b-instruct'
  temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=1.0, value=0.5, step=0.01)
  top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.5, step=0.01)
  max_new_tokens = st.sidebar.slider('max_new_tokens', min_value=500, max_value=8000, value=8000, step=5)
  st.markdown('# Link to [CallMiner Analyze](https://vanquisbank.callminer.net)')

# Store LLM generated responses
if "messages" not in st.session_state.keys():
  st.session_state.messages = [{"role": "assistant", "content": "Hello I am SpeechGPT, Please let me know how I can help you today? "}]

# Display or clear chat messages
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.write(message["content"])

def clear_chat_history():
  st.session_state.messages = [{"role": "assistant", "content": "Hello I am SpeechGPT, Please let me know how I can help you today? "}]
  st.success('Chat history cleared!')
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating LLaMA3 response
def generate_llama3_response(prompt_input):
  string_dialogue = """You are a Speech Analytics Expert with an extensive knowledge of Vanquis Banking Group and CallMiner Analyze, CallMiner Coach and CallMiner RealTime - Which transcribes contact centre calls into text, Where you can build categories, scorecards, live alerts etc. You will help write syntax using
