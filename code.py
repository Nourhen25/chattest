import streamlit as st
import requests
import os
import re
import time

# Together AI API Key (Use environment variable or Streamlit secrets)
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "85b9952e2ec424e60e2be7e243963eb121dd91bb33f6b9afd8a9ee1d6a114e47")

# Cooldown timer
if "last_request_time" not in st.session_state:
    st.session_state.last_request_time = 0
cooldown_seconds = 10

# Function to detect suicidal thoughts
def contains_suicidal_thoughts(user_message):
    keywords = [
        "suicide", "kill myself", "end my life", "i wanna die", "no reason to live",
        "give up", "can't go on", "hurt myself", "self harm", "nothing matters"
    ]
    return any(keyword in user_message.lower() for keyword in keywords)

# Function to detect loneliness-related messages
def contains_loneliness_keywords(user_message):
    loneliness_keywords = [
        "i don’t have friends", "i feel alone", "no one cares about me", "i am lonely",
        "how to make friends", "i have no one", "no one to talk to"
    ]
    return any(keyword in user_message.lower() for keyword in loneliness_keywords)

# Clean model reasoning/thinking tags
def clean_thinking_tags(text):
    if not text:
        return text

    patterns = [
        r'<think>.*?</think>',
        r'<think>.*',
        r'\[thinking\].*?\[/thinking\]',
        r'<thinking>.*?</thinking>',
        r'.*?thinking:.*?\n',
        r'\*thinking\*.*?\*',
    ]
    cleaned_text = text
    for pattern in patterns:
        cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.DOTALL | re.IGNORECASE)
    cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
    return cleaned_text.strip()

# Get response from Together AI
def get_response_from_together(messages):
    try:
        api_url = "https://api.together.xyz/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        final_messages = messages.copy()
        final_messages.append({
            "role": "system",
            "content": "IMPORTANT: Do not include any thinking tags or show your reasoning. Respond directly to the user."
        })

        data = {
            "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
            "messages": final_messages,
            "temperature": 0.3,
            "max_tokens": 500
        }

        response = requests.post(api_url, headers=headers, json=data)

        if response.status_code == 429:
            return "🚫 We're currently experiencing high demand. Please wait a few moments and try again."

        elif response.status_code == 200:
            raw_response = response.json()["choices"][0]["message"]["content"]
            return clean_thinking_tags(raw_response)
        else:
            return f"⚠️ An error occurred: {response.status_code} - {response.text}"
    except Exception as e:
        return f"⚠️ Unexpected error: {str(e)}"

# UI Styling
st.markdown(
    """
    <style>
    .stApp { background-color: #388E3C !important; }
    .stTextInput > div > div > input { background-color: white; color: black; }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit UI
st.title("💬 ZenMind - Mental Health Chatbot")
st.write("This chatbot provides **hope and motivation** while offering mental health support in **Qatar**.")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = {
        "role": "system",
        "content": """
🚨 IMPORTANT: DO NOT include any <think> tags or thinking process in your responses. Respond directly to the user without showing your reasoning.
🚨 IMPORTANT: If a user expresses suicidal thoughts, ALWAYS respond with this message:

💙 Thank you for trusting me with something so difficult. I'm really sorry you're feeling this way, and I want you to know that you're not alone. What you're experiencing matters, and there are people who want to help. Please reach out for immediate support - you deserve kindness and care. In Qatar, you can contact:
📞 Mental Health Helpline: 16000 (Available 24/7)
📞 Hamad Medical Corporation: +974 4439 5777
📞 Emergency Services: 999
These professionals are trained to help during moments like this. It's brave to ask for help, and you don't have to face these feelings alone. Would you like me to stay with you while you call?

---

You are a supportive and empathetic mental health assistant. Your job is to comfort users, validate their feelings, and gently encourage them to seek professional help when necessary.

- Be warm and engaging – like a caring friend.
- Never dismiss the user's feelings.
- Avoid generic or robotic answers.
- Respond with compassion, kindness, and humanity.
        """
    }

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Type your message here...")

if user_input:
    current_time = time.time()
    if current_time - st.session_state.last_request_time < cooldown_seconds:
        st.warning("⏳ Let’s take a breath. Please wait a few seconds before sending another message.")
    else:
        st.session_state.last_request_time = current_time
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Predefined responses
        if contains_suicidal_thoughts(user_input):
            response = """
💙 Thank you for trusting me with something so difficult. I'm really sorry you're feeling this way, and I want you to know that you're not alone. What you're experiencing matters, and there are people who want to help. Please reach out for immediate support - you deserve kindness and care. In Qatar, you can contact:
📞 Mental Health Helpline: 16000 (Available 24/7)  
📞 Hamad Medical Corporation: +974 4439 5777  
📞 Emergency Services: 999  
These professionals are trained to help during moments like this. It's brave to ask for help, and you don’t have to face this alone. Would you like me to stay with you while you call?
            """
        elif contains_loneliness_keywords(user_input):
            response = """
💙 I'm really sorry you're feeling this way. Loneliness can be really tough, but please know that you're not alone in this. Many people feel the same way, and there are ways to connect with others.

Here are some things you can try:
- 🌍 **Join online communities** – support groups and forums help.
- 🎨 **Start a hobby** – classes or clubs help you meet others.
- 💬 **Volunteer** – meet kind-hearted people while doing good.
- 📱 **Try therapy** – talking to a professional can truly help.

Even small steps can lead to meaningful connections. 💙 I'm here for you.
            """
        else:
            messages_for_api = [st.session_state.system_prompt] + st.session_state.messages
            with st.chat_message("assistant"):
                with st.spinner("ZenMind is typing..."):
                    response = get_response_from_together(messages_for_api)
            if not response:
                response = "I'm here with you. Can you tell me more about how you're feeling?"

        # Display response
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
