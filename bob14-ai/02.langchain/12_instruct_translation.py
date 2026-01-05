from dotenv import load_dotenv
import os   

from langchain_core.prompts import PromptTemplate

from langchain_openai import OpenAI
from langchain_core.runnables import RunnableLambda

load_dotenv()

template = "다음 영어 문장을 보고 한국어로 번역해주세요. \n\n{sentence}"
prompt = PromptTemplate(input_variables=["sentence"], template=template)
llm = OpenAI(openai_api_key=os.getenv("openai_api_key"), temperature=0.4, max_tokens=1024)

chain = prompt | llm | RunnableLambda(lambda x: {"translation": x.strip()})

input_text = {
    "sentence": """
The President will go on summer vacation next week.
Age is no guarantee of maturity.
    """
}

result = chain.invoke(input_text)
print("요약 결과: ", result['translation'])