from dotenv import load_dotenv
import os

from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

load_dotenv()
openai_api_key = os.environ.get("openai_api_key")

llm =ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=openai_api_key)
# prompt = "What is a good company name that makes arcade games?"
prompt = [HumanMessage(content= "What is a good company name that makes arcade games?")]
result = llm.invoke(prompt)
print(result)