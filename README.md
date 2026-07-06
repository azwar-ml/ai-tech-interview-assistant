# 💻 AI Tech Interview Prep Assistant

A production-grade, multi-session chatbot application built using **Streamlit** and the **Hugging Face Serverless Inference API**. This system functions as an interactive Technical Interview Coach, featuring stateful memory tracking, responsive error management, and protective prompt-engineering limits.

## 🚀 Key Architectural Features

* **Advanced Prompt Engineering:** Utilizes a strict, role-enforced System Prompt setting boundaries for formatting and tone.
* **Exploit Protection (Anti-Crash Guardrails):** Includes hard tokens constraints (`max_tokens=300`) to physically cut off adversarial loop requests (such as *"count to a million"*), protecting downstream execution context.
* **Dynamic Multi-Session Storage:** Implements structural dictionary stacks powered by Streamlit Session State and `uuid` markers, allowing users to spin up new chats, switch between topics, or delete specific logs seamlessly.
* **Graceful API Handling:** All endpoint interactions are safely wrapped inside proactive exception monitors, piping diagnostic feedback cleanly to the UI layer during a failure condition.

## 📁 Directory Setup

```text
Task6-Chatbot/
│
├── .env                # Private Hugging Face access token credential
├── .gitignore          # Prevents pushing sensitive files (.env) to GitHub
├── requirements.txt    # Managed application dependencies
├── app.py              # Single-file full-stack Python script (UI + Logic)
└── README.md           # Instructional submission document