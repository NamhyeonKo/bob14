from dotenv import load_dotenv
import os   

from langchain_core.prompts import PromptTemplate

from langchain_openai import OpenAI
from langchain_core.runnables import RunnableLambda

load_dotenv()

template = "다음 요청을 보고 SQL 쿼리를 작성해주세요. \n\n{query}"
prompt = PromptTemplate(input_variables=["query"], template=template)
llm = OpenAI(openai_api_key=os.getenv("openai_api_key"), temperature=0.6, max_tokens=1024)

chain = prompt | llm | RunnableLambda(lambda x: {"sql": x.strip()})

input_text = {
    "query": """
학생 테이블과 교과목 테이블 그리고 성적 테이블을 참조해서 점수가 90점 이상인 학생의 이름과 해당 교과목의 이름을 출력하는 SQL 쿼리를 작성해주세요.
    """
}

result = chain.invoke(input_text)
print("SQL 쿼리 결과: ", result['sql'])