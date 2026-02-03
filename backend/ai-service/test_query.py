import requests

# Test the ask endpoint
url = "http://localhost:8000/ask"

questions = [
    "What are the common medical conditions mentioned?",
    "What should I do in case of emergency symptoms?",
    "What are the treatment guidelines?"
]

print("Testing Query Functionality\n" + "="*50)

for i, question in enumerate(questions, 1):
    try:
        response = requests.post(url, params={"q": question})
        print(f"\n{i}. Question: {question}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            answer = response.json().get("answer", "No answer")
            print(f"   Answer: {answer[:200]}...")  # Show first 200 chars
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

print("\n" + "="*50)
print("✅ Query testing complete!")
