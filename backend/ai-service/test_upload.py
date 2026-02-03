import requests

# Test the upload endpoint
url = "http://localhost:8000/upload"
file_path = "test_document.txt"

try:
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f)}
        response = requests.post(url, files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS: File uploaded successfully!")
    else:
        print("\n❌ ERROR: Upload failed")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
