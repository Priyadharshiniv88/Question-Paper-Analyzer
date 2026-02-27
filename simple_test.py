import requests

# Test health
response = requests.get('http://localhost:5000/health')
print("Health check:", response.json())

# Replace with YOUR PDF path
pdf_path = r'C:\Users\vinot\Downloads\oop2024-2_merged.pdf'

try:
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        response = requests.post('http://localhost:5000/analyze', files=files)
    
    if response.status_code == 200:
        print("✅ Success!")
        data = response.json()
        print(f"Questions found: {data['analysis']['summary']['total_questions']}")
        print(f"Patterns: {data['analysis']['patterns']}")
    else:
        print("❌ Error:", response.json())
except Exception as e:
    print("❌ Error:", str(e))