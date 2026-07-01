# ============================================================
# TEACHER'S PET - FINAL WORKING VERSION
# ============================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# ============================================================
# CHECK FOR API KEYS
# ============================================================

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

# ============================================================
# GENERATE WITH GROQ (USING REQUESTS - NO PACKAGE NEEDED)
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
        
        prompt = f"""Create a worksheet for {grade} students.

Subject: {subject}
Topic: {topic}
Number of Questions: {num_q}
Question Type: {q_type}
Extra: {extra if extra else "None"}

Generate {num_q} UNIQUE questions about {topic} for {subject}.
For multiple choice, provide 4 realistic options (A, B, C, D).
DO NOT use "Option 1, 2, 3, 4" - use real answers.
Include an answer key at the end.

Start each question with the number and a period (1., 2., 3., etc.)

WORKSHEET:
"""
        
        data = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "You are a helpful teacher creating educational worksheets."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 2000
        }
        
        print("🔄 Calling Groq API...")
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print("✅ Groq success!")
            return content
        else:
            print(f"❌ Groq Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Groq Exception: {e}")
        return None

# ============================================================
# FALLBACK - ALWAYS WORKS
# ============================================================

def generate_fallback(subject, topic, grade, num_q, q_type):
    num_q = int(num_q)
    
    # Some real questions for common topics
    sample_questions = {
        "barter": [
            "What was the main problem with the barter system?",
            "How did people trade before money was invented?",
            "What is double coincidence of wants?",
            "Why did barter become less common over time?"
        ],
        "fraction": [
            "Simplify 6/8 to its lowest terms.",
            "What is 2/5 + 1/5?",
            "Which is larger: 3/4 or 5/8?",
            "Convert 0.75 to a fraction."
        ],
        "algebra": [
            "Solve for x: 3x + 5 = 20",
            "What is 2x + 3 when x = 4?",
            "Simplify: 5x - 2x + 7",
            "Is x = 3 a solution to 2x + 1 = 7?"
        ]
    }
    
    # Pick questions based on topic
    topic_lower = topic.lower()
    questions = []
    for key in sample_questions:
        if key in topic_lower:
            questions = sample_questions[key]
            break
    
    if not questions:
        questions = [f"What is {topic}?" for _ in range(num_q)]
    
    # Rotate questions if needed
    while len(questions) < num_q:
        questions.extend(questions[:num_q - len(questions)])
    
    worksheet = f"""
========================================
    {subject.upper()} WORKSHEET
    Topic: {topic}
    Grade: {grade}
========================================

INSTRUCTIONS: Answer all {num_q} questions below.

QUESTIONS:
"""
    for i in range(num_q):
        q = questions[i % len(questions)]
        if q_type == "Multiple Choice":
            worksheet += f"\n{i+1}. {q}\n   A) Option A\n   B) Option B\n   C) Option C\n   D) Option D\n"
        else:
            worksheet += f"\n{i+1}. {q}\n"

    worksheet += "\n========================================\nANSWER KEY\n========================================\n"
    for i in range(num_q):
        worksheet += f"{i+1}. (Answers will vary)\n"
    
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
    
    # Fallback
    print("⚠️ Groq failed, using fallback...")
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
    else:
        print("⚠️ No GROQ API Key found.")
        print("   Get one at: console.groq.com")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)