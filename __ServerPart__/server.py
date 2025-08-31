import json
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# File paths
USERS_FILE = ".json"
REQUESTS_FILE = ".json"
MESSAGES_FILE = ".json"

# Load or initialize files
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default

users = load_json(USERS_FILE, [])
requests_data = load_json(REQUESTS_FILE, [])
messages = load_json(MESSAGES_FILE, [])

@app.route('/')
def home():
    return "Message server is running!"

@app.route('/send', methods=['POST'])
def send():
    data = request.json
    if not data or 'from' not in data or 'to' not in data or 'text' not in data:
        return jsonify({'error': 'Invalid format'}), 400

    # If this is a system request (type: request)
    if data.get('type') == "request":
        requests_data.append(data)
        try:
            with open(REQUESTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(requests_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            return jsonify({'error': f'Failed to write requests file: {e}'}), 500
        return jsonify({'status': 'Request saved'})

    # Otherwise — regular message
    messages.append({
        'from': data['from'],
        'to': data['to'],
        'text': data['text']
    })

    try:
        with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return jsonify({'error': f'Failed to write messages: {e}'}), 500

    return jsonify({'status': 'OK'})

@app.route('/receive', methods=['GET'])
def receive():
    number = request.args.get('number')
    if not number:
        return jsonify({'error': 'Number not specified'}), 400

    global messages
    received = []
    remaining = []

    for msg in messages:
        if msg['to'] == number:
            received.append(msg)
        else:
            remaining.append(msg)

    if received:
        try:
            with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
                json.dump(remaining, f, ensure_ascii=False, indent=2)
            messages = remaining
        except Exception as e:
            return jsonify({'error': f'Failed to update messages.json: {e}'}), 500

    return jsonify({'messages': received})

@app.route('/check_requests', methods=['GET'])
def check_requests():
    number = request.args.get('number')
    if not number:
        return jsonify({'error': 'Number not specified'}), 400

    global requests_data
    found_requests = []
    remaining_requests = []

    for req in requests_data:
        if req['to'] == number:
            found_requests.append(req)
        else:
            remaining_requests.append(req)

    if found_requests:
        try:
            with open(REQUESTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(remaining_requests, f, ensure_ascii=False, indent=2)
            requests_data = remaining_requests
        except Exception as e:
            return jsonify({'error': f"Failed to update requests file: {e}"}), 500

    return jsonify({'requests': found_requests})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data or 'number' not in data or 'name' not in data:
        return jsonify({'error': 'Invalid format'}), 400

    for user in users:
        if user['number'] == data['number']:
            return jsonify({'status': 'Already registered'})

    users.append({
        'number': data['number'],
        'name': data['name']
    })

    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return jsonify({'error': f"Failed to write users file: {e}"}), 500

    return jsonify({'status': 'Registered'})

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify({'users': users})

if __name__ == '__main__':
    app.run()