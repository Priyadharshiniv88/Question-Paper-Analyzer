import PyPDF2
import re
import os
from typing import List, Dict

class PDFProcessor:
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                print(f"📄 PDF has {len(pdf_reader.pages)} pages")
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        # Clean page text
                        page_text = self.clean_page_text(page_text)
                        text += page_text + "\n"
                        print(f"  Page {page_num + 1}: {len(page_text)} chars")
                    
            print(f"✅ Total extracted: {len(text)} characters")
            return text
            
        except Exception as e:
            print(f"❌ Error extracting PDF: {e}")
            return ""
    
    def clean_page_text(self, text: str) -> str:
        """Clean text from a single page"""
        # Remove watermarks
        text = re.sub(r'www\.\S+\.com', '', text, flags=re.IGNORECASE)
        text = re.sub(r'EnggTree\.com', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Downloaded from.*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Reg\.No\..*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Question Paper Code.*', '', text, flags=re.IGNORECASE)
        
        # Remove page numbers
        text = re.sub(r'===== Page \d+ =====', '', text)
        
        return text
    
    def extract_questions_from_engineering_paper(self, text: str) -> List[Dict]:
        """Extract questions from engineering question paper format"""
        questions = []
        
        # First, split by parts (PART A, PART B, PART C)
        part_pattern = r'(PART\s+[A-C])(?:\s*[-\s]*\([^)]+\))?'
        parts = re.split(part_pattern, text, flags=re.IGNORECASE)
        
        current_part = "A"
        current_marks = 2
        
        print(f"🔍 Found {len(parts)//2} parts in the paper")
        
        for i in range(1, len(parts), 2):
            if i+1 < len(parts):
                part_header = parts[i].strip()
                part_content = parts[i+1].strip()
                
                # Determine part and marks
                if 'PART A' in part_header.upper():
                    current_part = 'A'
                    current_marks = 2
                    print(f"\n📝 Processing PART A (2 marks each)")
                elif 'PART B' in part_header.upper():
                    current_part = 'B'
                    current_marks = 13
                    print(f"\n📝 Processing PART B (13 marks each)")
                elif 'PART C' in part_header.upper():
                    current_part = 'C'
                    current_marks = 15
                    print(f"\n📝 Processing PART C (15 marks each)")
                
                # Extract questions from this part
                part_questions = self.extract_questions_from_part(part_content, current_part, current_marks)
                questions.extend(part_questions)
                print(f"   Found {len(part_questions)} questions in {part_header}")
        
        return questions
    
    def extract_questions_from_part(self, text: str, part: str, marks: int) -> List[Dict]:
        """Extract questions from a specific part"""
        questions = []
        
        # Split into lines
        lines = text.split('\n')
        
        current_question = ""
        current_q_num = ""
        current_subpart = ""
        collecting = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for main question numbers (1., 2., 11., 12., etc.)
            main_question_match = re.match(r'^(\d+)[\.\)]\s*(.*)', line)
            
            # Check for subparts (a), (b), etc.
            subpart_match = re.match(r'^\(([a-z])\)\s*(.*)', line)
            
            # Check for "Or" separator
            or_match = re.match(r'^Or\b', line, re.IGNORECASE)
            
            if main_question_match:
                # Save previous question if exists
                if current_question and len(current_question) > 10:
                    questions.append({
                        'number': current_q_num,
                        'subpart': current_subpart,
                        'text': current_question.strip(),
                        'part': part,
                        'marks': marks,
                        'is_or': False
                    })
                
                # Start new question
                current_q_num = main_question_match.group(1)
                current_subpart = ""
                current_question = main_question_match.group(2)
                collecting = True
                
            elif subpart_match and collecting:
                # Save previous subpart if exists
                if current_question and len(current_question) > 10 and current_subpart:
                    questions.append({
                        'number': current_q_num,
                        'subpart': current_subpart,
                        'text': current_question.strip(),
                        'part': part,
                        'marks': marks,
                        'is_or': False
                    })
                
                # Start new subpart
                current_subpart = subpart_match.group(1)
                current_question = subpart_match.group(2)
                
            elif or_match and collecting:
                # Mark the previous question as having an OR option
                if questions:
                    questions[-1]['has_or'] = True
                    
                # The next line after "Or" will be the alternative
                continue
                
            elif collecting:
                # Continue collecting current question
                current_question += " " + line
        
        # Add the last question
        if current_question and len(current_question) > 10:
            questions.append({
                'number': current_q_num,
                'subpart': current_subpart,
                'text': current_question.strip(),
                'part': part,
                'marks': marks,
                'is_or': False
            })
        
        return questions
    
    def extract_questions_fallback(self, text: str) -> List[Dict]:
        """Fallback method using simple patterns"""
        questions = []
        
        # Pattern for numbered questions
        patterns = [
            # Main questions: 1. or 1)
            r'(?:^|\n)\s*(\d+)[\.\)]\s*(.*?)(?=\n\s*\d+[\.\)]|\n\s*\([a-z]\)|\Z)',
            # Sub questions: (a) or (b)
            r'(?:^|\n)\s*\(([a-z])\)\s*(.*?)(?=\n\s*\(\d+|\n\s*\d+[\.\)]|\Z)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                if len(match) == 2:
                    q_num, q_text = match
                    # Clean the text
                    q_text = re.sub(r'\s+', ' ', q_text).strip()
                    if len(q_text) > 15 and 'www' not in q_text and 'EnggTree' not in q_text:
                        questions.append({
                            'number': q_num,
                            'text': q_text,
                            'part': 'A' if int(q_num) <= 10 else 'B' if int(q_num) <= 15 else 'C',
                            'marks': 2 if int(q_num) <= 10 else 13 if int(q_num) <= 15 else 15
                        })
        
        return questions
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """Main method to process PDF"""
        print(f"\n📂 Processing: {os.path.basename(pdf_path)}")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            raise ValueError("Could not extract text from PDF")
        
        # Try engineering paper format first
        print("\n🔍 Method 1: Engineering paper format...")
        questions = self.extract_questions_from_engineering_paper(text)
        print(f"   Found {len(questions)} questions")
        
        # If that fails, try fallback method
        if len(questions) < 10:
            print("\n🔍 Method 2: Using fallback patterns...")
            questions = self.extract_questions_fallback(text)
            print(f"   Found {len(questions)} questions")
        
        print(f"\n✅ Total questions extracted: {len(questions)}")
        
        # Group by part for statistics
        part_a = [q for q in questions if q.get('part') == 'A']
        part_b = [q for q in questions if q.get('part') == 'B']
        part_c = [q for q in questions if q.get('part') == 'C']
        
        if part_a:
            print(f"  • PART A: {len(part_a)} questions")
        if part_b:
            print(f"  • PART B: {len(part_b)} questions")
        if part_c:
            print(f"  • PART C: {len(part_c)} questions")
        
        # Print sample
        if questions:
            print("\n📋 Sample extracted questions:")
            for i, q in enumerate(questions[:5]):
                print(f"  {i+1}. [{q['part']}] Q{q['number']}{q.get('subpart', '')}: {q['text'][:80]}...")
        
        return {
            'filename': os.path.basename(pdf_path),
            'total_questions': len(questions),
            'questions': questions,
            'stats': {
                'part_a': len(part_a),
                'part_b': len(part_b),
                'part_c': len(part_c)
            }
        } 