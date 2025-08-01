from flask import Flask, jsonify, send_from_directory, request
from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

app = Flask(__name__, static_folder='public')

llm = ChatOpenAI(
    openai_api_key=os.getenv("openai_api_key"),
    model="gpt-3.5-turbo",
    temperature=0.2,
    max_tokens=2048
)

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("당신은 보안코드 분석 전문가입니다."),
    HumanMessagePromptTemplate.from_template("""
    다음 코드를 분석하고, 보안 취약점이 있는지 확인해주세요.
    각 취약점에 대해 해당 코드의 라인 번호, 코드 스니펫, 취약점 설명과 개선 방향을 간단하게 설명해줘. 주석라인은 무시해도 돼.
                                             
    소스코드:
    ----
    {code}                                     
    """)
])


chain = prompt | llm | StrOutputParser()

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/analyze', methods=['POST'])
def check_code():
    data = request.get_json()
    code = data.get('code', '')
    if not code:
        return jsonify({"error": "No code provided"}), 400
    
    analysis = chain.invoke({"code": code})
    return jsonify({"analysis": analysis})

if __name__ == '__main__':
    app.run(debug=True)