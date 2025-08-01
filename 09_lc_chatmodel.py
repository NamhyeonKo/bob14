from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import os

load_dotenv()

# 1. 프롬프트 템플릿 생성
# [오류 수정] 집합({ })이 아닌 튜플(( )) 형태로 메시지를 전달해야 합니다.
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a naming consultant for new companies."),
    ("human", "What is a good name for a {company} that makes {product}?")
])

# 2. chat 모델 생성
llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=os.getenv("openai_api_key"), temperature=1.0)

# 3. 후처리 파서 생성
parser = StrOutputParser()

# 6. 신버전 LCEL 방식
chain = prompt | llm | parser  # LCEL을 사용하여 파이프라인 생성

# 4. 입력값 정의
inputs = {"company": "High Tech Startup", "product": "web game"}

# # 5. 프롬프트 생성 및 모델 실행
# messages = prompt.format_messages(**inputs)
# response = llm.invoke(messages)
# final_output = parser.invoke(response)

# 7. chain 실행
final_output = chain.invoke(inputs)

print("최종 결과: ", final_output)