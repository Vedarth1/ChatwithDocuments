import os
import uuid
from flask import Blueprint, Response, json, request, session
from werkzeug.utils import secure_filename
from src.services.query_engine import QueryEngine

chats = Blueprint("chats", __name__)

query_engine = QueryEngine()

@chats.route('/hello', methods=["GET"])
def hello():
    return Response(
        response=json.dumps({'status': "success", "message": "Hello"}),
        status=200,
        mimetype='application/json'
    )

@chats.route('/upload', methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return Response(
            response=json.dumps({'status': "failed", "message": "No file part"}),
            status=400,
            mimetype='application/json'
        )
    file = request.files['file']
    if file.filename == '':
        return Response(
            response=json.dumps({'status': "failed", "message": "No selected file"}),
            status=400,
            mimetype='application/json'
        )
    if file:
        filename = secure_filename(file.filename)
        user_id = session.get('user_id')

        if not user_id:
            # Generate a new user_id if it doesn't exist in session
            user_id = str(uuid.uuid4())
            session['user_id'] = user_id

        filepath = os.path.join("uploaded_files", user_id, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        query_engine.load_documents(user_id, os.path.dirname(filepath))
        return Response(
            response=json.dumps({'status': "success", "message": f"File {filename} uploaded and documents loaded for user {user_id}"}),
            status=200,
            mimetype='application/json'
        )

@chats.route('/query', methods=["POST"])
def query_chatbot():
    data = request.get_json()
    user_id = session.get('user_id')
    query_text = data.get('query')

    if not user_id or not query_text:
        return Response(
            response=json.dumps({'status': "failed", "message": "Session not found or query is missing"}),
            status=400,
            mimetype='application/json'
        )

    print(user_id)
    response = query_engine.query(user_id, query_text)
    
    # Convert response to a JSON serializable format
    if isinstance(response, str):
        serialized_response = response
    else:
        serialized_response = {"result": str(response)}

    return Response(
        response=json.dumps({'status': "success", "response": serialized_response}),
        status=200,
        mimetype='application/json'
    )
