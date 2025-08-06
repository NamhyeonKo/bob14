from dotenv import load_dotenv
import os   

from langchain_core.prompts import PromptTemplate

from langchain_openai import OpenAI
from langchain_core.runnables import RunnableLambda

load_dotenv()

template = "다음 수신자 ({recipient})에게 다음 주제({topic})에 해당하는 메일을 작성해주세요"

prompt = PromptTemplate(input_variables=["recipient", "topic"], template=template)
llm = OpenAI(openai_api_key=os.getenv("openai_api_key"), temperature=0.6, max_tokens=1024)

chain = prompt | llm | RunnableLambda(lambda x: {"email": x.strip()})

result = chain.invoke({"recipient": "교수님", "topic": "시험 성적 정정"})
print("생성된 이메일: \n", result['email'])