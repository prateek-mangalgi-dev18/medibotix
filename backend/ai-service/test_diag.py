from ingest import ingest_file
from query import ask_question
import numpy as np

print("Imports successful.")

try:
    print("Testing ingest_file with dummy content...")
    ingest_file("test.txt", b"This is some test content for AI report analysis.")
    print("Ingestion successful.")
except Exception as e:
    print(f"Ingestion failed: {e}")

try:
    print("Testing ask_question...")
    res = ask_question("What is this about?")
    print(f"Result: {res}")
except Exception as e:
    print(f"Caught error in ask_question: {e}")


print("Test complete.")
