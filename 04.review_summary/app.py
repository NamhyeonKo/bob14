from flask import Flask, request, jsonify

app = Flask(__name__, static_folder='public', static_url_path='')

reviews = [] # 사용자의 후기 저장 db

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
    app.run(debug=True, host='0.0.0.0', port=5000)