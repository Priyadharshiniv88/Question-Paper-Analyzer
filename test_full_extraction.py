from pdf_processor import PDFProcessor
import json

def test_full_extraction():
    processor = PDFProcessor()
    
    # Update this path to your PDF
    pdf_path = r"C:\Users\vinot\Downloads\oop2024-2_merged.pdf"  # Change this path!
    
    print("="*80)
    print("🧪 TESTING FULL QUESTION EXTRACTION")
    print("="*80)
    
    try:
        result = processor.process_pdf(pdf_path)
        
        print("\n" + "="*80)
        print(f"📊 FINAL RESULTS: {result['total_questions']} questions extracted")
        print("="*80)
        
        if result['total_questions'] > 0:
            # Show statistics
            print(f"\n📈 Statistics:")
            print(f"  • PART A: {result['stats']['part_a']} questions")
            print(f"  • PART B: {result['stats']['part_b']} questions")
            print(f"  • PART C: {result['stats']['part_c']} questions")
            
            # Show all extracted questions
            print(f"\n📋 ALL EXTRACTED QUESTIONS:")
            print("-" * 80)
            
            current_part = ""
            for i, q in enumerate(result['questions'], 1):
                if q['part'] != current_part:
                    current_part = q['part']
                    print(f"\n--- PART {current_part} ({(q['marks'])} marks) ---")
                
                subpart = f"({q.get('subpart', '')})" if q.get('subpart') else ""
                print(f"{i:3}. Q{q['number']}{subpart}: {q['text'][:100]}...")
            
            # Save to file
            with open('extracted_questions.json', 'w', encoding='utf-8') as f:
                json.dump(result['questions'], f, indent=2, ensure_ascii=False)
            print(f"\n💾 Saved to extracted_questions.json")
            
        else:
            print("\n❌ No questions extracted")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_extraction()