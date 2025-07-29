from flask import Blueprint, request, jsonify, Flask
import os
from huggingface_hub import InferenceClient
import json

bp = Blueprint("mistral", __name__, url_prefix="/mistral")

API_TOKEN = os.getenv("HF_API_TOKEN")
client = InferenceClient(token=API_TOKEN)
model_id = "mistralai/Mistral-7B-v0.1"

@bp.route("/generate", methods=["POST"])
def generate_post():
    data = request.json
    topic = data.get("topic", "")
    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    prompt = f"write post about: {topic}"
    response = client.text_generation(model=model_id, inputs=prompt, parameters={"max_new_tokens": 200})
    post_text = response.generated_text

    result = {
        "topic": topic,
        "post": post_text
    }

    filename = f"post_{topic[:10].replace(' ', '_')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    return jsonify(result)

app = Flask(__name__)
app.register_blueprint(bp)