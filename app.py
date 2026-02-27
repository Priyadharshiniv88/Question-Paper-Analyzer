from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

from analyzer import QuestionTrendAnalyzer
from sample_questions import get_sample_questions  # Import sample questions

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_subject_from_filename(filename):
    """Detect subject based on filename"""
    filename_lower = filename.lower()
    if 'oop' in filename_lower or 'object' in filename_lower:
        return 'OOP'
    elif 'ds' in filename_lower or 'data' in filename_lower or 'structure' in filename_lower:
        return 'DS'
    elif 'dbms' in filename_lower or 'database' in filename_lower:
        return 'DBMS'
    elif 'cn' in filename_lower or 'network' in filename_lower:
        return 'CN'
    else:
        return 'OOP'  # Default to OOP

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'running', 'time': datetime.now().isoformat()})

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Please upload a PDF file'}), 400
        
        # Detect subject from filename
        subject = detect_subject_from_filename(file.filename)
        print(f"📚 Detected subject: {subject} from file: {file.filename}")
        
        # Get sample questions for the detected subject
        questions = get_sample_questions(subject)
        print(f"📊 Loaded {len(questions)} sample questions for {subject}")
        
        # Analyze the questions
        analyzer = QuestionTrendAnalyzer(similarity_threshold=0.7)
        analysis = analyzer.analyze(questions)
        
        # Add metadata
        analysis['subject'] = subject
        analysis['source'] = 'sample_data'
        
        return jsonify({
            'success': True,
            'filename': file.filename,
            'subject': subject,
            'analysis': analysis,
            'message': f'Analysis complete using {subject} question bank'
        })
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/subjects', methods=['GET'])
def get_subjects():
    """Get list of available subjects"""
    subjects = ['OOP', 'DS', 'DBMS', 'CN']
    return jsonify({'subjects': subjects})

@app.route('/questions/<subject>', methods=['GET'])
def get_questions_by_subject(subject):
    """Get questions for a specific subject"""
    try:
        questions = get_sample_questions(subject)
        return jsonify({
            'success': True,
            'subject': subject,
            'total_questions': len(questions),
            'questions': questions[:5]  # Return first 5 as preview
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("="*60)
    print("🚀 EXAM CRAM AI BACKEND STARTING...")
    print("="*60)
    print("\n📚 Available subjects:")
    print("  • OOP (Object Oriented Programming)")
    print("  • DS (Data Structures)")
    print("  • DBMS (Database Management)")
    print("  • CN (Computer Networks)")
    print("\n🌐 Server running on: http://localhost:5000")
    print("="*60)
    app.run(debug=True, port=5000)