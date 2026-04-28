from flask import Flask, render_template, request, jsonify
import pdfplumber
import json
import os
from openai import OpenAI
import tempfile
from dotenv import load_dotenv

load_dotenv() # Load variables from .env

app = Flask(__name__)

# --- CONFIG ---
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def analyze_resume_ai(resume_text, job_description):
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=NVIDIA_API_KEY
    )
    
    prompt = f"""
You are an expert ATS (Applicant Tracking System) and resume coach.

Analyze the following resume against the job description and respond ONLY in this exact JSON format with no extra text.

CRITICAL RULE: If the provided RESUME text is NOT a resume (e.g. it is an admit card, a ticket, a random letter, or gibberish), you MUST set "ats_score" to 0 and "score_reason" to "INVALID DOCUMENT: The uploaded file does not appear to be a resume. Please upload a valid resume."

{{
  "ats_score": <number 0-100>,
  "score_reason": "<one sentence explaining the score>",
  "matched_keywords": ["keyword1", "keyword2"],
  "missing_keywords": ["keyword1", "keyword2"],
  "strengths": ["strength1", "strength2", "strength3"],
  "improvements": [
    {{"section": "section name", "suggestion": "specific rewrite suggestion"}},
    {{"section": "section name", "suggestion": "specific rewrite suggestion"}}
  ],
  "overall_verdict": "<2-3 sentence honest summary>"
}}

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""

    response = client.chat.completions.create(
        model="meta/llama-3.1-8b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
    )
    
    content = response.choices[0].message.content.strip()
    
    # Strip markdown code fences
    if content.startswith("```"):
        parts = content.split("```")
        if len(parts) >= 3:
            content = parts[1]
            if content.startswith("json"):
                content = content[4:].strip()
            else:
                content = content.strip()
    
    return json.loads(content)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file uploaded"}), 400
    
    file = request.files['resume']
    jd = request.form.get('jd', '')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not jd:
        return jsonify({"error": "Job description is empty"}), 400

    # --- MOCK MODE FOR TESTING ---
    if NVIDIA_API_KEY == "your_nvidia_api_key_here":
        import time
        time.sleep(2) # Simulate delay
        return jsonify({
            "ats_score": 82,
            "score_reason": "Your background in Python and SQL is a strong match for the Data Analyst role.",
            "matched_keywords": ["Python", "SQL", "Data Visualization", "Machine Learning", "Pandas"],
            "missing_keywords": ["Tableau", "ETL Pipelines"],
            "strengths": [
                "Strong proficiency in core data science libraries (NumPy, Pandas).",
                "Direct experience with implementing predictive models.",
                "Clear documentation and structured SQL logic."
            ],
            "improvements": [
                {"section": "Skills", "suggestion": "Add specific visualization tools like Tableau or Power BI to match the JD."},
                {"section": "Experience", "suggestion": "Quantify your impact on data cleaning tasks (e.g., 'Reduced processing time by 20%')."}
            ],
            "overall_verdict": "A very strong candidate with 90% of the required technical stack. Focusing on visualization tools will make this profile nearly perfect."
        })

    try:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            file.save(temp_pdf.name)
            temp_path = temp_pdf.name

        # Extract text
        resume_text = extract_text_from_pdf(temp_path)
        os.unlink(temp_path) # Delete temp file

        if not resume_text.strip():
            return jsonify({"error": "Could not extract text from PDF. Ensure it's not a scanned image."}), 400

        # AI Analysis
        analysis_data = analyze_resume_ai(resume_text, jd)
        return jsonify(analysis_data)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
