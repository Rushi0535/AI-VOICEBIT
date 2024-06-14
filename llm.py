import re
from langchain_community.llms import Ollama
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.document_loaders import PyPDFDirectoryLoader
import os

DB_PATH='vectorstore/db/'
DATA_PATH='knowledge_base/'
MODEL="gemma:2b"
EMBEDDINGS = MODEL

def create_vector_db():
    try:
        if not os.path.exists(DB_PATH):
            loader = PyPDFDirectoryLoader(DATA_PATH)
            documents = loader.load()
            print(f"Processed {len(documents)} pdf files")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
            texts = text_splitter.split_documents(documents)
            vectorstore = FAISS.from_documents(texts, OllamaEmbeddings(model=EMBEDDINGS))
            vectorstore.save_local(DB_PATH)
            print(f'There was no database hence vector database created: {DB_PATH}')
    except Exception as e:
        print(f"Error creating vector database: {e}")

def chat(question):
    print("LLM Initiated")
    create_vector_db()
    llm = Ollama(model=MODEL)
    vector_db = FAISS.load_local(DB_PATH, OllamaEmbeddings(model=EMBEDDINGS), allow_dangerous_deserialization=True)
    vector_store = vector_db.as_retriever()

    prompt = ChatPromptTemplate.from_template("""
                                          [INST]
                                          Please answer the following question based solely on the provided knowledge.
                                      
                                            
                                          <knowledge>
                                          {context}
                                          </knowledge>

                                          Question: {input}
                                          [/INST]
                                            """)

    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(vector_store, document_chain)
    response = retrieval_chain.invoke({"input": question})
    
    # Clean up the response by removing all special characters except for periods and commas
    clean_response = re.sub(r'[^A-Za-z0-9\s.,:;]', '', response["answer"])
    
    return clean_response

# # Example usage for debugging
# if __name__ == "__main__":
#     response = chat("What is Silver Oak University?")
#     print(response)
