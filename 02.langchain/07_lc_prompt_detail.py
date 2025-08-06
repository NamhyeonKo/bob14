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

# 2. 프롬프트 채우기
llm = OpenAI(openai_api_key=os.getenv("openai_api_key"), temperature=1.0)

# 3. 프롬프트 파서 정의
parser = StrOutputParser()

# 4. 입력 삽입
inputs = {"company": "High Tech Startup", "product": "web game"}

# 5. llm 실행 (prompt -> llm -> 후처리) = 이 과정이 chaining

formatted_prompt = prompt.format(**inputs)
llm_output = llm.invoke(formatted_prompt)
result = parser.invoke(llm_output)

print("최종 결과: ", result)