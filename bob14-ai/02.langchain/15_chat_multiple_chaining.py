from dotenv import load_dotenv
import os

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.runnables import RunnableLambda

load_dotenv()

# 목적
# chain1: 요리사 역할 프롬프트
# chain2: 다국어 번역 프롬프트
# chain3: 번역 결과를 CSV 형태로 파싱하는 프롬프트

# 1-1. 요리사 역할 프롬프트 정의
prompt1 = ChatPromptTemplate.from_template(
    "당신은 요리사입니다. 다음 질문에 답변하시오. \n\n {input}"
)

# 1-2. 모델 생성
llm = ChatOpenAI(openai_api_key=os.getenv("openai_api_key"), model="gpt-3.5-turbo", temperature=0.5)

# 1-3. 체인 구성
chain1 = prompt1 | llm | RunnableLambda(lambda x: {"response": x.content.strip()})

# 1-4. 실행
print("\n[체인1 실행 결과]\n")
print(chain1.invoke({"input": "김치는 어떻게 만드나요?"})["response"])

# 2-1. 번역 프롬프트 실행
translation_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("당신은 번역 전문가입니다. 주어진 문장을 보고 {input_language}에서 {output_language}로 번역해주세요."),
    HumanMessagePromptTemplate.from_template("다음 문장을 번역해주세요.\n\n {text}")
])


# 2-2. 체인 구성
chain2 = translation_prompt | llm | RunnableLambda(lambda x: {"response": x.content.strip()})

# 2-3. 체인3으로 보내서 CSV로 처리
chain3 = translation_prompt | llm | CommaSeparatedListOutputParser()

# 2-4. 실행
inputs = {
    "input_language":"영어",
    "output_language": "한국어",
    "text": "Hello, Nice to meet you."
}

print("\n[Chain2 실행]\n")
print(chain2.invoke(inputs)["response"])

print("\n[Chain3 실행]\n")
print(chain3.invoke(inputs))