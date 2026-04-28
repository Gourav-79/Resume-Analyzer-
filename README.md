# 🚀 AI Resume Analyzer (NVIDIA NIM & Llama 3.1)

A high-fidelity, professional AI-powered Resume Analyzer built with **Python**, **Flask**, and **NVIDIA NIM API**. This tool analyzes resumes against job descriptions using the **Llama 3.1 8B** model to provide an ATS score, keyword matching, and detailed feedback.

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-v3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![NVIDIA](https://img.shields.io/badge/NVIDIA_NIM-Llama_3.1-76B900?style=for-the-badge&logo=nvidia&logoColor=white)

## ✨ Features

- 📊 **ATS Score Calculation**: Instant scoring based on the provided Job Description.
- 🔍 **Keyword Analysis**: Identifies matched and missing keywords.
- ✅ **Strengths & Improvements**: Provides specific, actionable advice for resume enhancement.
- 📄 **PDF Extraction**: Efficiently extracts text from uploaded PDF resumes.
- 🌑 **Dark-Themed UI**: Modern, premium design for a great user experience.

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **AI Model**: Meta Llama 3.1 8B (via NVIDIA NIM)
- **PDF Processing**: `pdfplumber`
- **Frontend**: HTML5, Vanilla CSS, JavaScript
- **API Integration**: OpenAI Python Client (NVIDIA endpoint)

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.8+
- NVIDIA NIM API Key (Get it from [NVIDIA Build](https://build.nvidia.com/))

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/Gourav-79/Resume-Analyer-.git
cd Resume-Analyer-
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory and add your API key:
```env
NVIDIA_API_KEY=your_nvidia_api_key_here
```

### 4. Run the App
```bash
python app.py
```
Visit `http://127.0.0.1:5000` in your browser.

## 📸 Screenshots

*(Add your screenshots here later)*

---
Developed by **Gourav** 🚀
