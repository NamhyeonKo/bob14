# pip install flask flask-cors
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from vectorstore import initialize_vector_db, create_vector_db, answer_question, DATA_DIR

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    # return send_from_directory('static', 'index.html') 
    return app.send_static_file('index.html')

# 파일 업로드를 처리하는 엔드포인트
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "파일이 없습니다."}), 400
    
    file = request.files['file']
    if file:
        file_path = os.path.join(DATA_DIR, file.filename)
        file.save(file_path)
        create_vector_db(file_path)
        
    return jsonify({"message": "파일이 업로드되고 벡터 DB가 성공적으로 생성되었습니다."}), 200

# 질문을 처리하는 엔드포인트
@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question', '')
    if not question:
        return jsonify({"error": "질문이 제공되지 않았습니다."}), 400
    
    answer = answer_question(question)
    return jsonify({"answer": answer})

# 파일 목록을 조회하는 엔드포인트
@app.route('/files', methods=['GET'])
def get_files():
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.endswith(('.pdf', '.txt', '.docx'))]
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": f"파일 목록을 가져오는 중 오류가 발생했습니다: {str(e)}"}), 500

# 파일을 삭제하는 엔드포인트
@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        file_path = os.path.join(DATA_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"message": f"파일 '{filename}'이 성공적으로 삭제되었습니다."})
        else:
            return jsonify({"error": "파일을 찾을 수 없습니다."}), 404
    except Exception as e:
        return jsonify({"error": f"파일 삭제 중 오류가 발생했습니다: {str(e)}"}), 500

if __name__ == '__main__':
    initialize_vector_db()
    app.run(debug=True)