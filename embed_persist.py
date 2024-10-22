import traceback
import os
import tempfile
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv(override=True)

class EmbedDBError(Exception):
    pass

class EmbedPersist:
    def __init__(self, user_id):
        try:
            self.vectorstore = PGVector(
                embeddings=GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
                connection=f'postgresql://postgres.uvamvatffkoqvcghnsph:{os.getenv("DB_PASSWORD")}@aws-0-ap-south-1.pooler.supabase.com:6543/postgres',
                use_jsonb=True,
                collection_name=user_id
            )    
            self.retriever = self.vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})
        except Exception:
            traceback.print_exc()
            raise EmbedDBError
    
    def add_to_pg(self, uploaded_file):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name
            loader = PyPDFLoader(temp_file_path)  
            data = loader.load()
        
            # Split the text into manageable chunks
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
            docs = text_splitter.split_documents(data)    
            os.remove(temp_file_path) 
            self.vectorstore.add_documents(docs)
        except Exception:
            traceback.print_exc()
            raise EmbedDBError 
        
    def delete_from_pg(self):
        try:
            self.vectorstore.delete_collection()
        except Exception:
            traceback.print_exc()
            raise EmbedDBError         
        
    def get_retriever(self):
        return self.retriever