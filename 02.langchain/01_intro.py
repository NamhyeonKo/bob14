import requests
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("open-ai-key")
print(openai_api_key)

response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    json={
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "당신은 사용자의 질문에 답변을 하는 AI입니다.",
            },
            {
                "role": "user",
                "content": "오늘 저녁에 먹어야 할 음식은?",
            },
        ],
        # 다양한 변수 적용
        "max_tokens" : 100,
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0.5,  # 반복 억제
        "presence_penalty": 0.6,  # 새로운 주제 장려
    },
    headers={
        'Content-Type':'application/json',
        'Authorization': f'Bearer {openai_api_key}'
    }
)
print(response)
print(response.json()['choices'][0]['message']['content'])
