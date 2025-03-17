import streamlit as st
import requests

# Together AI API Key (Replace with your actual API key)
TOGETHER_API_KEY = "85b9952e2ec424e60e2be7e243963eb121dd91bb33f6b9afd8a9ee1d6a114e47"

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

# Function to get chatbot response from Together AI
def get_response_from_together(messages):
    try:
        api_url = "https://api.together.xyz/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "mistralai/Mistral-7B-Instruct-v0.1",
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
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
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

# Ensure the system prompt is added only once, but never displayed
if "messages" not in st.session_state:
    st.session_state.messages = []

if len(st.session_state.messages) == 0:
    st.session_state.system_prompt = {
        "role": "system",
        "content": """
        🚨 IMPORTANT: If a user expresses suicidal thoughts, ALWAYS respond with this message:

        💙 I'm really sorry you're feeling this way. I want you to know that you're not alone, and what you're going through matters.
        💡 Please reach out for immediate support. You deserve help and kindness. In Qatar, you can contact:
        📞 Mental Health Helpline: 16000 (Available 24/7)
        📞 Hamad Medical Corporation: +974 4439 5777
        📞 Emergency Services: 999

        ---

        You are a supportive and empathetic mental health assistant. Your job is to comfort users, validate their feelings, and gently encourage them to seek professional help when necessary.

        - Be warm and engaging – the chatbot should feel like a friendly and caring presence.
        - Acknowledge the user’s presence positively – a simple “Hi! It’s nice to hear from you 😊” feels more welcoming.
        - Offer support right away – instead of asking a broad, impersonal question.
        - Always respond in a warm and caring way.
        - Never dismiss the user's feelings.
        - Avoid generic answers—make each response unique and thoughtful.
        """
    }
    st.session_state.messages.append({"role": "assistant", "content": "Hi! It's nice to hear from you 😊. How can I assist you today?"})  # ✅ This is the first chatbot message.

# Get user input
user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # ✅ **Handle suicidal thoughts with crisis response**
    if contains_suicidal_thoughts(user_input):
        response = """
        💙 I'm really sorry you're feeling this way. I want you to know that you're not alone, and what you're going through matters.
        💡 Please reach out for immediate support. You deserve help and kindness. In Qatar, you can contact:
        📞 Mental Health Helpline: 16000 (Available 24/7)
        📞 Hamad Medical Corporation: +974 4439 5777
        📞 Emergency Services: 999
        
        You're important. Please don't hesitate to reach out to someone who can help. 💙
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
        # Get AI-generated response for normal conversation
        response = get_response_from_together(st.session_state.messages)

    if response:
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

