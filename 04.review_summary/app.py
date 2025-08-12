from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os

app = Flask(__name__, static_folder='public', static_url_path='')

reviews = [] # 사용자의 후기 저장 db

load_dotenv()

api_key = os.getenv('openai_api_key')
openai = OpenAI(api_key=api_key)

@app.route('/api/ai-summary', methods=['GET'])
def get_ai_summary():
    if not reviews:
        return jsonify({"summary": "No reviews available.", 'averageRating': 0}), 200

    average_rating = sum(review['rating'] for review in reviews) / len(reviews)
    reviews_text = "\n".join(f"Rating: {review['rating']}, Opinion: {review['opinion']}" for review in reviews)

    print(f"평점 계산: {average_rating}\n리뷰 내용: {reviews_text}")
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"Please summarize the following reviews:\n{reviews_text}\n\nAverage Rating: {average_rating}"
        }]
    )

    summary = response.choices[0].message.content.strip()
    return jsonify({"summary": summary, "averageRating": average_rating}), 200

@app.route('/api/reviews', methods=['POST'])
def add_review():
    data = request.get_json()
    # print(data)  # For debugging purposes
    rating = data.get('rating')
    opinion = data.get('opinion')

    if not rating or not opinion:
        return jsonify({'error': 'Rating and opinion are required'}), 400

    reviews.append({'rating': rating, 'opinion': opinion})

    return jsonify({'message': 'Review added successfully'}), 201

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    return jsonify({"reviews": reviews}), 200

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True)