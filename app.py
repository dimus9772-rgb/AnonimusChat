from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

FILE = "messages.json"


def load_messages():
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_messages(messages):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False)


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


if __name__ == "__main__":
    app.run(debug=True)