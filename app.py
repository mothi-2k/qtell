import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import tempfile
import os

# Load environment variables (if needed)
load_dotenv()

st.title("RAG Application built on Gemini Model")

# File uploader for the PDF document (optional)
st.session_state.uploaded_file = st.file_uploader("Upload a PDF file (optional)", type="pdf")
if 'files' not in st.session_state:
    st.session_state.files = []
docs = []
vectorstore = None

if st.session_state.uploaded_file is not None and st.session_state.uploaded_file not in st.session_state.files:
    st.session_state.files.append(st.session_state.uploaded_file)
    print('new file uploaded')
    # Save the uploaded file to a temporary directory
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(st.session_state.uploaded_file.read())
        temp_file_path = temp_file.name
    
    # Load the PDF document using the temporary file path
    loader = PyPDFLoader(temp_file_path)
    data = loader.load()

    # Split the text into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
    docs = text_splitter.split_documents(data)
    # print(docs)

    # Set a persistent directory for ChromaDB storage
    persist_directory = "./chroma_storage"  # Ensure this path exists

    # Cache the vectorstore so it doesn't get re-initialized on every rerun
    @st.cache_resource
    def get_vectorstore():
        return Chroma(
            embedding_function=GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
            persist_directory=persist_directory
        )
        return Chroma.from_documents(
            documents=docs,
            embedding=GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
            persist_directory=persist_directory  # Use a persistent directory
        )

    # Get the cached vectorstore
    vectorstore = get_vectorstore()
    vectorstore.add_documents(docs)
    
    if 'retriever' not in st.session_state:
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10}) if vectorstore else None
        st.session_state.retriever = retriever

    # Clean up the temporary file
    os.remove(temp_file_path)
    # st.rerun()

# Create a retriever using the vectorstore if available
retriever = st.session_state.retriever if 'retriever' in st.session_state else None

# Initialize the Gemini model (Generative AI)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0, max_tokens=None, timeout=None)

# Define the system prompt template
system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question if a document is uploaded. If not, answer based on your general knowledge. "
    "If you don't know the answer, say that you don't know. Always include the page number and the file name in your response if relevant. "
    "Use markdown wherever necessary. Use five to eight sentences maximum and keep the answer concise.\n\n"
    "{context}\n\n"
    "Previous conversation:\n{history}\n"
)

# Define the chat prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

# Initialize the conversation history
if "history" not in st.session_state:
    st.session_state["history"] = []

# Streamlit chat input
query = st.chat_input("Ask a question about the uploaded PDF or anything else:")

if query:
    # Append the user question to the conversation history
    st.session_state["history"].append({"role": "user", "content": query})

    # Prepare the conversation history for the prompt
    history_context = "\n".join(f"{msg['role']}: {msg['content']}" for msg in st.session_state["history"][:-1])

    # If a retriever is available, use it to get context
    if retriever:
        # Create the document chain for question answering
        question_answer_chain = create_stuff_documents_chain(llm, prompt)

        # Create the RAG chain combining retrieval and question answering
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        # Invoke the chain to get the answer
        response = rag_chain.invoke({"input": query, "context": "", "history": history_context})

        # Get the answer from the AIMessage object
        answer = response.get('answer', 'Sorry, I couldn''t find an answer in the file.')
        # answer = response['answer'].content if hasattr(response, 'answer') else "Sorry, I couldn't find an answer in the file."
    else:
        # If no document is uploaded, still invoke the model for general knowledge
        formatted_prompt = prompt.format(input=query, context="", history=history_context)
        response = llm.invoke(formatted_prompt)
        # Get the answer from the AIMessage object
        answer = response.content if hasattr(response, 'content') else "Sorry, I couldn't find an answer by default."

    # Append the AI's answer to the conversation history
    st.session_state["history"].append({"role": "assistant", "content": answer})

# Display the conversation history as a chat-like interface
for message in st.session_state["history"]:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.write(message["content"])
