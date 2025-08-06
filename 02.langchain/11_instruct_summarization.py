from dotenv import load_dotenv
import os   

from langchain_core.prompts import PromptTemplate

from langchain_openai import OpenAI
from langchain_core.runnables import RunnableLambda

load_dotenv()

template = "다음 문장을 요약해주세요: \n\n{article}"
prompt = PromptTemplate(input_variables=["article"], template=template)
llm = OpenAI(openai_api_key=os.getenv("openai_api_key"), temperature=0.4, max_tokens=1024)

chain = prompt | llm | RunnableLambda(lambda x: {"summary": x.strip()})

input_text = {
    "article": """
이 대통령은 다음 주 하계휴가에 들어갑니다.

최재민 기자의 보돕니다.

[기자]
취임 후 두 달 만에 처음으로 17개 시도지사를 만난 이 대통령의 첫 일성은 지역의 균형 발전이었습니다.

[이재명 / 대통령 : 새로운 정부는 대한민국의 지속적인 성장 발전을 위해서 균형 발전이 지역에 대한 지방에 대한 배려가 아니라 또는 시혜가 아니라 국가의 생존을 위한 생존 전략입니다.]

소비쿠폰 지급에서도 명백하게 보여줬다며 수도권보다는 지방에 더 많이 지원해야만 비로소 균형을 조금이라도 유지할 수 있다고 강조했습니다.
    """
}

result = chain.invoke(input_text)
print("요약 결과: ", result['summary'])