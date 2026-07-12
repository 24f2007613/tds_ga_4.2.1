import os
import base64
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
# Enable CORS globally for all endpoints to allow cross-origin requests from the grader
CORS(app, resources={r"/*": {"origins": "*"} })

# Initialize the Gemini Client. 
# Make sure GEMINI_API_KEY is configured in your Render environment variables.
client = genai.Client()

def clean_answer(text: str) -> str:
    cleaned = text.strip()
    # Remove markdown code blocks if the model wraps the output text
    cleaned = re.sub(r'^```[a-zA-Z]*\s*', '', cleaned)
    cleaned = re.sub(r'\s*