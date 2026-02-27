import sys
from pdf_processor import PDFProcessor

def debug_pdf(pdf_path):
    """Debug PDF extraction"""
    print(f"\n🔍 DEBUGGING PDF: {pdf_path}")
    print("="*60)
    
    # Check if file exists
    import os
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return
    
    print(f"✅ File exists: {os.path.getsize(pdf_path)} bytes")
    
    # Process PDF
    processor = PDFProcessor()
    
    try:
        result = processor.process_pdf(pdf_path)
        
        print("\n📊 FINAL RESULTS:")
        print(f"Total questions: {result['total_questions']}")
        
        if result['questions']:
            print("\n📝 All extracted questions:")
            for i, q in enumerate(result['questions']):
                print(f"\n--- Question {i+1} ---")
                print(f"Number: {q['number']}")
                print(f"Part: {q.get('part', 'Unknown')}")
                print(f"Text: {q['text'][:200]}...")
        else:
            print("\n❌ No questions were extracted!")
            print("\n💡 Suggestions:")
            print("1. Check if PDF is text-based (not scanned)")
            print("2. Try a different PDF file")
            print("3. Check if PDF has questions in standard format")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    # Use the path to your PDF
    pdf_path = r"C:\Users\vinot\Downloads\dbms2024-2_merged.pdf"
    
    # You can also pass path as command line argument
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    
    debug_pdf(pdf_path)