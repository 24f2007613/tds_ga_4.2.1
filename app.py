import os
import base64
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"} })

client = genai.Client()

def clean_answer(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r'^```[a-zA-Z]*\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$', '', cleaned).strip()
    return cleaned

# Add a root route to handle default GET/HEAD requests and prevent 404 errors
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return jsonify({"status": "healthy", "message": "Multimodal QA API is running"}), 200

@app.route('/answer-image', methods=['POST'])
def answer_image():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400
            
        image_base64 = data.get("image_base64")
        question = data.get("question")
        
        if not image_base64 or not question:
            return jsonify({"error": "Missing image_base64 or question in request"}), 400
            
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]
            
        try:
            image_bytes = base64.b64decode(image_base64)
        except Exception:
            return jsonify({"error": "Invalid base64 encoding"}), 400

        system_instruction = (
            "You are a precise document data extraction agent. Analyze the provided image and "
            "answer the user query directly. "
            "CRITICAL RULES:\n"
            "1. Output ONLY the final raw answer string or number value.\n"
            "2. Do NOT include any extra conversational text, labels, units, or currency symbols.\n"
            "3. If the answer is a number, output only the digits and necessary decimal points (e.g., '4089.35')."
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/png',
                ),
                question
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0
            )
        )
        
        raw_text = response.text or ""
        final_answer = clean_answer(raw_text)
        
        return jsonify({"answer": final_answer}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)