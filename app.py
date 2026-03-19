from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

FILE = "messages.json"
BABLO_FILE = "bablo.json"


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
        messages = messages[-13:]
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
    socketio.emit('bablo_update', {'bablo': bablo})
    return jsonify({"bablo": bablo})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080, debug=True)
