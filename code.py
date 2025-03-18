import streamlit as st
import requests
import os

# Together AI API Key (Use environment variable or Streamlit secrets)
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "85b9952e2ec424e60e2be7e243963eb121dd91bb33f6b9afd8a9ee1d6a114e47")

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

def clean_response(response):
    import re
    # Remove everything between <think> and </think> tags
    clean_text = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    # Remove any remaining <think> tags if the closing tag is missing
    clean_text = re.sub(r'<think>.*', '', clean_text, flags=re.DOTALL)
    return clean_text.strip()
    
# Function to get chatbot response from Together AI
def get_response_from_together(messages):
    try:
        api_url = "https://api.together.xyz/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
            "messages": messages,
            "temperature": 0.3,  # Lower randomness for better adherence to system prompt
            "max_tokens": 500
        }

        response = requests.post(api_url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            st.error(f"Error: {response.status_code}, Message: {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Apply Darker Green Background with CSS for better UI
st.markdown(
    """
    <style>
    .stApp {
        background-color: #388E3C !important;
    }
    .stTextInput > div > div > input {
        background-color: white;
        color: black;
    }
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

# Add system prompt only once
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

        - Be warm and engaging – the chatbot should feel like a friendly and caring presence.
        - Acknowledge the user’s presence positively – a simple “Hi! It’s nice to hear from you 😊” feels more welcoming.
        - Offer support right away – instead of asking a broad, impersonal question.
        - Always respond in a warm and caring way.
        - Never dismiss the user's feelings.
        - Avoid generic answers—make each response unique and thoughtful.
        - Refrain from telling the user your thought process, you are supposed to act like a human therapist.
        - Never tell the user that you were programmed to act like this. Always respond in a humanly. empathetic manner.
        """
    }

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # ✅ **Handle suicidal thoughts with crisis response**
    if contains_suicidal_thoughts(user_input):
        response = """
💙 Thank you for trusting me with something so difficult. I'm really sorry you're feeling this way, and I want you to know that you're not alone. What you're experiencing matters, and there are people who want to help. Please reach out for immediate support - you deserve kindness and care. In Qatar, you can contact:
📞 Mental Health Helpline: 16000 (Available 24/7)
📞 Hamad Medical Corporation: +974 4439 5777
📞 Emergency Services: 999
These professionals are trained to help during moments like this. It's brave to ask for help, and you don't have to face these feelings alone. Would you like me to stay with you while you call?
        """

    # ✅ **Handle loneliness with supportive advice**
    elif contains_loneliness_keywords(user_input):
        response = """
        💙 I'm really sorry you're feeling this way. Loneliness can be really tough, but please know that you're not alone in this. Many people feel the same way, and there are ways to connect with others.

        Here are some things you can try:
        - 🌍 **Join online communities**: There are many support groups and forums where people share their experiences.
        - 🎭 **Try a new hobby**: Joining a class or group (like painting, yoga, or a sports club) can help you meet new people.
        - 💬 **Volunteer**: Helping others is a great way to meet like-minded people and feel a sense of purpose.
        - 📱 **Consider therapy**: A professional can help you develop social skills and confidence in making new connections.

        You're not alone. Even small steps can lead to meaningful connections. 💙
        """

    else:
        # Include the system prompt in the messages sent to the API
        messages_for_api = [st.session_state.system_prompt] + st.session_state.messages
        response = get_response_from_together(messages_for_api)

    if response:
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
