import pdfplumber
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG ---
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
RESUME_PDF_PATH = "resume.pdf"

# --- JOB DESCRIPTION ---
JOB_DESCRIPTION = """
Job Description: Data Analyst (SQL, Python, Visualization, Machine Learning)
Role and Responsibilities:
- Collaborate with cross-functional teams to identify data requirements, analyse business processes, and recommend data-driven solutions.
- Develop and execute complex SQL queries to retrieve, clean, and transform data from various sources.
- Utilize Python for data manipulation, statistical analysis, automation tasks, and implementing machine learning models.
- Apply machine learning techniques for predictive modelling, anomaly detection, and pattern recognition.
- Create insightful and interactive visualizations using Tableau, Power BI, or Python libraries (matplotlib, seaborn).
- Develop and optimize machine learning pipelines including feature engineering, model selection, and hyperparameter tuning.

Qualifications:
- Bachelor's degree in Computer Science, Statistics, Data Science, or related field.
- 1-3 years experience as a Data Analyst, Data Scientist, or Product Analyst.
- Strong proficiency in SQL, Python, data visualization tools, and machine learning concepts.

---

Job Description: Data Scientist (Machine Learning, NLP, Image Analytics)
Role and Responsibilities:
- Lead end-to-end data science projects from problem formulation to model deployment.
- Apply advanced ML algorithms for predictive modeling, classification, and regression.
- Develop and fine-tune NLP models for sentiment analysis, entity recognition, and language generation.
- Utilize image analytics techniques using OpenCV, Pillow, and deep learning frameworks.
- Build and evaluate machine learning models ensuring performance and robustness.

Qualifications:
- Bachelor's degree in Computer Science, Data Science, Statistics, or related field.
- 1-3 years of hands-on experience in data science, ML, NLP, and image analytics.
- Proficiency in TensorFlow, PyTorch, scikit-learn, spaCy, NLTK.
- Strong Python skills and understanding of statistical concepts and feature engineering.
"""

def extract_text_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    if not text.strip():
        raise ValueError("Extracted text is empty. PDF might be scanned or corrupted.")
    
    print(f"✅ Extracted {len(text)} characters from {num_pages} pages.")
    return text

def analyze_resume(resume_text, job_description):
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
    
    # Strip markdown code fences if present
    if content.startswith("```"):
        # Split by ``` and take the middle part
        parts = content.split("```")
        if len(parts) >= 3:
            # Check if first part had 'json'
            content = parts[1]
            if content.startswith("json"):
                content = content[4:].strip()
            else:
                content = content.strip()
    
    return json.loads(content)

def print_results(data):
    score = data.get("ats_score", 0)
    
    # ANSI Color Codes
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    if score >= 70:
        color = GREEN
    elif score >= 40:
        color = YELLOW
    else:
        color = RED
        
    print("\n" + "═"*60)
    print(f"{BOLD}REPORT: AI RESUME ANALYSIS{RESET}")
    print("═"*60)
    
    print(f"\n{BOLD}ATS SCORE:{RESET} {color}{score}/100{RESET}")
    print(f"{BOLD}Reason:{RESET} {data.get('score_reason', 'N/A')}")
    print("\n" + "─"*60)
    
    matched = data.get("matched_keywords", [])
    print(f"{BOLD}Matched Keywords ({len(matched)}):{RESET}")
    print(f"{GREEN}{', '.join(matched) if matched else 'None'}{RESET}")
    
    missing = data.get("missing_keywords", [])
    print(f"\n{BOLD}Missing Keywords ({len(missing)}):{RESET}")
    print(f"{RED}{', '.join(missing) if missing else 'None'}{RESET}")
    print("\n" + "─"*60)
    
    print(f"{BOLD}Strengths:{RESET}")
    for strength in data.get("strengths", []):
        print(f"  • {strength}")
    
    print(f"\n{BOLD}Areas for Improvement:{RESET}")
    for imp in data.get("improvements", []):
        section = imp.get("section", "General")
        suggestion = imp.get("suggestion", "")
        print(f"  [{color}{section.upper()}{RESET}] {suggestion}")
        
    print("\n" + "─"*60)
    print(f"{BOLD}Overall Verdict:{RESET}")
    print(f"\"{data.get('overall_verdict', '')}\"")
    print("═"*60 + "\n")
    
    # Save to JSON
    with open("analysis_result.json", "w") as f:
        json.dump(data, f, indent=4)
    print(f"💾 Results saved to analysis_result.json\n")

def main():
    print("🚀 Resume Analyzer — NVIDIA NIM API")
    try:
        # Step 1: Extract
        resume_text = extract_text_from_pdf(RESUME_PDF_PATH)
        
        # Step 2: Analyze
        print("🤖 Analyzing resume via NVIDIA NIM...")
        data = analyze_resume(resume_text, JOB_DESCRIPTION)
        
        # Step 3: Print
        print_results(data)
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
    except ValueError as e:
        print(f"❌ Error: {e}")
    except json.JSONDecodeError:
        print("❌ Error: Failed to parse API response. Please try again.")
    except Exception as e:
        print(f"❌ API Failure: {e}")

if __name__ == "__main__":
    main()
