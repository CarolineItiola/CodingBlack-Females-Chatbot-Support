import streamlit as st
from chatbot import get_response

st.title("Coding Black Females Support")
st.write("Ask about membership, events or the bootcamps.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Type your question..."):
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )
    with st.chat_message("user"):
        st.write(prompt)

    result = get_response(prompt)

    with st.chat_message("assistant"):
        if result:
            st.write(result["response_text"])
            if result["needs_human"]:
                st.warning("Passed to a human for follow up.")
            st.session_state.messages.append(
                {"role": "assistant",
                 "content": result["response_text"]}
            )
        else:
            st.error("Something went wrong. Please try again.")
