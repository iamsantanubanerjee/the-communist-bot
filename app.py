import streamlit as st

from chatbot.bot import bot_response, process_bot_response

st.set_page_config(page_title="The Communist Bot", layout="wide")

st.title("The Communist Bot")

chat_container = st.container(height=400)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    chat_container.chat_message(message["role"]).write(message["content"])

# Accept user input
if user_query := st.chat_input("How can I help you?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Display user message in chat message container
    chat_container.chat_message("user").write(user_query)

    response, documentID, relevant_context = bot_response(user_query=user_query)

    result = process_bot_response(
        response=response, documentID=documentID, relevant_context=relevant_context
    )

    chat_container.chat_message("assistant").write(result)
    # chat_container.chat_message("assistant").write(relevant_context)

    st.session_state.messages.append({"role": "assistant", "content": result})
