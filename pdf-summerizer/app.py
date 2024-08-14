import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
from PyPDF2 import PdfReader
import traceback

app = Flask(__name__)
CORS(app)

# 初始化 OpenAI 客户端
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    # 如果文本超过50000个字符，截断它
    max_chars = 50000
    if len(text) > max_chars:
        text = text[:max_chars]
        print(f"Warning: PDF content truncated to {max_chars} characters.")
    
    return text

def generate_summary(text):
    max_tokens = 14000
    chunk_size = max_tokens // 2
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    summaries = []

    try:
        for chunk in chunks:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-16k",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes academic papers."},
                    {"role": "user", "content": f"Please summarize the following part of an academic paper in about 100 words:\n\n{chunk}"}
                ],
                max_tokens=250
            )
            summaries.append(response.choices[0].message.content.strip())

        if len(summaries) > 1:
            combined_summary = " ".join(summaries)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-16k",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes academic papers."},
                    {"role": "user", "content": f"Please provide a comprehensive final summary of about 300-400 words for these summaries of different parts of a paper. Ensure the summary is complete and coherent:\n\n{combined_summary}"}
                ],
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        else:
            return summaries[0]
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.pdf'):
        try:
            text = extract_text_from_pdf(file)
            summary = generate_summary(text)
            return jsonify({"summary": summary})
        except Exception as e:
            error_message = str(e)
            stack_trace = traceback.format_exc()
            print(f"Error in summarize_pdf: {error_message}")
            print(f"Stack trace:\n{stack_trace}")
            return jsonify({"error": f"Error in generating summary: {error_message}"}), 500
    else:
        return jsonify({"error": "Invalid file format"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=3001)