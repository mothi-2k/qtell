from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
import traceback

class BotError(Exception):
    pass

class QtellBot:
    def __init__(self, retriever):
        try:
            load_dotenv(override=True)        
            self.retriever = retriever
            self.history = []

            self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0, max_tokens=None, timeout=None)
            self.system_prompt = (
                "You are an assistant for question-answering tasks. "
                "Use the following pieces of retrieved context to answer "
                "the question if a document is uploaded. If not, answer based on your general knowledge. "
                "If you don't know the answer, say that you don't know. Always include the page number and the file name in your response if relevant. "
                "Don't use markdown. Use five to eight sentences maximum and keep the answer concise.\n\n"
                "{context}\n\n"
                "Previous conversation:\n{history}\n"
            )
            self.prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", self.system_prompt),
                    ("human", "{input}"),
                ]
            )
            self.question_answer_chain = create_stuff_documents_chain(self.llm, self.prompt)
            self.rag_chain = create_retrieval_chain(self.retriever, self.question_answer_chain)
        except Exception:
            traceback.print_exc()
            raise BotError

    def ask_question(self, query, history):
        try:
            history_context = "\n".join(f"user: {msg['chat']['user']}\nassistant': {msg['chat']['bot']}" for msg in history)
            if self.retriever:
                response = self.rag_chain.invoke({"input": query, "context": "", "history": history_context})
                answer = response.get('answer', 'Sorry, I couldn\'t find an answer in the file.')
            else:
                formatted_prompt = self.prompt.format(input=query, context="", history=history_context)
                response = self.llm.invoke(formatted_prompt)
                answer = response.content if hasattr(response, 'content') else "Sorry, I couldn't find an answer by default."
            return answer
        except Exception:
            traceback.print_exc()
            raise BotError()

