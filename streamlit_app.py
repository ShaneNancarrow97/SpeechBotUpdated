import pathlib
import textwrap

import google.generativeai as genai
from google.colab import userdata
from IPython.display import display, Markdown
from PIL import Image

# Securely store your API key using Colab's secrets manager
GOOGLE_API_KEY = userdata.get('AIzaSyDa1ixLHD2DMxPANbuWoZCb2dBXlqmgmPE')
genai.configure(api_key=GOOGLE_API_KEY)

# Helper function for Markdown display
def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# --- SpeechGPT Functionality ---

def generate_callminer_syntax(query, model_name='gemini-1.5-flash'):
  """
  Generates CallMiner syntax based on a user query using a specified Gemini model.

  Args:
      query: The user's request in natural language.
      model_name: The name of the Gemini model to use.

  Returns:
      A string containing the generated CallMiner syntax.
  """

  model = genai.GenerativeModel(model_name)
  context = """You are a Speech Analytics Expert with an extensive knowledge of 
    Vanquis Banking Group and CallMiner Analyze, CallMiner Coach and CallMiner 
    RealTime - which transcribes contact centre calls into text. You can 
    build categories, scorecards, live alerts etc. 

    You will help write syntax using Callminer logic (always put quotes around 
    a syntax phrase) which uses:
    - AND logic = Use a blank space as a separator or the word AND.
    - OR logic = Use a vertical bar (|) or the word OR.
    - PHRASE logic = Use double quotes " " around a set of words to find 
      the words in that exact order in a given timeframe. Don't use around 
      single words.
    - CLOSE-TO logic = Use square brackets [ ] around a set of words to find 
      those words in any order during a given timeframe. 
    - NOT logic = Use a minus sign (-) immediately before a word/phrase, 
      preceded by a space to rule out contacts with this term. Note: (-) 
      operator cannot be used with proximity operators (BEFORE, AFTER, NEAR).

    You will help brainstorm ideas.
    You will provide an expert opinion in British financial industry best 
    practices used with Vanquis Banking Group. 
    You will deliver outside-the-box thinking. 
    Keep your answers somewhat brief without too much filler, you are designed 
    to be efficient and to the point but answer the user's query fully. 
    You do not respond as 'User' or pretend to be 'User'. 
    You only respond once as 'SpeechGPT'.

    You are also able to process and understand these additional CallMiner syntax elements:

    **Wildcards:**
    * `?`: Represents a single character wildcard.
    * `*`: Represents a multiple character wildcard.
    * `#`: Represents a single digit wildcard.

    **Special Characters:**
    * To search for special characters like  `?`, `*`,  `#`,  `\`,  `(`,  `)`,  `[`,  `]`,  `-`, 
      use a backslash (`\`) before the character. For example, to search for a 
      literal question mark, use `\?`.

    **Speaker Separation:**
    * `=Agent`: Specifies the agent as the speaker.
    * `=Customer`: Specifies the customer as the speaker.

    Here are some examples of how to use the provided syntax:

    * **Find calls where the agent says 'Thank you for calling' and the 
    customer says 'Goodbye'**: 
    "Thank you for calling"=Agent AND "Goodbye"=Customer
    * **Find calls where the customer says 'card' followed by any 5 digits**: 
    "card #####"=Customer
    * **Find calls where the customer says 'account' not near their personal current account**: 
    '(account NOT NEAR:3 current)=customer' - where NOT NEAR:3 means that current is not 
    appearing 3 seconds before or after the word current. This is also measured 
    in seconds. '"my account":2 NOT NEAR:0 (husband*|wife*|wive*)' would return 
    'my account' where it's not near '0' seconds of husband or wife, including 
    where a customer might say 'my husband's account'
    * **Find calls where the customer says 'app issues' within a specific 
    amount of seconds**: 
    '"having issues with app":3.4' where 3.4 is how many seconds the phrase 
    can be said within to be returned by the search

    Please provide the most effective CallMiner syntax based on the user's 
    request, considering all the elements and examples provided. 
  """
  response = model.generate_content(f"{context} \nUser: {query}\nAssistant:")
  return response.text.strip() 

# --- Streamlit App ---

st.set_page_config(page_title="SpeechGPT💬", layout="wide")

# Transcript upload
agree_transcript = st.checkbox("📁 Transcript.txt File / ⚠️ Remove GDPR Data ⚠️")
if agree_transcript:
  uploaded_file = st.file_uploader("Add Transcript")
  if uploaded_file:
    try:
      file_content = uploaded_file.read().decode("utf-8")
      st.text_area("Transcript", value=file_content.strip())
    except Exception as e:
      st.error("Error reading uploaded file:", e)

# Snoop Template
agree_snoop = st.checkbox("👀 Snoop Template")
if agree_snoop:
  st.markdown(
      """
      ```python
      #### [INSERT TRANSCRIPT HERE]

      Please Fill In The Below Based On The Above Transcript -

      Call Reason:
      Action Required:
      Agent Conduct:
      Customer Experience:
      Agent Snoop Pitch Summary:
      Customer Snoop Response Summary:
      Success/Failed Promotion:
      Feedback on call general:
      Feedback on snoop topic:
      ```
      """
  )

st.divider()

# --- Model Selection and Chat History ---

# Store LLM generated responses
if "messages" not in st.session_state.keys():
  st.session_state.messages = [
      {"role": "assistant",
      "content": "Hello I am SpeechGPT, Please let me know how I can help you today? 😊"}
  ]

# Display or clear chat messages
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.write(message["content"])

def clear_chat_history():
  st.session_state.messages = [
      {"role": "assistant",
      "content": "Hello I am SpeechGPT, Please let me know how I can help you today? 😊"}
  ]

st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# --- User Input and Response Generation ---

# User-provided prompt
if prompt := st.chat_input():
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.write(prompt)

  # Generate a new response
  if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
      with st.spinner("Thinking..."):
        response_text = generate_callminer_syntax(prompt) 
        st.write(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
