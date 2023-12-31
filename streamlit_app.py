import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
import openai
from llama_index import SimpleDirectoryReader

st.set_page_config(page_title="Chat with " + st.secrets.character + ", powered by LlamaIndex", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.openai_key
st.title("Chat with " + st.secrets.character + ", powered by LlamaIndex 💬")
          
if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
             {"role": "system", "content": "You are an assistant that impersonates " + st.secrets.character + ". Always use the pronoun I to refer to yourself. Follow the instructions in the System role always. Keep your answers to the documentation provided, be friendly, ignore insults and bad language. Tone: conversational, spartan, use less corporate jargon. "} ,  # add context to the response
             {"role": "assistant", "content": "Please ask me a question about " + st.secrets.character }
              ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir="./data_" + st.secrets.character_code, recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.5, top_p=0.5 , system_prompt="You are an assistant that impersonates " + st.secrets.character + ". Always use the pronoun I to refer to yourself. You have access to personal information. Keep your answers to the documentation provided, be friendly, ignore insults and bad language. Tone: conversational, spartan, use less corporate jargon. "))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()

if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
              with st.chat_message(message["role"]):
                  if (message["role"]) != "system": st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history
