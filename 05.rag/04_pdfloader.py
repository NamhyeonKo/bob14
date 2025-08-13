from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
# pip install pypdf

load_dotenv()

pdf_filename = './DATA/Python_시큐어코딩_가이드(2023년_개정본).pdf'
PERSIST_DIRECTORY = './chroma_db'
COLLECTION_NAME = 'secure_coding'

loader = PyPDFLoader(pdf_filename)
pages = loader.load()

# print(f"총 페이지수: {len(pages)}")
# print(f"1페이지 내용 샘플\n{pages[1].page_content}")
# print(f"1페이지 메타데이터 샘플\n{pages[1].metadata}")

def create_vector_db():
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n\n",
        chunk_size=2000,
        chunk_overlap=500
    )
    text = text_splitter.split_documents(pages)
    embeddings = OpenAIEmbeddings()
    store = Chroma.from_documents(text, embeddings,
                                collection_name=COLLECTION_NAME,
                                persist_directory=PERSIST_DIRECTORY
                                )
    return store

# print(text[:10])
def load_vector_db():
    embeddings = OpenAIEmbeddings()
    store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=PERSIST_DIRECTORY
    )
    return store

# import os
# if os.path.exists(PERSIST_DIRECTORY):
#     print("기존 DB 로드")
#     store = load_vector_db()
# else:
#     print("새로운 DB 생성")
#     store = create_vector_db()

def check_collection_exists(persist_dir, collection_name):
    embeddings = OpenAIEmbeddings()
    store = Chroma(collection_name=collection_name,
                   embedding_function=embeddings, persist_directory=persist_dir)
    results = store.get(limit=1)
    print(f"쿼리 답변 길이 확인: {len(results['ids'])}")

    return bool(results['ids'])

if check_collection_exists(PERSIST_DIRECTORY, COLLECTION_NAME):
    print(f"기존 데이터베이스를 로딩합니다. 컬렉션명 : {COLLECTION_NAME}")
    store = load_vector_db()
else:
    print("새로운 DB 생성")
    store = create_vector_db()

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
"""

# 위에는 프롬프트 엔지니어링 기법 중 OutPut format specification 방법으로, 출력 형태를 지정하는 방식.

prompt = ChatPromptTemplate.from_template(template)

retriever = store.as_retriever(search_kwargs={"k": 5}) # 유사 문서 5개 반환

chain = (
    {"context": retriever, "question": lambda x: x}
    | prompt
    | llm
    | StrOutputParser()
)

def answer_question(question):
    response = chain.invoke(question)
    print(f"-------시작-------")
    print(f"\n질문: {question}")
    print(f"\n답변: {response}\n")
    print(f"-------끝-------")

answer_question("웹 취약점에 대해서 알려줘")