# ============================================================
# TEACHER'S PET - COMPLETE BACKEND (The Brain)
# ============================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load the API key from the .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allows your website to talk to this backend

# ============================================================
# 1. GET YOUR SECRET API KEY
# ============================================================
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# ============================================================
# 2. OPENAI (Smart AI)
# ============================================================
def generate_with_openai(prompt):
    if not OPENAI_API_KEY:
        return None
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": 0.8,
    }
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
        print(f"OpenAI Error: {resp.status_code}")
        return None
    except Exception as e:
        print(f"OpenAI Exception: {e}")
        return None

# ============================================================
# 3. HUGGINGFACE (Free Backup)
# ============================================================
def generate_with_huggingface(prompt):
    url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 1500, "temperature": 0.7, "return_full_text": False},
    }
    try:
        resp = requests.post(url, json=payload, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and data:
                return data[0].get('generated_text', '')
        return None
    except Exception:
        return None

# ============================================================
# 4. FALLBACK (No AI - Always works)
# ============================================================
def generate_fallback(subject, topic, grade, num_q, q_type):
    num_q = int(num_q)
    worksheet = f"""
========================================
    {subject.upper()} WORKSHEET
    Topic: {topic}
    Grade: {grade}
========================================

INSTRUCTIONS: Answer all {num_q} questions below.

QUESTIONS:
"""
    for i in range(1, num_q + 1):
        if q_type == "Multiple Choice":
            worksheet += f"\n{i}. What is {topic}?\n   A) Option 1\n   B) Option 2\n   C) Option 3\n   D) Option 4\n"
        else:
            worksheet += f"\n{i}. Explain the concept of {topic}.\n"

    worksheet += "\n========================================\nANSWER KEY\n========================================\n"
    for i in range(1, num_q + 1):
        worksheet += f"{i}. (Answer will vary)\n"
    return worksheet

# ============================================================
# 5. THE MAIN GENERATOR
# ============================================================
def generate_worksheet(subject, topic, grade, num_q, q_type, extra):
    prompt = f"""
You are an expert teacher. Create a unique, diverse worksheet.

RULES:
- NEVER repeat the same question.
- For multiple choice, give 4 REAL options (not Option 1,2,3,4).

Subject: {subject}
Topic: {topic}
Grade: {grade}
Number: {num_q}
Type: {q_type}
Extra: {extra if extra else "None"}

Create the worksheet with a title, instructions, {num_q} unique questions, and an answer key.
"""
    result = generate_with_openai(prompt)
    if result:
        return result
    result = generate_with_huggingface(prompt)
    if result:
        return result
    return generate_fallback(subject, topic, grade, num_q, q_type)

# ============================================================
# 6. THE ROUTES (Connecting the website)
# ============================================================
@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        worksheet = generate_worksheet(
            data.get('subject', 'Math'),
            data.get('topic', 'Fractions'),
            data.get('grade', '5th Grade'),
            data.get('numQuestions', 10),
            data.get('questionType', 'Multiple Choice'),
            data.get('extraInstructions', '')
        )
        return jsonify({'worksheet': worksheet, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': '🚀 Backend is running!'})

# ============================================================
# 7. START THE SERVER
# ============================================================
if __name__ == '__main__':
    print("=" * 50)
    print("🚀 TEACHER'S PET BACKEND STARTED!")
    print("📍 http://localhost:5000")
    if OPENAI_API_KEY:
        print("✅ OpenAI API Key: FOUND (Smart worksheets enabled!)")
    else:
        print("⚠️ No OpenAI API Key found. Using fallback.")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)