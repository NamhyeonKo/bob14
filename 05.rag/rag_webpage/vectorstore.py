import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma import Chroma

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

DATA_DIR = './DATA'
VECTOR_DB = './chroma_db'
COLLECTION_NAME = 'my-data'
store = None

load_dotenv()
os.makedirs(DATA_DIR, exist_ok=True)

def initialize_vector_db():
    global store
    if os.path.exists(VECTOR_DB):
        store = Chroma(collection_name=COLLECTION_NAME,
                       embedding_function=OpenAIEmbeddings(),
                       persist_directory=VECTOR_DB)
        
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def create_vector_db(file_path):
    global store

    loader = PyPDFLoader(file_path)
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()

    if store:
        store.add_documents(texts)
    else:
        store = Chroma.from_documents(
            texts,
            embedding=embeddings,
            collection_name=COLLECTION_NAME,
            persist_directory=VECTOR_DB
        )

    return store

def answer_question(question):
    global store
    if not store:
        initialize_vector_db()
        if not store:
            return "벡터 DB가 초기화되지 않았습니다. 먼저 파일을 업로드해주세요."
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
    
    template = """
    주어진 문서 내용을 바탕으로 질문에 답변해주세요.

    문서 내용: {context}

    질문 : {question}

    답변 작성 규칙:
    1. 명확하고 구체적으로 답변하세요.
    2. 기술적 내용은 실제 예제를 포함해서 답변하세요.
    3. 취약점 관련 내용은 대응방안도 함께 제시해주세요.
    4. 리스트 형태로 번호를 붙여 답변하고, 답변은 최대 3개 이하로 작성해주세요.
    5. 모르면 '모르겠습니다.'라고 답변하세요.
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    retriever = store.as_retriever(search_kwargs={"k": 5})
    
    chain = (
        {"context": retriever, "question": lambda x: x}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    try:
        response = chain.invoke(question)
        return response
    except Exception as e:
        return f"답변 생성 중 오류가 발생했습니다: {str(e)}"