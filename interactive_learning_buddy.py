import streamlit as st  
import google.generativeai as genai
from dotenv import load_dotenv
import os

st.set_page_config(
    page_title="AI Learning companion for Dyslexic/ADHD Students", 
    page_icon="🤖", 
    layout="wide"
)

load_dotenv()
API_KEY = os.getenv("GENAI_API_KEY")
genai.configure(api_key=API_KEY)

if not API_KEY:
    st.warning(
        "GENAI_API_KEY not found. Create a file named .env and add:\nGENAI_API_KEY=your_api_key_here"
    )
    genai_client_configured = False
    model = None
else:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        genai_client_configured = True
    except Exception as e:
        st.error(f"Failed to configure generative API client: {e}")
        genai_client_configured = False


# ================== 🎨 Base Styles ==================
# Keep base styling small and rely on dynamic controls for accessibility.
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background-color: #fbfbff;
        color: #0f172a;
    }
    .gradient-header { padding: 1rem; border-radius: 0.6rem; margin-bottom: 1rem; }
    .sidebar-card { padding: 0.8rem; border-radius: 0.5rem; margin-bottom: 0.8rem; }
    .history-card { border-radius: 0.6rem; padding: 0.9rem; margin-bottom: 0.9rem; background: #fff; }
    .muted { color: #64748b; }
</style>
""", unsafe_allow_html=True)


# ================== 🤖 Functions ==================
def get_response(prompt, difficulty="intermediate"):
    """Generate educational response based on difficulty level"""
    difficulty_prompts = {
        "beginner": "Explain this in simple terms for a beginner: ",
        "intermediate": "Provide a detailed explanation of: ",
        "advanced": "Give an in-depth technical analysis of: "
    }
    
    full_prompt = f"{difficulty_prompts[difficulty]}{prompt}"
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None


def save_to_history(question, answer):
    if 'history' not in st.session_state:
        st.session_state.history = []
    st.session_state.history.append({
        "question": question,
        "answer": answer
    })


def save_note(text):
    if 'notes' not in st.session_state:
        st.session_state.notes = []
    st.session_state.notes.append(text)


# ================== 📌 Layout ==================
with st.container():
    st.markdown('<div class="gradient-header"><h1>🤖 AI Learning Buddy</h1></div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-card"><h2>⚙️ Settings</h2>', unsafe_allow_html=True)
        difficulty = st.select_slider(
            "Select difficulty level",
            options=["beginner", "intermediate", "advanced"],
            value=st.session_state.get('difficulty_slider', 'intermediate'),
            key="difficulty_slider"
        )

        st.markdown('---')
        st.markdown('### Accessibility')
        font_size = st.slider('Answer font size', min_value=14, max_value=28, value=16, key='font_size')
        high_contrast = st.checkbox('High contrast mode', value=False, key='high_contrast')

        st.markdown('---')
        st.markdown('### Quick prompts')
        # quick prompt buttons that populate the textarea
        if st.button('Explain like I am 5'):
            st.session_state.learn_prompt = 'Explain this topic like I am 5 years old.'
        if st.button('Step-by-step guide'):
            st.session_state.learn_prompt = 'Provide a step-by-step guide for this topic.'
        if st.button('Provide examples'):
            st.session_state.learn_prompt = 'Give concrete examples for this topic.'

        st.markdown('</div>', unsafe_allow_html=True)

    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📚 Learn", "🧩 Quiz", "📈 Review"])

    with tab1:
        st.subheader("📚 Learn Something New")
        user_prompt = st.text_area(
            "💡 What would you like to learn about?",
            key="learn_prompt",
            height=100
        )
        
        if st.button("✨ Get Answer", key="learn_button", use_container_width=True):
            if user_prompt:
                if not genai_client_configured:
                    st.error("API key not configured. Add GENAI_API_KEY to your .env or environment.")
                else:
                    with st.spinner("Generating response..."):
                        response = get_response(user_prompt, difficulty)
                        if response:
                            st.success("✅ Here's your explanation:")
                            # Display with adjustable font size and optional high contrast
                            st.markdown(f"<div style='font-size: {font_size}px; color: {'#000' if high_contrast else '#0f172a'}'>{response}</div>", unsafe_allow_html=True)
                            # Action buttons
                            cols = st.columns([1,1,2])
                            with cols[0]:
                                if st.button("📋 Copy Answer"):
                                    st.write("Answer copied to clipboard (use browser copy if not supported).")
                            with cols[1]:
                                if st.button("🔊 Read Aloud"):
                                    # Simple TTS via browser - using HTML <audio> requires creating an audio file; instead, provide a short instruction.
                                    st.info("Use your OS/browser reader or install a browser extension for text-to-speech.\nFuture versions may include built-in TTS.")
                            with cols[2]:
                                note = st.text_input("Add a quick note from this answer:")
                                if st.button("💾 Save Note") and note:
                                    save_note(note)
                                    st.success("Note saved")

                            save_to_history(user_prompt, response)
            else:
                st.warning("⚠️ Please enter a question")

    with tab2:
        st.subheader("🧩 Generate Quiz")
        quiz_topic = st.text_input(
            "Enter a topic for a quick quiz:",
            key="quiz_topic"
        )
        
        if st.button("📝 Generate Quiz", key="quiz_button", use_container_width=True):
            if quiz_topic:
                if not genai_client_configured:
                    st.error("API key not configured. Add GENAI_API_KEY to your .env or environment.")
                else:
                    with st.spinner("Creating your quiz..."):
                        quiz_prompt = f"Create a 3-question quiz about {quiz_topic} suitable for {difficulty} level"
                        quiz = get_response(quiz_prompt, difficulty)
                        if quiz:
                            st.success("📌 Here's your quiz:")
                            st.markdown(f"<div style='font-size: {font_size}px'>{quiz}</div>", unsafe_allow_html=True)
            else:
                st.warning("⚠️ Please enter a topic for the quiz")

    with tab3:
        st.subheader("📈 Learning History")
        if 'history' not in st.session_state or len(st.session_state.history) == 0:
            st.info("ℹ️ No history available yet. Start learning to see your previous topics here!")
        else:
            for i, item in enumerate(st.session_state.history):
                st.markdown(f"""
                <div class="history-card">
                    <h4>📖 Question:</h4>
                    <p style='font-size: {font_size}px'>{item['question']}</p>
                    <h4>💡 Answer:</h4>
                    <p style='font-size: {font_size}px'>{item['answer']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        if st.button("🗑️ Clear History", key="clear_history", use_container_width=True):
            st.session_state.history = []
            st.success("✅ History cleared successfully!")
