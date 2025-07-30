import openai
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("openai_api_key")
client = openai.OpenAI(api_key=openai_api_key)

def ask_chatbot(user_input):
    response = client.chat.completions.create(
        model = 'gpt-3.5-turbo',
        messages = [
            {'role':'system','content':'당신은 고급 호텔 요리사 입니다'},
            {'role':'user','content':user_input}
        ],
        temperature=1.3
    )
    return response.choices[0].message.content

while True:
    user_input = input("you : ".strip())
    print(ask_chatbot(user_input))