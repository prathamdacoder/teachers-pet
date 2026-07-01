# ============================================================
# TEACHER'S PET - SIMPLE & WORKING!
# ============================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# ============================================================
# GET API KEYS
# ============================================================

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# ============================================================
# GENERATE WITH GROQ (FAST & FREE!)
# ============================================================

def generate_with_groq(subject, topic, grade, num_q, q_type, extra):
    if not GROQ_API_KEY:
        print("❌ No Groq API key found")
        return None
    
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""You are a teacher creating a worksheet for {grade} students.

Subject: {subject}
Topic: {topic}
Number of Questions: {num_q}
Question Type: {q_type}
Extra Instructions: {extra if extra else "None"}

Create {num_q} unique questions about {topic} for {subject}.
Make sure each question is DIFFERENT.
For multiple choice, give 4 options (A, B, C, D).
Include an answer key at the end.

Worksheet:
"""
        
        data = {
            "model": "mixtral-8x7b-32768",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"Groq API Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Groq Exception: {e}")
        return None

# ============================================================
# GENERATE WITH OPENAI (BACKUP)
# ============================================================

def generate_with_openai(subject, topic, grade, num_q, q_type, extra):
    if not OPENAI_API_KEY:
        return None
    
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""Create a worksheet for {grade} students.
Subject: {subject}
Topic: {topic}
Questions: {num_q} ({q_type})
Extra: {extra if extra else "None"}

Create {num_q} unique questions with an answer key.
"""
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return None
            
    except Exception as e:
        print(f"OpenAI Exception: {e}")
        return None

# ============================================================
# FALLBACK (ALWAYS WORKS!)
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
        elif q_type == "True/False":
            worksheet += f"\n{i}. {topic} is important. (True/False)\n"
        elif q_type == "Fill in the Blank":
            worksheet += f"\n{i}. The study of {topic} is called ______.\n"
        else:
            worksheet += f"\n{i}. Explain {topic} in your own words.\n"

    worksheet += "\n========================================\nANSWER KEY\n========================================\n"
    for i in range(1, num_q + 1):
        worksheet += f"{i}. (Answer will vary)\n"
    return worksheet

# ============================================================
# MAIN GENERATOR
# ============================================================

def generate_worksheet(subject, topic, grade, num_q, q_type, extra):
    print(f"📝 Generating: {subject} - {topic}")
    
    # Try Groq first
    result = generate_with_groq(subject, topic, grade, num_q, q_type, extra)
    if result:
        return result
    
    # Try OpenAI as backup
    print("⚠️ Groq failed, trying OpenAI...")
    result = generate_with_openai(subject, topic, grade, num_q, q_type, extra)
    if result:
        return result
    
    # Ultimate fallback
    print("⚠️ All AI failed, using fallback...")
    return generate_fallback(subject, topic, grade, num_q, q_type)

# ============================================================
# ROUTES
# ============================================================

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        subject = data.get('subject', 'Math')
        topic = data.get('topic', 'Fractions')
        grade = data.get('grade', '5th Grade')
        num_q = data.get('numQuestions', 10)
        q_type = data.get('questionType', 'Multiple Choice')
        extra = data.get('extraInstructions', '')
        
        worksheet = generate_worksheet(subject, topic, grade, num_q, q_type, extra)
        return jsonify({'worksheet': worksheet, 'success': True})
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': '🚀 Teacher\'s Pet is running!'})

# ============================================================
# START
# ============================================================

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 TEACHER'S PET BACKEND STARTED!")
    print("📍 http://localhost:5000")
    if GROQ_API_KEY:
        print("✅ GROQ API Key: FOUND")
    if OPENAI_API_KEY:
        print("✅ OPENAI API Key: FOUND")
    if not GROQ_API_KEY and not OPENAI_API_KEY:
        print("⚠️ No API keys found. Using fallback only.")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)