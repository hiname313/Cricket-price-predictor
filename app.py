import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pulp import LpMaximize, LpProblem, LpVariable, lpSum
import os
from dotenv import load_dotenv
import joblib
from google import genai
from google.genai import types
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load environment variables
load_dotenv()

# Page configuration with modern styling
st.set_page_config(
    page_title="Cricket Analytics Project",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed"  # We'll handle navigation ourselves
)

# Initialize session state for page navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏆 Best XI Team Builder"

# COMPLETELY NEW SIDEBAR SOLUTION - Always visible custom navigation
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Roboto:wght@300;400;500;700&display=swap');
    
    /* Hide default Streamlit sidebar completely */
    .css-1d391kg, [data-testid="stSidebar"] {
        display: none !important;
    }
    
    
    /* Navigation buttons */
    .nav-section {
        padding: 1.5rem;
    }
    
    .nav-button {
        display: block;
        width: 100%;
        background: rgba(255,255,255,0.05);
        color: white;
        border: 2px solid rgba(50, 205, 50, 0.3);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 0.8rem 0;
        font-size: 1rem;
        font-weight: 500;
        text-align: left;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        font-family: 'Poppins', sans-serif;
    }
    
    .nav-button:hover {
        background: rgba(50, 205, 50, 0.2);
        border-color: #32CD32;
        transform: translateX(8px);
        box-shadow: 0 4px 12px rgba(50, 205, 50, 0.3);
        color: #90EE90;
    }
    
    .nav-button.active {
        background: linear-gradient(135deg, #32CD32 0%, #2E8B57 100%);
        border-color: #32CD32;
        color: white;
        font-weight: 600;
        transform: translateX(12px);
        box-shadow: 0 6px 20px rgba(50, 205, 50, 0.4);
    }
    
    .nav-button.active:hover {
        background: linear-gradient(135deg, #90EE90 0%, #32CD32 100%);
    }
    
    /* Stats section in sidebar */
    .sidebar-stats {
        background: rgba(255,255,255,0.05);
        margin: 1.5rem;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(50, 205, 50, 0.3);
    }
    
    .sidebar-stats h4 {
        color: #32CD32;
        text-align: center;
        margin-bottom: 1rem;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    .sidebar-stats p {
        color: rgba(255,255,255,0.8);
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        font-size: 0.9rem;
    }
    
    .sidebar-stats strong {
        color: #90EE90;
    }
    
    /* Adjust main content for custom sidebar */
    .main .block-container {
        margin-left: 340px;
        max-width: calc(100% - 360px);
        padding-left: 2rem;
    }
    
    /* Global Styles */
    .main {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Toggle button for mobile */
    .sidebar-toggle {
        display: none;
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 10000;
        background: #2E8B57;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.8rem;
        cursor: pointer;
        font-size: 1.2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    .sidebar-toggle:hover {
        background: #32CD32;
    }
    
    /* Cricket-themed Header */
    .main-header {
        background: linear-gradient(135deg, #2E8B57 0%, #228B22 25%, #32CD32 50%, #90EE90 75%, #98FB98 100%);
        padding: 3rem 2rem;
        border-radius: 25px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: "🏏";
        position: absolute;
        font-size: 120px;
        opacity: 0.1;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    
    .main-header h1 {
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        z-index: 1;
        position: relative;
    }
    
    .main-header p {
        font-size: 1.4rem;
        opacity: 0.95;
        font-weight: 400;
        z-index: 1;
        position: relative;
    }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border-left: 5px solid #32CD32;
        margin: 1rem 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 50px rgba(0,0,0,0.15);
        border-left: 5px solid #228B22;
    }
    
    .feature-card::before {
        content: "";
        position: absolute;
        top: 0;
        right: 0;
        width: 100px;
        height: 100px;
        background: linear-gradient(45deg, #32CD32, #90EE90);
        opacity: 0.1;
        border-radius: 50%;
        transform: translate(30px, -30px);
    }
    
    /* Stats Cards */
    .stats-card {
        background: linear-gradient(135deg, #2E8B57 0%, #32CD32 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 10px 25px rgba(46, 139, 87, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stats-card:hover {
        transform: scale(1.05);
        box-shadow: 0 15px 35px rgba(46, 139, 87, 0.4);
    }
    
    .stats-card::after {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #FFD700, #FFA500, #FF6347);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Chat Styling */
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1.5rem;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 20px;
        margin: 1rem 0;
        border: 2px solid #e2e8f0;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .chat-message {
        padding: 1.5rem;
        border-radius: 20px;
        margin: 1rem 0;
        animation: slideIn 0.3s ease-out;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .user-message {
        background: linear-gradient(135deg, #2E8B57 0%, #32CD32 100%);
        color: white;
        margin-left: 15%;
        border-bottom-right-radius: 8px;
        border-top-right-radius: 20px;
    }
    
    .user-message::before {
        content: "👤";
        position: absolute;
        left: -40px;
        top: 50%;
        transform: translateY(-50%);
        background: white;
        padding: 8px;
        border-radius: 50%;
        font-size: 1.2rem;
    }
    
    .ai-message {
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        color: #1e293b;
        margin-right: 15%;
        border: 2px solid #e2e8f0;
        border-bottom-left-radius: 8px;
        border-top-left-radius: 20px;
    }
    
    .ai-message::before {
        content: "🤖";
        position: absolute;
        right: -40px;
        top: 50%;
        transform: translateY(-50%);
        background: #2E8B57;
        color: white;
        padding: 8px;
        border-radius: 50%;
        font-size: 1.2rem;
    }
    
    /* Form Styling */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #2E8B57 0%, #32CD32 100%);
        color: white;
        border-radius: 12px;
        border: none;
        font-weight: 500;
    }
    
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
        transition: all 0.3s ease;
        font-family: 'Roboto', sans-serif;
    }
    
    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus {
        border-color: #32CD32;
        box-shadow: 0 0 0 3px rgba(50, 205, 50, 0.1);
        outline: none;
    }
    
    /* Enhanced Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #2E8B57 0%, #32CD32 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2.5rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 20px rgba(46, 139, 87, 0.3);
        text-transform: uppercase;
        letter-spacing: 1px;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(46, 139, 87, 0.4);
        background: linear-gradient(135deg, #32CD32 0%, #90EE90 100%);
    }
    
    .stButton > button::before {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.6s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    /* Sample Question Buttons */
    .sample-question-btn {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        color: #2E8B57;
        border: 2px solid #32CD32;
        border-radius: 25px;
        padding: 1rem;
        margin: 0.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        text-align: left;
    }
    
    .sample-question-btn:hover {
        background: linear-gradient(135deg, #32CD32 0%, #90EE90 100%);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(50, 205, 50, 0.3);
    }
    
    /* Player Card Styling */
    .player-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #32CD32;
        margin: 0.5rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .player-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        border-left-color: #2E8B57;
    }
    
    /* Performance Metrics */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .metric-item {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .metric-item:hover {
        border-color: #32CD32;
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(50, 205, 50, 0.1);
    }
    
    /* Data Frame Styling */
    .dataframe {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border: none;
    }
    
    .dataframe th {
        background: linear-gradient(135deg, #2E8B57 0%, #32CD32 100%);
        color: white;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, #32CD32 0%, #90EE90 100%);
        border-radius: 15px;
        border: none;
        color: white;
        font-weight: 500;
    }
    
    .stError {
        background: linear-gradient(135deg, #FF6B6B 0%, #FFE66D 100%);
        border-radius: 15px;
        border: none;
        color: white;
        font-weight: 500;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #FFA726 0%, #FFCC02 100%);
        border-radius: 15px;
        border: none;
        color: white;
        font-weight: 500;
    }
    
    /* Animated Elements */
    @keyframes slideIn {
        from { 
            opacity: 0; 
            transform: translateX(-20px); 
        }
        to { 
            opacity: 1; 
            transform: translateX(0); 
        }
    }
    
    @keyframes fadeInUp {
        from { 
            opacity: 0; 
            transform: translateY(30px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }
    
    .fade-in {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        border: 2px solid #32CD32;
        color: #2E8B57;
        font-weight: 600;
    }
    
    .streamlit-expanderContent {
        border: 2px solid #e2e8f0;
        border-top: none;
        border-radius: 0 0 12px 12px;
        background: white;
    }
    
    /* File Uploader */
    .stFileUploader {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
        border: 2px dashed #32CD32;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #2E8B57 0%, #32CD32 100%);
        border-radius: 10px;
    }
    
    /* Loading Spinner */
    .stSpinner {
        color: #32CD32;
    }
    
    /* Footer */
    .footer {
        background: linear-gradient(135deg, #2E8B57 0%, #1e3a8a 100%);
        color: white;
        text-align: center;
        padding: 3rem 2rem;
        border-radius: 25px;
        margin-top: 3rem;
        position: relative;
        overflow: hidden;
    }
    
    .footer::before {
        content: "🏆🏏⚡";
        position: absolute;
        font-size: 80px;
        opacity: 0.1;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        letter-spacing: 30px;
    }
    
    .footer h3 {
        font-size: 2rem;
        margin-bottom: 1rem;
        z-index: 1;
        position: relative;
    }
    
    .footer p {
        z-index: 1;
        position: relative;
        margin: 0.5rem 0;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .custom-sidebar {
            transform: translateX(-100%);
            transition: transform 0.3s ease;
        }
        
        .custom-sidebar.mobile-open {
            transform: translateX(0);
        }
        
        .sidebar-toggle {
            display: block !important;
        }
        
        .main .block-container {
            margin-left: 0;
            max-width: 100%;
            padding-left: 1rem;
        }
        
        .main-header h1 {
            font-size: 2.5rem;
        }
        
        .main-header p {
            font-size: 1rem;
        }
        
        .chat-message {
            margin-left: 5% !important;
            margin-right: 5% !important;
        }
        
        .stat-value {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)



# Page selection logic 
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🤖 Cricket AI Chatbot", key="nav1", use_container_width=True, 
                 type="primary" if st.session_state.current_page == "🤖 Cricket AI Chatbot" else "secondary"):
        st.session_state.current_page = "🤖 Cricket AI Chatbot"
        st.rerun()

with col2:
    if st.button("💰 Price Predictor", key="nav2", use_container_width=True,
                 type="primary" if st.session_state.current_page == "💰 Price Predictor" else "secondary"):
        st.session_state.current_page = "💰 Price Predictor"
        st.rerun()

with col3:
    if st.button("🏆 Best XI Team Builder", key="nav3", use_container_width=True,
                 type="primary" if st.session_state.current_page == "🏆 Best XI Team Builder" else "secondary"):
        st.session_state.current_page = "🏆 Best XI Team Builder"
        st.rerun()

# Initialize Gemini client
@st.cache_resource
def init_gemini():
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return None

# Load price prediction model
@st.cache_resource
def load_price_model():
    try:
        return joblib.load("best_price_model.pkl")
    except:
        st.warning("⚠️ Price prediction model not found. Please ensure 'best_price_model.pkl' is in the project directory.")
        return None

# Initialize resources
gemini_client = init_gemini()
price_model = load_price_model()

# Enhanced Main Header
st.markdown("""
<div class="main-header">
    <h1>🏏 Cricket Analytics Pro</h1>
    <p>Advanced AI-Powered Cricket Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# CRICKET AI CHATBOT 
# ============================================================================
if st.session_state.current_page == "🤖 Cricket AI Chatbot":
    st.markdown("""
    <div class="feature-card fade-in">
        <h2 style="color: #2E8B57; margin-bottom: 1rem; display: flex; align-items: center; gap: 10px;">
            🤖 Cricket AI Chatbot <span style="font-size: 1rem; background: linear-gradient(135deg, #32CD32, #90EE90); color: white; padding: 0.3rem 0.8rem; border-radius: 20px;">Powered by Gemini AI</span>
        </h2>
        <p style="color: #666; font-size: 1.1rem; margin-bottom: 0;">Ask me anything about IPL Auctions, Best XI Teams, Players, Cricket Stats, and Match Analysis!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""

    # Function to handle submit
    def handle_submit():
        user_question = st.session_state.user_input.strip()
        if not user_question:
            return

        # Add user message to history
        st.session_state.chat_history.append(("user", user_question))

        with st.spinner("🏏 Cricket AI is analyzing your question..."):
            try:
                if gemini_client:
                    response = gemini_client.models.generate_content(
                        model="gemini-2.5-flash",
                        config=types.GenerateContentConfig(
                            system_instruction=(
                                "You are a Cricket AI expert with deep knowledge of IPL, international cricket, player statistics, team strategies, and match analysis. "
                                "You ONLY reply to queries about cricket, IPL auctions, players, stats, team formations, match predictions, and cricket strategy. "
                                "If the user asks anything unrelated to cricket, reply politely and shut down the unrelated conversation. "
                                "If it is cricket-related, reply enthusiastically with detailed, insightful explanations including statistics where relevant."
                            )
                        ),
                        contents=user_question
                    )
                    ai_reply = response.text.strip() if response.text else "⚠️ No response from Gemini."
                else:
                    ai_reply = "⚠️ Gemini AI not configured. Please add your GOOGLE_API_KEY to the .env file to unlock full AI capabilities."
            except Exception as e:
                ai_reply = f"⚠️ Error connecting to Cricket AI: {str(e)}"

        # Add AI reply to history
        st.session_state.chat_history.append(("ai", ai_reply))
        st.session_state.user_input = ""

    # Display chat history with enhanced styling
    if st.session_state.chat_history:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for role, msg in st.session_state.chat_history:
            if role == "user":
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {msg}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message ai-message"><strong>Cricket AI:</strong> {msg}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Enhanced input section
    col1, col2 = st.columns([4, 1])
    with col1:
        st.text_input(
            "Ask your cricket question:",
            key="user_input",
            placeholder="e.g., 'Who is Virat Kohli?'",
            on_change=handle_submit,
            help="Press Enter to send your question to Cricket AI"
        )
    
    with col2:
        if st.button("🚀 Send", use_container_width=True):
            handle_submit()

    

# ============================================================================
# PRICE PREDICTOR 
# ============================================================================
elif st.session_state.current_page == "💰 Price Predictor":
    st.markdown("""
    <div class="feature-card fade-in">
        <h2 style="color: #2E8B57; margin-bottom: 1rem; display: flex; align-items: center; gap: 10px;">
            💰 IPL Auction Price Predictor <span style="font-size: 1rem; background: linear-gradient(135deg, #FFD700, #FFA500); color: white; padding: 0.3rem 0.8rem; border-radius: 20px;">AI Powered</span>
        </h2>
        <p style="color: #666; font-size: 1.1rem; margin-bottom: 0;">Enter player performance statistics to predict their IPL auction value using advanced machine learning 🚀</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not price_model:
        st.error("❌ Price prediction model not loaded. Please ensure 'best_price_model.pkl' is available.")
    else:
        # Enhanced input form
        with st.form("player_form", clear_on_submit=False):
            st.markdown("### 📊 Player Performance Dashboard")
            
            # Player info section
            col1, col2 = st.columns(2)
            with col1:
                player_name = st.text_input("🏏 Player Name", placeholder="e.g., Virat Kohli")
            with col2:
                player_role = st.selectbox("👤 Primary Role", ["Batsman", "Bowler", "All-Rounder", "Wicketkeeper"])
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**🏏 Batting Performance**")
                runs_scored = st.number_input("🏃‍♂️ Total Runs", min_value=0, value=500, help="Total runs scored in the season")
                balls_faced = st.number_input("🎯 Balls Faced", min_value=1, value=400, help="Total balls faced")
                fours = st.number_input("4️⃣ Boundaries", min_value=0, value=45, help="Number of fours hit")
                sixes = st.number_input("6️⃣ Sixes", min_value=0, value=15, help="Number of sixes hit")
                dot_balls = st.number_input("⏹️ Dot Balls", min_value=0, value=150, help="Dot balls faced")
                innings_batted = st.number_input("🎪 Innings", min_value=0, value=14, help="Number of innings batted")
                strike_rate = st.number_input("⚡ Strike Rate", min_value=0.0, value=140.0, help="Batting strike rate")

            with col2:
                st.markdown("**🎳 Bowling Performance**")
                balls_bowled = st.number_input("🎳 Balls Bowled", min_value=0, value=200, help="Total balls bowled")
                runs_conceded = st.number_input("🏃‍♂️ Runs Conceded", min_value=0, value=250, help="Total runs conceded")
                economy = st.number_input("📊 Economy Rate", min_value=0.0, value=8.5, help="Bowling economy rate")
                wickets = st.number_input("🎯 Wickets", min_value=0, value=15, help="Total wickets taken")
                wicket_strike_rate = st.number_input("⚡ Bowling SR", min_value=0.0, value=18.0, help="Balls per wicket")
                boundary_percent = st.number_input("🎯 Boundary %", min_value=0.0, max_value=100.0, value=25.0, help="Percentage of runs from boundaries")

            submitted = st.form_submit_button("🔮 Predict Auction Price", use_container_width=True)

        # Enhanced prediction results 
        if submitted:
            # Calculate impact score
            impact_score = runs_scored + (20 * wickets)

            input_data = {
                'runs_scored': runs_scored,
                'balls_faced': balls_faced,
                'fours': fours,
                'sixes': sixes,
                'dot_balls': dot_balls,
                'innings_batted': innings_batted,
                'strike_rate': strike_rate,
                'balls_bowled': balls_bowled,
                'runs_conceded': runs_conceded,
                'economy': economy,
                'wickets': wickets,
                'wicket_strike_rate': wicket_strike_rate,
                'boundary_percent': boundary_percent,
                'impact_score': impact_score,
                'season': "2025"
            }

            input_df = pd.DataFrame([input_data])

            try:
                predicted_log_price = price_model.predict(input_df)[0]
                predicted_price = np.expm1(predicted_log_price)
                
                # Results display
                st.markdown("### 🎯 Prediction Results")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="stats-card">
                        <div class="stat-value">₹{predicted_price/10000000:.1f}Cr</div>
                        <div class="stat-label">Predicted Price</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="stats-card">
                        <div class="stat-value">{impact_score}</div>
                        <div class="stat-label">Impact Score</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    category = "🔥 Premium" if predicted_price > 70000000 else "⭐ Mid-tier" if predicted_price > 10000000 else "💎 Budget"
                    st.markdown(f"""
                    <div class="stats-card">
                        <div class="stat-value" style="font-size: 1.5rem;">{category}</div>
                        <div class="stat-label">Player Category</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col4:
                    avg_impact = impact_score / max(innings_batted, 1)
                    st.markdown(f"""
                    <div class="stats-card">
                        <div class="stat-value">{avg_impact:.1f}</div>
                        <div class="stat-label">Per Inning Impact</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Visualization using Plotly 
                st.markdown("### 📈 Performance Analysis Dashboard")
                
                # Create subplot
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=('Batting Performance', 'Bowling Performance', 'Strike Rate vs Economy', 'Impact Breakdown'),
                    specs=[[{"type": "bar"}, {"type": "bar"}],
                           [{"type": "scatter"}, {"type": "pie"}]]
                )
                
                # Batting performance radar
                batting_metrics = ['Runs', 'Strike Rate', 'Boundaries', 'Consistency']
                batting_values = [
                    min(runs_scored/10, 100),
                    min(strike_rate/2, 100),
                    min((fours + sixes*1.5)*2, 100),
                    min(100 - (dot_balls/max(balls_faced,1)*100), 100)
                ]
                
                fig.add_trace(
                    go.Bar(x=batting_metrics, y=batting_values, 
                          marker_color=['#2E8B57', '#32CD32', '#90EE90', '#98FB98'],
                          name='Batting'),
                    row=1, col=1
                )
                
                # Bowling performance
                if wickets > 0:
                    bowling_metrics = ['Wickets', 'Economy', 'Strike Rate']
                    bowling_values = [wickets, economy, wicket_strike_rate]
                    
                    fig.add_trace(
                        go.Bar(x=bowling_metrics, y=bowling_values,
                              marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1'],
                              name='Bowling'),
                        row=1, col=2
                    )
                
                # Strike Rate vs Economy scatter
                fig.add_trace(
                    go.Scatter(x=[economy], y=[strike_rate], 
                              mode='markers', marker_size=20,
                              marker_color='#2E8B57', name=f'{player_name or "Player"}'),
                    row=2, col=1
                )
                
                # Impact breakdown pie chart
                impact_breakdown = ['Runs', 'Wickets Bonus']
                impact_values = [runs_scored, 20 * wickets]
                
                fig.add_trace(
                    go.Pie(labels=impact_breakdown, values=impact_values,
                          marker_colors=['#32CD32', '#2E8B57']),
                    row=2, col=2
                )
                
                fig.update_layout(height=800, showlegend=False, title_text="Player Performance Analysis")
                st.plotly_chart(fig, use_container_width=True)
                
                
            except Exception as e:
                st.error(f"❌ Prediction failed: {e}")

# ============================================================================
# BEST XI TEAM BUILDER 
# ============================================================================
elif st.session_state.current_page == "🏆 Best XI Team Builder":
    st.markdown("""
    <div class="feature-card fade-in">
        <h2 style="color: #2E8B57; margin-bottom: 1rem; display: flex; align-items: center; gap: 10px;">
            🏆 Best XI Team Builder <span style="font-size: 1rem; background: linear-gradient(135deg, #FF6B6B, #4ECDC4); color: white; padding: 0.3rem 0.8rem; border-radius: 20px;">Optimization Engine</span>
        </h2>
        <p style="color: #666; font-size: 1.1rem; margin-bottom: 0;">Build your optimal cricket team using advanced mathematical optimization algorithms! 🚀</p>
    </div>
    """, unsafe_allow_html=True)

    # Team constraints in main area instead of sidebar
    st.markdown("### ⚙️ Team Configuration")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        team_size = st.number_input("👥 Team Size", 0, 30, 11)
        budget = st.number_input("💰 Max Budget (Cr)", 0.0, 500.0, 100.0, step=0.1)
    
    with col2:
        max_overseas = st.slider("🌍 Max Overseas", 0, 10, 4)
        min_batsmen = st.slider("🏏 Min Batsmen", 0, 20, 3)
    
    with col3:
        min_bowlers = st.slider("🎳 Min Bowlers", 0, 20, 3)
        min_allrounders = st.slider("⚡ Min All-Rounders", 0, 20, 2)
        min_wk = st.slider("🧤 Min Wicketkeepers", 0, 20, 1)

    

    # Session state initialization 
    if "players" not in st.session_state:
        st.session_state.players = pd.DataFrame(columns=[
            "player_name", "role", "price", "runs_scored",
            "strike_rate", "wickets", "economy", "is_overseas"
        ])

    # Impact Score function
    def compute_impact(df):
        df["impact"] = df["runs_scored"] + 20 * df["wickets"]
        return df

    
    # Input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📋 Player Database Management")
        
        # File upload 
        uploaded = st.file_uploader(
            "📁 Upload Player Data (CSV)",
            type=["csv"],
            help="Upload a CSV file with player statistics"
        )

        if uploaded:
            df = pd.read_csv(uploaded)
            st.session_state.players = df
            st.success(f"✅ Successfully loaded {len(df)} players from CSV file!")
            
            # Show data preview
            with st.expander("👀 Preview Uploaded Data", expanded=True):
                st.dataframe(df.head(), use_container_width=True)
        
        # Manual player addition
        with st.expander("➕ Add Individual Player", expanded=len(st.session_state.players) == 0):
            with st.form("add_player_form"):
                st.markdown("**Player Information**")
                pcol1, pcol2 = st.columns(2)
                
                with pcol1:
                    name = st.text_input("🏏 Player Name", placeholder="e.g., MS Dhoni")
                    role = st.selectbox("👤 Role", ["Batsman", "Bowler", "All-Rounder", "Wicketkeeper"])
                    price = st.number_input("💰 Price (Cr)", 0.0, 25.0, 5.0, step=0.5)
                    overseas = st.checkbox("🌍 Overseas Player")
                
                with pcol2:
                    runs = st.number_input("🏃‍♂️ Runs Scored", 0, 3000, 300)
                    sr = st.number_input("⚡ Strike Rate", 0.0, 300.0, 130.0)
                    wkts = st.number_input("🎯 Wickets", 0, 50, 5)
                    eco = st.number_input("📊 Economy", 0.0, 15.0, 7.5)

                if st.form_submit_button("✅ Add Player to Database", use_container_width=True):
                    if name.strip():
                        new_row = pd.DataFrame([{
                            "player_name": name,
                            "role": role,
                            "price": price,
                            "runs_scored": runs,
                            "strike_rate": sr,
                            "wickets": wkts,
                            "economy": eco,
                            "is_overseas": 1 if overseas else 0
                        }])
                        st.session_state.players = pd.concat([st.session_state.players, new_row], ignore_index=True)
                        st.success(f"🎉 Added {name} to your player database!")
                        st.rerun()
                    else:
                        st.error("❌ Please enter a player name!")

    with col2:
        st.markdown("### ⚡ Quick Actions")
        
        # Enhanced sample players
        if st.button("🌟 Add Star Players", use_container_width=True, help="Add popular IPL players"):
            star_players = pd.DataFrame([
                {"player_name": "Virat Kohli", "role": "Batsman", "price": 15.0, "runs_scored": 741, "strike_rate": 154.69, "wickets": 0, "economy": 0, "is_overseas": 0},
                {"player_name": "AB de Villiers", "role": "Batsman", "price": 11.0, "runs_scored": 454, "strike_rate": 151.68, "wickets": 0, "economy": 0, "is_overseas": 1},
                {"player_name": "MS Dhoni", "role": "Wicketkeeper", "price": 12.0, "runs_scored": 200, "strike_rate": 116.28, "wickets": 0, "economy": 0, "is_overseas": 0},
                {"player_name": "Jasprit Bumrah", "role": "Bowler", "price": 13.0, "runs_scored": 10, "strike_rate": 100, "wickets": 27, "economy": 6.73, "is_overseas": 0},
                {"player_name": "Kagiso Rabada", "role": "Bowler", "price": 9.25, "runs_scored": 15, "strike_rate": 120, "wickets": 30, "economy": 8.34, "is_overseas": 1},
                {"player_name": "Andre Russell", "role": "All-Rounder", "price": 12.0, "runs_scored": 348, "strike_rate": 204.81, "wickets": 6, "economy": 9.52, "is_overseas": 1},
                {"player_name": "Ravindra Jadeja", "role": "All-Rounder", "price": 16.0, "runs_scored": 131, "strike_rate": 127.18, "wickets": 13, "economy": 7.01, "is_overseas": 0},
                {"player_name": "KL Rahul", "role": "Wicketkeeper", "price": 17.0, "runs_scored": 626, "strike_rate": 135.38, "wickets": 0, "economy": 0, "is_overseas": 0},
            ])
            st.session_state.players = pd.concat([st.session_state.players, star_players], ignore_index=True)
            st.success("🌟 Added 8 star players to your database!")
            st.rerun()
        
        if st.button("🔄 Clear Database", use_container_width=True, help="Remove all players"):
            st.session_state.players = pd.DataFrame(columns=[
                "player_name", "role", "price", "runs_scored",
                "strike_rate", "wickets", "economy", "is_overseas"
            ])
            st.success("🗑️ Player database cleared!")
            st.rerun()
        
        # Database stats
        if not st.session_state.players.empty:
            st.markdown("### 📊 Database Stats")
            total_players = len(st.session_state.players)
            total_value = st.session_state.players['price'].sum()
            overseas_count = st.session_state.players['is_overseas'].sum()
            
            st.metric("Total Players", total_players)
            st.metric("Total Value", f"₹{total_value:.1f}Cr")
            st.metric("Overseas Players", overseas_count)

    # Enhanced current player pool display
    if not st.session_state.players.empty:
        st.markdown("### 👥 Current Player Pool")
        
        # Add filters
        col1, col2, col3 = st.columns(3)
        with col1:
            role_filter = st.multiselect("Filter by Role", 
                options=st.session_state.players['role'].unique(),
                default=st.session_state.players['role'].unique())
        with col2:
            max_price_filter = st.slider("Max Price (Cr)", 
                0.0, float(st.session_state.players['price'].max()), 
                float(st.session_state.players['price'].max()))
        with col3:
            overseas_filter = st.selectbox("Overseas Filter", 
                ["All Players", "Local Only", "Overseas Only"])
        
        # Apply filters
        filtered_df = st.session_state.players.copy()
        filtered_df = filtered_df[filtered_df['role'].isin(role_filter)]
        filtered_df = filtered_df[filtered_df['price'] <= max_price_filter]
        
        if overseas_filter == "Local Only":
            filtered_df = filtered_df[filtered_df['is_overseas'] == 0]
        elif overseas_filter == "Overseas Only":
            filtered_df = filtered_df[filtered_df['is_overseas'] == 1]
        
        # Calculate and display impact scores
        display_df = filtered_df.copy()
        display_df["impact"] = display_df["runs_scored"] + 20 * display_df["wickets"]
        display_df = display_df.sort_values('impact', ascending=False)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "player_name": "Player Name",
                "role": st.column_config.SelectboxColumn("Role", options=["Batsman", "Bowler", "All-Rounder", "Wicketkeeper"]),
                "price": st.column_config.NumberColumn("Price (Cr)", format="%.1f"),
                "runs_scored": st.column_config.NumberColumn("Runs"),
                "strike_rate": st.column_config.NumberColumn("Strike Rate", format="%.2f"),
                "wickets": st.column_config.NumberColumn("Wickets"),
                "economy": st.column_config.NumberColumn("Economy", format="%.2f"),
                "is_overseas": st.column_config.CheckboxColumn("Overseas"),
                "impact": st.column_config.NumberColumn("Impact Score", format="%.0f")
            }
        )

    # Team selection logic with strategy
    def select_best_team(players_df):
        players_df = compute_impact(players_df.copy())

        prob = LpProblem("BestXI", LpMaximize)
        choices = LpVariable.dicts("select", players_df.index, cat="Binary")

        # Objective: maximize impact
        prob += lpSum(players_df.loc[i, "impact"] * choices[i] for i in players_df.index)

        # Constraints
        prob += lpSum(choices[i] for i in players_df.index) == team_size, "TeamSize"
        prob += lpSum(players_df.loc[i, "price"] * choices[i] for i in players_df.index) <= budget, "Budget"
        prob += lpSum(players_df.loc[i, "is_overseas"] * choices[i] for i in players_df.index) <= max_overseas, "OverseasLimit"
        prob += lpSum(choices[i] for i in players_df.index if players_df.loc[i, "role"] == "Batsman") >= min_batsmen, "MinBatsmen"
        prob += lpSum(choices[i] for i in players_df.index if players_df.loc[i, "role"] == "Bowler") >= min_bowlers, "MinBowlers"
        prob += lpSum(choices[i] for i in players_df.index if players_df.loc[i, "role"] == "All-Rounder") >= min_allrounders, "MinAllRounders"
        prob += lpSum(choices[i] for i in players_df.index if players_df.loc[i, "role"] == "Wicketkeeper") >= min_wk, "MinWicketkeepers"

        prob.solve()

        violated = []

        # Check constraint satisfaction
        if prob.status != 1:  # not optimal
            for cname, c in prob.constraints.items():
                if c.value() is not None and c.value() < -1e-6:  # constraint violated
                    violated.append(cname)

        if violated:
            st.error(f"❌ Cannot build a valid team. Violated constraints: {', '.join(violated)}")
            return pd.DataFrame()

        selected = players_df[[choices[i].value() == 1 for i in players_df.index]]
        return selected

    # Team building button
    st.markdown("### 🚀 Team Generation")

    # Single column layout
    col1 = st.container()

    with col1:
        if st.button("🏆 Build Optimal Team", use_container_width=True, type="primary"):
            if st.session_state.players.empty:
                st.error("⚠️ Please add players to your database first!")
            else:
                with st.spinner("🔮 AI is optimizing your dream team..."):
                    best_team = select_best_team(st.session_state.players)

                if best_team.empty:
                    st.error("❌ No valid team found with current constraints. Please adjust your requirements.")
                else:
                    st.balloons()  # Celebration effect
                    st.success("🎉 Your optimal team has been assembled!")

                    # Team metrics
                    total_cost = best_team["price"].sum()
                    total_impact = best_team["impact"].sum()
                    overseas_count = best_team["is_overseas"].sum()
                    avg_sr = best_team[best_team["strike_rate"] > 0]["strike_rate"].mean()
                    
                    # Team summary cards
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stat-value">₹{total_cost:.1f}Cr</div>
                            <div class="stat-label">Total Cost</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stat-value">{total_impact:.0f}</div>
                            <div class="stat-label">Team Impact</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stat-value">{overseas_count}/{max_overseas}</div>
                            <div class="stat-label">Overseas Quota</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stat-value">{avg_sr:.1f}</div>
                            <div class="stat-label">Avg Strike Rate</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col5:
                        efficiency = (total_impact / total_cost) if total_cost > 0 else 0
                        st.markdown(f"""
                        <div class="stats-card">
                            <div class="stat-value">{efficiency:.1f}</div>
                            <div class="stat-label">Cost Efficiency</div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Team composition table 
                    st.markdown("### 🏏 Your Dream Team XI")
                    team_display = best_team.copy()
                    team_display['Captain Potential'] = team_display.apply(
                        lambda x: '⭐ Captain' if x['impact'] == team_display['impact'].max() else '👤 Player', axis=1
                    )
                    
                    st.dataframe(
                        team_display[['player_name', 'role', 'price', 'runs_scored', 'strike_rate', 'wickets', 'economy', 'impact', 'Captain Potential']],
                        use_container_width=True,
                        column_config={
                            "player_name": "🏏 Player",
                            "role": "👤 Role",
                            "price": st.column_config.NumberColumn("💰 Price (Cr)", format="%.1f"),
                            "runs_scored": st.column_config.NumberColumn("🏃‍♂️ Runs"),
                            "strike_rate": st.column_config.NumberColumn("⚡ SR", format="%.1f"),
                            "wickets": st.column_config.NumberColumn("🎯 Wickets"),
                            "economy": st.column_config.NumberColumn("📊 Eco", format="%.1f"),
                            "impact": st.column_config.NumberColumn("🔥 Impact", format="%.0f"),
                            "Captain Potential": "🎖️ Role"
                        }
                    )


                    # Analytics with Plotly
                    st.markdown("### 📊 Team Analytics Dashboard")
                    
                    # Create comprehensive subplot
                    fig = make_subplots(
                        rows=2, cols=2,
                        subplot_titles=(
                            'Role Distribution', 
                            'Impact vs Price Analysis', 
                            'Player Performance Radar',
                            'Budget Utilization'
                        ),
                        specs=[
                            [{"type": "pie"}, {"type": "scatter"}],
                            [{"type": "scatterpolar"}, {"type": "bar"}]
                        ]
                    )
                    
                    # Role distribution pie chart
                    role_counts = best_team["role"].value_counts()
                    fig.add_trace(
                        go.Pie(
                            labels=role_counts.index, 
                            values=role_counts.values,
                            marker_colors=['#2E8B57', '#32CD32', '#90EE90', '#98FB98']
                        ),
                        row=1, col=1
                    )
                    
                    # Impact vs Price scatter
                    fig.add_trace(
                        go.Scatter(
                            x=best_team["price"], 
                            y=best_team["impact"],
                            mode='markers+text',
                            text=best_team["player_name"],
                            textposition="top center",
                            marker=dict(
                                size=15,
                                color=best_team["is_overseas"],
                                colorscale=['#2E8B57', '#FF6B6B'],
                                showscale=True,
                                colorbar=dict(title="Overseas")
                            ),
                            name="Players"
                        ),
                        row=1, col=2
                    )
                    
                    best_team["impact"] = pd.to_numeric(best_team["impact"], errors="coerce")

                    # Performance radar for top 3 players
                    top_players = best_team.nlargest(3, 'impact')

                    # Performance radar for top 3 players
                    top_players = best_team.nlargest(3, 'impact')
                    categories = ['Runs', 'Strike Rate', 'Wickets', 'Economy']
                    
                    for _, player in top_players.iterrows():
                        values = [
                            player['runs_scored']/10,  # Normalize
                            player['strike_rate']/2,
                            player['wickets']*5,
                            max(0, 50 - player['economy']*5)
                        ]
                        
                        fig.add_trace(
                            go.Scatterpolar(
                                r=values,
                                theta=categories,
                                fill='toself',
                                name=player['player_name']
                            ),
                            row=2, col=1
                        )
                    
                    # Budget utilization
                    budget_used = total_cost
                    budget_remaining = budget - total_cost
                    
                    fig.add_trace(
                        go.Bar(
                            x=['Used', 'Remaining'],
                            y=[budget_used, budget_remaining],
                            marker_color=['#2E8B57', '#90EE90'],
                            name="Budget"
                        ),
                        row=2, col=2
                    )
                    
                    fig.update_layout(height=800, showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    
                    
                    # Download CSV
                    enhanced_csv = best_team.copy()
                    enhanced_csv['selection_date'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    csv_data = enhanced_csv.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "⬇️ Download Team Sheet", 
                        data=csv_data, 
                        file_name=f"best_xi_team.csv", 
                        mime="text/csv", 
                        use_container_width=True
                    )


# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <h3>🏏 Cricket Analytics Pro</h3>
    <p><strong>The Ultimate AI-Powered Cricket Intelligence Platform</strong></p>
    <p>🤖 Advanced AI Analysis • 💰 Smart Price Predictions • 🏆 Optimal Team Building</p>
    <p><em>Empowering cricket decisions with cutting-edge technology</em></p>
    <div style="margin-top: 2rem; font-size: 0.9rem; opacity: 0.8;">
        <p>Built with ❤️ from Vedant • Powered by Gemini AI • Optimized with PuLP</p>
    </div>
</div>
""", unsafe_allow_html=True)