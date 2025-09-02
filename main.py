import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
from google.api_core.exceptions import DeadlineExceeded

# Load environment variables
load_dotenv()
password = os.getenv("password")

# Invesho Password
def check_password():
    def password_entered():
        if st.session_state["password"] == password:  
            st.session_state["password_correct"] = True
            del st.session_state["password"] 
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Ask for password
        st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
        st.error("❌ Incorrect password. Try again.")
        return False
    else:
        return True

if not check_password():
    st.stop()

# Configure Streamlit page settings
st.set_page_config(
    page_title="LLM Reply system for Invesho",
    page_icon=":brain:",  
    layout="centered",  
)  

from PIL import Image
import base64

logo_path = "invesho_logo.png"
with open(logo_path, "rb") as f:
    data = f.read()
    encoded_logo = base64.b64encode(data).decode()

st.markdown(
    f"""
    <div style="text-align: center; margin-top: -20px; margin-bottom: 10px;">
        <a href="https://www.invesho.com" target="_blank">
            <img src="data:image/png;base64,{encoded_logo}" alt="Invesho Logo" width="100" />
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Google Gemini-Pro AI model
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('models/gemini-2.0-flash')

def translate_role_for_streamlit(user_role):
    return "assistant" if user_role == "model" else user_role

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[
        {
            "role": "model",
            "parts": ["Hi! 👋 Please share the post content or URL to generate a smart reply."]
        }
    ])

# Display the chatbot's title on the page
st.title("🤖 Invesho - LLM Reply generator")

# Display the chat history
for message in st.session_state.chat_session.history:
    with st.chat_message(translate_role_for_streamlit(message.role)):
        st.markdown(message.parts[0].text)

# Input field for user's message
user_prompt = st.chat_input("Ask Gemini-Pro...")
if user_prompt:
    # Add user's message to chat and display it
    st.chat_message("user").markdown(user_prompt)

    # Wrap user prompt in brand voice instruction
    prompt = f"""You're replying as Invesho, an AI fundraising co-pilot that helps startups find investors and manage their fundraising. 
Respond politely ,professionally, helpfully, and in a tone aligned with startup founders or VCs, always tag @InveshoAI .
Please format the response in 3 short lines, with spacing between them.
Kindly avoid using hashtags.

Here is the post content or link you need to reply to:
\"\"\"{user_prompt}\"\"\"
"""

    try:
        gemini_response = st.session_state.chat_session.send_message(prompt)

        # Show Gemini reply
        with st.chat_message("assistant"):
            st.markdown(gemini_response.parts[0].text)

    except DeadlineExceeded:
        st.error("⚠️ The request to Gemini timed out. Please try again later or simplify your prompt.")
    except Exception as e:
        st.error("⚠️ An unexpected error occurred while contacting Gemini.")
        with st.expander("See details"):
            st.exception(e)
