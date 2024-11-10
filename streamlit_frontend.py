import streamlit as st
import requests
import json

API_URL = "http://fastapi:8000"  # Use the service name when running in Docker
# API_URL = "http://localhost:8000"  # Use this for local development

st.title("Biology Text RAG System")

# Sidebar for upload
with st.sidebar:
    st.header("Document Upload")
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    
    if uploaded_file:
        if st.button("Process Document"):
            with st.spinner("Processing document... This may take a few minutes..."):
                files = {"file": uploaded_file}
                response = requests.post(f"{API_URL}/upload", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    if result["status"] == "success":
                        st.success(f"""Document processed successfully!
                        - PGVector documents: {result['documents_written']['pgvector']}
                        - Elasticsearch documents: {result['documents_written']['elasticsearch']}
                        """)
                    else:
                        st.error(f"Error: {result['message']}")

# Main chat interface
st.header("Chat Interface")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about the biology text"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Generating response... This may take a few moments..."):
            response = requests.post(
                f"{API_URL}/query",
                json={"text": prompt}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(result)
                answer = result["answer"]
                usage = result["usage"]
                
                st.markdown(answer)
                with st.expander("Token Usage"):
                    st.json(usage)
                
                # Add assistant response to chat history
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            else:
                st.error("Failed to get response from the API")