import openai
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("open-ai-key")
print(openai_api_key)

openai.api_key = openai_api_key

response = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages = [
        {
            "role": "system",
            "content": "당신은 사용자의 질문에 답변을 하는 AI입니다.",
        },
        {
            "role": "user",
            "content": "오늘 저녁에 먹어야 할 음식은?",
        }
    ],
    temperature = 0.7
)

print(response)
print(response['choices'][0]['message']['content'])