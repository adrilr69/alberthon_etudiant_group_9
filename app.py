import os
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory
from dotenv import load_dotenv
import vertexai
from vertexai.preview import reasoning_engines

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
REASONING_ENGINE_ID = os.getenv("REASONING_ENGINE_ID")
creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

if creds_path and not os.path.isabs(creds_path):
    creds_path = str(BASE_DIR / creds_path)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path

vertexai.init(project=PROJECT_ID, location=LOCATION)
_engine = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = reasoning_engines.ReasoningEngine(REASONING_ENGINE_ID)
    return _engine


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(BASE_DIR / "pictures", filename)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()
    thread_id = data.get("thread_id", "1")

    if not message:
        return jsonify({"error": "Message is required"}), 400

    try:
        response = get_engine().query(
            config={"thread_id": thread_id},
            message=message
        )
        return jsonify({"response": str(response)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
