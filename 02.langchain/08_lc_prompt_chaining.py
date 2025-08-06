from dotenv import load_dotenv

from langchain.prompts import PromptTemplate

from langchain_openai import OpenAI
from langchain_core.output_parsers import StrOutputParser

import os
load_dotenv()

# 1. 프롬프트 템플릿 정의
template = "You are a naming consultant for new companies. What is a good name for a {company} that makes {product}?"

prompt = PromptTemplate(
    input_variables=["company", "product"],
    template=template
)

# 2. 모델 생성
llm = OpenAI(temperature=1.0, openai_api_key=os.getenv("openai_api_key"))

# 3. 프롬프트 파서 정의
parser = StrOutputParser()

# LLM 실행 (prompt -> llm -> 후처리) = 이 과정이 chaining
# 4. chain 파이프 라인 생성
chain = prompt | llm | parser # 이 문법을 LCEL(LangChain Expression Language)

# 5. 입력 삽입
inputs = {"company": "High Tech Startup", "product": "web game"}

result = chain.invoke(inputs)

print("최종 결과: ", result)