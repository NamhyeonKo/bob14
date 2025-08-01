# pip install langchain
# pip install langchain-openai
# pip install langchain-core
# pip install langchain-community

from dotenv import load_dotenv
import os

from langchain_openai import OpenAI

load_dotenv()
openai_api_key = os.environ.get("openai_api_key")

llm = OpenAI(model="gpt-3.5-turbo-instruct", openai_api_key=openai_api_key)

prompt = "What is a good company name that makes arcade games?"

result = llm.invoke(prompt)

print(result)