from flask import Flask, render_template, request, redirect
import json

app = Flask(__name__)

FILE = "messages.json"


def load_messages():
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_messages(messages):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False)


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        text = request.form.get("message")

        if text:
            messages = load_messages()
            messages.append(text)

            messages = messages[-40:]

            save_messages(messages)

        return redirect("/")

    messages = load_messages()

    return render_template("index.html", messages=messages)


if __name__ == "__main__":
    app.run(debug=True)