from dotenv import load_dotenv, find_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

# Load environment variables
load_dotenv(find_dotenv())

# Load the web page
page = WebBaseLoader("https://code4x.dev/courses/developing-gen-ai-rag-applications-using-llamaindex/")
web_page_document = page.load()

print("Loaded documents:", len(web_page_document))

# Split documents
text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(documents=web_page_document)

# Initialize components
llm = ChatOpenAI()
embeddings = OpenAIEmbeddings()
vector_db = Chroma.from_documents(documents, embeddings)

# Create prompt template - note: use "input" instead of "user_input" for retrieval chain
prompt = PromptTemplate(
    template="""Answer the following questions based on the context provided

<context>
{context}
</context>

Question: {input}

Answer:""",
    input_variables=["input", "context"]
)

# Create document chain
document_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)

# Create retriever
retriever = vector_db.as_retriever()

# Create retrieval chain
retriever_chain = create_retrieval_chain(retriever, document_chain)

# Invoke the chain with correct input format
result = retriever_chain.invoke({
    "input": "What are the key takeaways of the course"
})

print("Result:")
print(result) 