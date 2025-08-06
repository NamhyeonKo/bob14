from langchain_core.prompts import PromptTemplate

# 1. 프롬프트 템플릿 정의
templete = "당신은 이름을 짓는 작명가입니다. 다음 상품을 만드는 회사명을 적어주세요 \n 상품: {product}"

prompt = PromptTemplate(
    input_variables=["product"],
    template=templete
)

filled_prompt = prompt.format(product="아이스크림")
print("프롬프트 결과 : ",filled_prompt)

test_products = [
    "모바일 게임",
    "컴퓨터 게임",
    "로봇 장난감",
    "에코백",
    "자전거"
]

# LLM 모델 초기화
from langchain_openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
llm = OpenAI(model="gpt-3.5-turbo", openai_api_key=os.getenv("openai_api_key"), temperature=1.0)

for product in test_products:
    result = llm.invoke(final_prompt := prompt.format(product=product))
    # result = llm.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "user", "content": prompt.format(product=product)}
    #     ]
    # )
    print(f"{product} : ", result)