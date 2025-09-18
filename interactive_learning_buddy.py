import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

# --------------------
# 🔹 Setup
# --------------------
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.sidebar.warning("⚠️ GOOGLE_API_KEY not found. Please set it in .env or sidebar below.")
    api_key_input = st.sidebar.text_input("Enter your Google API Key:", type="password")
    if api_key_input:
        api_key = api_key_input

genai.configure(api_key=api_key)

# Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(
    page_title="Interactive Learning Buddy",
    page_icon="📘",
    layout="wide",
)

# --------------------
# 🔹 Custom CSS (Website Look)
# --------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f9a8d4, #a78bfa, #60a5fa);
        font-family: "Segoe UI", sans-serif;
        color: #1e293b;
    }
    h1, h2, h3 {
        color: #0f172a;
        font-weight: bold;
    }
    .stTabs [role="tablist"] {
        gap: 15px;
        justify-content: center;
    }
    .stTabs [role="tab"] {
        background: rgba(255, 255, 255, 0.7);
        padding: 12px 20px;
        border-radius: 12px;
        font-weight: 600;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    }
    .stTabs [role="tab"]:hover {
        background: #2563eb;
        color: white !important;
        transform: scale(1.05);
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.85);
        padding: 20px;
        border-radius: 18px;
        box-shadow: 0px 6px 16px rgba(0,0,0,0.25);
        margin-bottom: 20px;
        backdrop-filter: blur(8px);
    }
    .response-box {
        background: rgba(255, 255, 255, 0.9);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
        border-left: 6px solid #9333ea;
        margin-top: 12px;
    }
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 20px;
    }
    .stButton button {
        background: linear-gradient(135deg, #4f46e5, #9333ea);
        color: white;
        border-radius: 10px;
        font-size: 16px;
        font-weight: bold;
        padding: 10px 24px;
        transition: all 0.3s ease;
        border: none;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #2563eb, #4f46e5);
        transform: scale(1.05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------
# 🔹 Session State
# --------------------
if "history" not in st.session_state:
    st.session_state.history = []
if "settings" not in st.session_state:
    st.session_state.settings = {"difficulty": "Medium", "mode": "Learn", "response_length": "Long"}

# --------------------
# 🔹 Helper: Gemini Query
# --------------------
def ask_gemini(prompt: str):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error: {e}"

# --------------------
# 🔹 Sidebar (Settings)
# --------------------
with st.sidebar:
    st.title("⚙️ Settings Panel")
    st.session_state.settings["difficulty"] = st.radio(
        "Select Difficulty:", ["Easy", "Medium", "Hard"], index=1
    )
    st.session_state.settings["mode"] = st.selectbox(
        "Learning Mode:", ["Learn", "Quiz"]
    )
    st.session_state.settings["response_length"] = st.radio(
        "Response Length:", ["Short", "Medium", "Long"], index=2
    )
    st.markdown("---")
    st.info("Use the tabs to explore features 📘📝📜⚙️")

# --------------------
# 🔹 Hero Section
# --------------------
st.markdown(
    """
    <div style='text-align: center; padding: 25px;'>
        <h1>📘 Interactive Learning Buddy</h1>
        <p style="font-size:18px; color:#0f172a;">
            Your AI-powered companion to <b>Learn Smarter</b>, <b>Test Yourself</b>, 
            and <b>Track Progress</b>. 🚀
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------
# 🔹 Determine Prompt Detail Based on Length
# --------------------
def get_length_detail(length_option: str):
    if length_option == "Short":
        return "Give a brief answer in 3-4 sentences."
    elif length_option == "Medium":
        return "Give a detailed answer in 2-3 paragraphs with examples."
    else:
        return "Write a very long, structured answer with 5+ paragraphs, examples, and applications."

length_detail = get_length_detail(st.session_state.settings["response_length"])

# --------------------
# Tabs Layout
# --------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📖 Learn", "📝 Quiz", "📜 History", "⚙️ Settings"]
)

# --------------------
# 📖 Learn Section
# --------------------
with tab1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.header("📖 Learn Something New")
    topic = st.text_input("Enter a topic to explore:", "")
    if st.button("✨ Learn Now", key="learn_btn"):
        if topic:
            with st.spinner("🔍 Fetching detailed explanation..."):
                prompt = f"Explain {topic}. {length_detail}"
                explanation = ask_gemini(prompt)
            st.success("Here’s what I found:")
            st.markdown(f"<div class='response-box'>{explanation}</div>", unsafe_allow_html=True)
            st.session_state.history.append(
                {"type": "learn", "topic": topic, "response": explanation}
            )
        else:
            st.warning("⚠️ Please enter a topic.")
    st.markdown("</div>", unsafe_allow_html=True)

# --------------------
# 📝 Quiz Section
# --------------------
with tab2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.header("📝 Take a Quiz")
    subject = st.text_input("Enter a subject for quiz:", "")
    if st.button("🚀 Start Quiz", key="quiz_btn"):
        if subject:
            diff = st.session_state.settings["difficulty"]
            with st.spinner("🧠 Generating quiz question..."):
                prompt = (
                    f"Generate one {diff} level quiz question on {subject}. "
                    f"Provide the question first, then a detailed step-by-step solution, "
                    f"and a final correct answer. {length_detail}"
                )
                quiz_q = ask_gemini(prompt)
            st.success("Here’s your quiz:")
            st.markdown(f"<div class='response-box'>{quiz_q}</div>", unsafe_allow_html=True)
            st.session_state.history.append(
                {"type": "quiz", "subject": subject, "response": quiz_q}
            )
        else:
            st.warning("⚠️ Please enter a subject.")
    st.markdown("</div>", unsafe_allow_html=True)

# --------------------
# 📜 History Section
# --------------------
with tab3:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.header("📜 Your Learning & Quiz History")
    if st.session_state.history:
        for i, entry in enumerate(reversed(st.session_state.history), 1):
            with st.expander(f"{entry['type'].title()} - {i}"):
                st.write(f"**Input:** {entry.get('topic') or entry.get('subject')}")
                st.markdown(f"<div class='response-box'>{entry['response']}</div>", unsafe_allow_html=True)
    else:
        st.info("No history yet. Start learning or take a quiz!")
    st.markdown("</div>", unsafe_allow_html=True)

# --------------------
# ⚙️ Settings Tab
# --------------------
with tab4:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.header("⚙️ Adjust Your Settings")
    st.write("Use the sidebar to change difficulty, mode, and response length.")
    st.json(st.session_state.settings)
    st.markdown("</div>", unsafe_allow_html=True)
