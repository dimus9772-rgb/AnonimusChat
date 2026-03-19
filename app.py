from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

FILE = "messages.json"
BABLO_FILE = "bablo.json"

# In-memory set to track online users
online_users = set()


def load_messages():
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_messages(messages):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False)


def load_bablo():
    with open(BABLO_FILE, "r", encoding="utf-8") as f:
        return int(f.read())


def save_bablo(amount):
    with open(BABLO_FILE, "w", encoding="utf-8") as f:
        f.write(str(amount))


def add_user(ip):
    online_users.add(ip)
    return True


def remove_user(ip):
    online_users.discard(ip)


@app.route("/")
def index():
    messages = load_messages()
    return render_template("index.html", messages=messages)


@app.route("/api/messages", methods=["GET"])
def get_messages():
    messages = load_messages()
    return jsonify(messages)


@app.route("/api/messages", methods=["POST"])
def post_message():
    data = request.get_json()
    text = data.get("message")
    
    if text:
        messages = load_messages()
        messages.append(text)
        messages = messages[-12:]
        save_messages(messages)
        
    return jsonify({"success": True})


@app.route("/api/bablo", methods=["GET"])
def get_bablo():
    bablo = load_bablo()
    return jsonify({"bablo": bablo})


@app.route("/api/bablo", methods=["POST"])
def post_bablo():
    bablo = load_bablo()
    bablo += 1
    save_bablo(bablo)
    socketio.emit('bablo_update', {'bablo': bablo, 'play_sound': True})
    return jsonify({"bablo": bablo})


@app.route("/api/buy-puk", methods=["POST"])
def buy_puk():
    data = request.get_json()
    cost = data.get("cost")
    sound_file = data.get("sound")
    
    if cost is None or sound_file is None:
        return jsonify({"success": False, "error": "Missing cost or sound"}), 400
    
    bablo = load_bablo()
    
    if bablo < cost:
        return jsonify({"success": False, "error": "Not enough bablo", "bablo": bablo}), 400
    
    bablo -= cost
    save_bablo(bablo)
    socketio.emit('bablo_update', {'bablo': bablo, 'play_sound': False})
    socketio.emit('puk_sound', {'sound': sound_file})
    
    return jsonify({"success": True, "bablo": bablo})


@app.route("/api/users", methods=["GET"])
def get_users():
    return jsonify({"count": len(online_users)})


@socketio.on('connect')
def handle_connect():
    ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    add_user(ip)
    socketio.emit('users_update', {'count': len(online_users)})


@socketio.on('disconnect')
def handle_disconnect():
    ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    remove_user(ip)
    socketio.emit('users_update', {'count': len(online_users)})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080, debug=True)
