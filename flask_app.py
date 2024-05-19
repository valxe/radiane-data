from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)

@app.route('/users')
def serve_users():
    users_data = {}
    users_dir = os.path.join('data', 'users')
    for filename in os.listdir(users_dir):
        if filename.endswith('.json'):
            with open(os.path.join(users_dir, filename), 'r') as file:
                user_data = json.load(file)
                user_name = os.path.splitext(filename)[0]
                users_data[user_name] = user_data

    return jsonify(users_data)

@app.route('/top.json')
def serve_top():
    return send_from_directory('data', 'top.json')

@app.route('/total.json')
def serve_total():
    return send_from_directory('data', 'total.json')

def start_flask_server():
    app.run(host='0.0.0.0', port=9999)
