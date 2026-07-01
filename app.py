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
# VIDYA-9B - NCERT Expert (Classes 6-12)
# ============================================================

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load Vidya-9B (this runs on Render's free tier!)
def generate_with_vidya(subject, topic, grade, num_q, q_type, extra):
    try:
        # Load model (only once!)
        if not hasattr(generate_with_vidya, "model"):
            print("🔄 Loading Vidya-9B... (this takes ~30 seconds)")
            model_name = "neo-saket/vidya-9b"
            
            # Use CPU if GPU not available (Render free tier)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"📱 Using device: {device}")
            
            generate_with_vidya.tokenizer = AutoTokenizer.from_pretrained(model_name)
            generate_with_vidya.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float32,
                device_map="auto" if device == "cuda" else None,
                low_cpu_mem_usage=True
            )
            
            if device == "cpu":
                generate_with_vidya.model.to("cpu")
            
            print("✅ Vidya-9B loaded successfully!")

        # Build prompt for Vidya (it's trained on NCERT!)
        full_prompt = f"""
### Instruction:
You are a knowledgeable NCERT teacher for Classes 6-12. Create a high-quality worksheet.

### Subject: {subject}
### Topic: {topic}
### Grade Level: {grade}
### Number of Questions: {num_q}
### Question Type: {q_type}
### Extra: {extra if extra else "None"}

### Response:
Here is a worksheet with {num_q} unique questions. Include an answer key at the end.
"""
        
        # Generate
        inputs = generate_with_vidya.tokenizer(full_prompt, return_tensors="pt")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cuda":
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        
        outputs = generate_with_vidya.model.generate(
            **inputs,
            max_new_tokens=1500,
            temperature=0.8,
            do_sample=True,
            pad_token_id=generate_with_vidya.tokenizer.eos_token_id
        )
        
        response = generate_with_vidya.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the worksheet part
        if "### Response:" in response:
            response = response.split("### Response:")[-1].strip()
        
        return response
    except Exception as e:
        print(f"❌ Vidya error: {e}")
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
    # Try Vidya first (NCERT expert!)
    result = generate_with_vidya(subject, topic, grade, num_q, q_type, extra)
    if result:
        return result
    
    # Fallback to HuggingFace if Vidya fails
    prompt = f"Create a worksheet for {subject} on {topic} for {grade} with {num_q} questions."
    result = generate_with_huggingface(prompt)
    if result:
        return result
    
    # Ultimate fallback
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