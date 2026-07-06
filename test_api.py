from huggingface_hub import InferenceClient

print("Attempting to connect...")
# Put your real hf_... token inside the quotes below!
client = InferenceClient(model="HuggingFaceH4/zephyr-7b-beta", token="YOUR_TOKEN_HERE")

try:
    response = client.text_generation("Hello, are you there?", max_new_tokens=20)
    print("SUCCESS! The AI said:", response)
except Exception as e:
    print("\n--- THE REAL ERROR IS ---")
    print(e)