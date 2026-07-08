import os
from huggingface_hub import InferenceClient
from groq import Groq

def generate_response(messages, raw_system_prompt):
    PRIMARY_TOKEN = os.getenv("HF_TOKEN")
    FALLBACK_TOKEN = os.getenv("GROQ_API_KEY") 
    
    system_msg = [{"role": "system", "content": raw_system_prompt}]
    full_payload = system_msg + messages

    # Attempt 1: Primary API (Hugging Face)
    try:
        client = InferenceClient(model="Qwen/Qwen2.5-7B-Instruct", token=PRIMARY_TOKEN, timeout=8)
        hf_stream = client.chat_completion(messages=full_payload, max_tokens=300, stream=True)
        
        # CRITICAL FIX: Yield chunks INSIDE the try block so we can catch timeouts!
        for chunk in hf_stream:
            yield chunk
            
    except Exception as primary_error:
        print(f"Primary API Failed or Timed Out. Rerouting to Groq Fallback...")
        
        # Attempt 2: Fallback API (Groq - Llama 3.1)
        try:
            groq_client = Groq(api_key=FALLBACK_TOKEN)
            groq_stream = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",  # The updated valid model
                messages=full_payload,
                max_tokens=300,
                stream=True
            )
            for chunk in groq_stream:
                yield chunk
        except Exception as fallback_error:
            raise Exception("⚠️ Both Primary (Hugging Face) and Fallback (Groq) APIs are currently down.")