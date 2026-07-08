import os
from dotenv import load_dotenv
from groq import Groq
from huggingface_hub import InferenceClient

# Load the keys from your .env file
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
GROQ_TOKEN = os.getenv("GROQ_API_KEY")

print("====================================")
print("🔍 API DIAGNOSTIC TEST")
print("====================================\n")

# 1. Test Primary API (Hugging Face)
print("Testing Primary API (Hugging Face - Qwen)...")
try:
    hf_client = InferenceClient(model="Qwen/Qwen2.5-7B-Instruct", token=HF_TOKEN, timeout=15)
    response = hf_client.chat_completion(
        messages=[{"role": "user", "content": "Say exactly: 'Hugging Face is working!'"}]
    )
    print("✅ SUCCESS! AI said:", response.choices[0].message.content)
except Exception as e:
    print("❌ HUGGING FACE FAILED!")
    print(f"Error Details: {e}")

print("\n------------------------------------\n")

# 2. Test Fallback API (Groq)
print("Testing Fallback API (Groq - Llama 3)...")
try:
    groq_client = Groq(api_key=GROQ_TOKEN)
    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": "Say exactly: 'Groq is working!'"}]
    )
    print("✅ SUCCESS! AI said:", response.choices[0].message.content)
except Exception as e:
    print("❌ GROQ FAILED!")
    print(f"Error Details: {e}")

print("\n====================================")