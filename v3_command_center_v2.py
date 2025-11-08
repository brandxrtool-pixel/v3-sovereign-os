# V3 Sovereign OS - Command Center
# Streamlit application for personal development, structured by Pillars and Shadows.
# MODIFIED FOR LOCAL EXECUTION (Reads API Key from st.secrets)
# --- NOW INCLUDES CHROMA DB CONNECTION & RAG CHAT INTERFACE ---

import streamlit as st
import json
import os
import time
import base64
from datetime import datetime
import asyncio
import requests # Added requests for API calls
import re # Added for text chunking
from typing import List, Dict, Any, Optional

# --- ChromaDB Import ---
# Make sure to add 'chromadb' to your requirements.txt file!
import chromadb

# --- Configuration ---
# Set the model name for text generation tasks
GEMINI_MODEL = "gemini-2.5-flash-preview-09-2025"

# --- Global Variables for Firestore/API Keys ---
# Using standard global variables provided by the Canvas environment.
# Note: Canvas provides __app_id, __firebase_config, and __initial_auth_token
# We check for these in the environment or use placeholders.

# Check for existence of Canvas global variables if running outside Streamlit environment
try:
    # Use environment variables for Canvas globals
    APP_ID = os.environ.get('__app_id') or 'default-sovereign-os-id'
    config_str = os.environ.get('__firebase_config', '{}')
    initialAuthToken = os.environ.get('__initial_auth_token')
except Exception:
    # Fallback placeholders
    APP_ID = 'default-sovereign-os-id'
    config_str = '{}'
    initialAuthToken = None

try:
    firebaseConfig = json.loads(config_str)
except json.JSONDecodeError:
    firebaseConfig = {}


def get_base_path(relative_path):
    """Return absolute path for a file (works in local + Streamlit Cloud)"""
    try:
        # When running on Streamlit Cloud or local Streamlit run
        base_path = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
    except NameError:
        # When running interactively or in notebooks
        base_path = os.getcwd()
    return os.path.join(base_path, relative_path)

# Ensure a minimal style.css exists for the load_css function not to fail
# We create a dummy file on the fly if needed, or rely on the fallback CSS.
try:
    with open(get_base_path('style.css'), 'w') as f:
        f.write(".st-emotion-cache-12fmj8x { padding-top: 2rem; }")
except Exception:
    pass

# --- ChromaDB Client Setup ---

@st.cache_resource
def setup_chroma_client(_dummy_param=None):
    """
    Initializes and returns a ChromaDB client connected to the cloud.
    Uses st.secrets for credentials.
    """
    try:
        # Load all connection details from secrets
        api_key = st.secrets["CHROMA_API_KEY"]
        tenant = st.secrets["CHROMA_TENANT"]
        database = st.secrets["CHROMA_DATABASE"]
        
        st.info(f"Connecting to ChromaDB: {database}")
        
    except KeyError as e:
        st.error(f"Error: Chroma key '{e.args[0]}' not found in st.secrets.")
        st.error("Please add CHROMA_API_KEY, CHROMA_TENANT, and CHROMA_DATABASE to your .streamlit/secrets.toml file.")
        return None
        
    try:
        # Connect to ChromaDB Cloud using CloudClient
        client = chromadb.CloudClient(
            tenant=tenant,
            database=database,
            api_key=api_key 
        )
        
        # Test connection by listing collections
        collections = client.list_collections()
        st.success(f"✅ Successfully connected to Chroma database: {database}")
        st.info(f"Found {len(collections)} collections")
        return client
        
    except Exception as e:
        st.error(f"Error connecting to ChromaDB: {e}")
        st.info("The app will continue without ChromaDB functionality. You can still use other features.")
        return None

# --- Persistence Functions (Simulated File I/O) ---

def load_data(filename: str, default_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Loads data from a JSON file with error handling.
    This function has been reinforced to prevent the list index TypeError
    by checking the file's root structure before accessing keys.
    """
    filepath = get_base_path(filename)
    data = default_data.copy() # Start with a copy of defaults
    
    try:
        with open(filepath, 'r') as f:
            file_data = json.load(f)
            
            # CRITICAL FIX: Ensure file_data is a dictionary before trying to merge/access keys
            if isinstance(file_data, dict):
                data.update(file_data)
            else:
                # If it's a list or primitive, skip the update and use defaults/existing keys
                st.warning(f"File {filename} content is a list/primitive, not a dict. Using default structure.")
            
            # Ensure the required keys from default_data are present in the final data
            for key, default_value in default_data.items():
                if key not in data:
                    data[key] = default_value
            return data
            
    except FileNotFoundError:
        st.warning(f"Data file not found: {filename}. Initializing with default data.")
        # Save default data immediately to create the file structure
        try:
             with open(filepath, 'w') as f:
                json.dump(default_data, f, indent=4)
        except Exception:
            pass # Ignore write errors if the environment is read-only
        return default_data
        
    except json.JSONDecodeError:
        st.error(f"Error decoding JSON in {filename}. Initializing with default data to prevent crash.")
        return default_data


def save_all_data():
    """Saves all current session state data back to their respective files."""
    try:
        # Save Pillars and Shadows
        with open(get_base_path('pillars.json'), 'w') as f:
            json.dump({'pillars': st.session_state.pillars_data['pillars']}, f, indent=4)
        with open(get_base_path('shadows.json'), 'w') as f:
            json.dump({'shadows': st.session_state.shadows_data['shadows']}, f, indent=4)

        # Save Goals
        with open(get_base_path('goals_detailed.json'), 'w') as f:
            json.dump({'goals': st.session_state.goals_data['goals']}, f, indent=4)
            
        # Save Tasks
        with open(get_base_path('tasks.json'), 'w') as f:
            json.dump({'tasks': st.session_state.tasks_data['tasks']}, f, indent=4)

        # Save Chat Histories (Adhering to the {'history': list} structure for load_data compatibility)
        with open(get_base_path('v3_advisor_history.json'), 'w') as f:
            json.dump({'history': st.session_state.v3_advisor_history}, f, indent=4)  
        with open(get_base_path('super_ai_history.json'), 'w') as f:
            json.dump({'history': st.session_state.super_ai_history}, f, indent=4)
        with open(get_base_path('bol_academy_history.json'), 'w') as f:
            json.dump({'history': st.session_state.bol_academy_history}, f, indent=4)
        with open(get_base_path('business_coach_history.json'), 'w') as f:
            json.dump({'history': st.session_state.business_coach_history}, f, indent=4)
        with open(get_base_path('health_coach_history.json'), 'w') as f:
            json.dump({'history': st.session_state.health_coach_history}, f, indent=4)
        # 1. (TEMPLATE) Save history for the new coach
        with open(get_base_path('energy_somatic_history.json'), 'w') as f:
            json.dump({'history': st.session_state.energy_somatic_history}, f, indent=4)


        st.toast("✅ All data saved successfully!", icon="💾")
        st.session_state.unsaved_changes = False

    except Exception as e:
        st.error(f"An error occurred during save: {e}")

def create_backup():
    """Creates a zip archive of all current JSON data files."""
    st.info("Backup functionality would typically create a ZIP file of all JSONs here.")
    st.toast("Backup data created!", icon="📦")
    st.session_state.unsaved_changes = False

# --- Core Data Initialization ---

def initialize_session_state():
    """Initializes session state with data loaded from files."""
    if 'initialized' not in st.session_state:
        # 1. Structural Data
        st.session_state.pillars_data = load_data('pillars.json', {'pillars': [
            {'name': 'Health', 'score': 60, 'focus': 'Optimize physical and mental energy.'},
            {'name': 'Wealth', 'score': 45, 'focus': 'Build autonomous income streams.'},
            {'name': 'Relationship', 'score': 75, 'focus': 'Deepen connection with core network.'},
            {'name': 'Sovereignty', 'score': 55, 'focus': 'Increase personal agency and self-reliance.'}
        ]})
        st.session_state.shadows_data = load_data('shadows.json', {'shadows': [
            {'name': 'Procrastination', 'score': 80, 'focus': 'Immediate action bias.'},
            {'name': 'Self-Doubt', 'score': 30, 'focus': 'Confidence in execution.'},
        ]})
        st.session_state.goals_data = load_data('goals_detailed.json', {'goals': []})
        st.session_state.tasks_data = load_data('tasks.json', {'tasks': []})

        # 2. UI State
        st.session_state.page = 'Dashboard'
        st.session_state.unsaved_changes = False
        st.session_state.initialized = True
        st.session_state.user_input = ""

        # 3. Chat Histories
        v3_advisor_default = [{
            "role": "model",
            "text": "Welcome to the V3 Command Center. I am your V3 Advisor. How can I assist you in optimizing your day or refining your Pillars and Shadows today?",
            "is_user": False
        }]
        st.session_state.v3_advisor_history = load_data('v3_advisor_history.json', {'history': v3_advisor_default})['history']

        super_ai_default = [{
            "role": "model",
            "text": "Greetings. I am the Super AI. Submit any complex, unstructured data or queries, and I will analyze them through the lens of your Sovereign OS structure.",
            "is_user": False
        }]
        st.session_state.super_ai_history = load_data('super_ai_history.json', {'history': super_ai_default})['history']

        bol_academy_default = [{
            "role": "model",
            "text": "Welcome to the BOL Academy. I am your dedicated tutor for the 21 Brotherhood of Light Courses. When you are ready, please tell me to begin **Course 1: Laws of Occultism: Inner Plane Theory and the Fundamentals of Psychic Phenomena**.",
            "is_user": False
        }]
        st.session_state.bol_academy_history = load_data('bol_academy_history.json', {'history': bol_academy_default})['history']

        business_coach_default = [{
            "role": "model",
            "text": "Welcome to the V3 Business Coach. I am here to answer questions based on the knowledge you provide. Please go to the 'Ingest Data' page to upload your business notes before we begin.",
            "is_user": False
        }]
        st.session_state.business_coach_history = load_data('business_coach_history.json', {'history': business_coach_default})['history']
        
        health_coach_default = [{
            "role": "model",
            "text": "Welcome to the V3 Health Coach. I am ready to review your 'Hardware' protocols. Please go to the 'Ingest Data' page to upload your health and somatic notes.",
            "is_user": False
        }]
        st.session_state.health_coach_history = load_data('health_coach_history.json', {'history': health_coach_default})['history']

        # 2. (TEMPLATE) Initialize history for the new coach
        energy_somatic_default = [{
            "role": "model",
            "text": "Welcome to the Energy & Somatic Coach. I am here to help you regulate your nervous system and manage your 'Hardware' protocols. Please feed my knowledge base via the 'Ingest Data' page.",
            "is_user": False
        }]
        st.session_state.energy_somatic_history = load_data('energy_somatic_history.json', {'history': energy_somatic_default})['history']


        # 4. Auth/Database (Placeholder for Firestore)
        st.session_state.db = None
        st.session_state.auth = None
        st.session_state.user_id = APP_ID 

        # 5. ChromaDB Client
        st.session_state.chroma_client = setup_chroma_client()


# --- Styling and UI Functions ---

def load_css(filepath: str):
    """Injects custom CSS from a file."""
    try:
        with open(filepath) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback inline CSS for aesthetics
        st.markdown("""
            <style>
                .main { background-color: #0d1117; color: #c9d1d9; font-family: 'Inter', sans-serif; }
                .st-emotion-cache-12fmj8x { padding-top: 2rem; }
                .os-title { font-size: 1.8rem; font-weight: bold; color: #2f81f7; margin-bottom: 20px; }
                .subheader { color: #8b949e; margin-bottom: 10px; }
                .metric-card { background: #161b22; padding: 15px; border-radius: 8px; border-left: 5px solid #2f81f7; margin-bottom: 15px; }
                .metric-title { font-size: 0.9rem; color: #8b949e; }
                .metric-value { font-size: 2rem; font-weight: bold; }
                .score-glow-blue { color: #58a6ff; text-shadow: 0 0 5px rgba(47, 129, 247, 0.5); }
                .score-glow-green { color: #3fb950; text-shadow: 0 0 5px rgba(63, 185, 80, 0.5); }
                .score-glow-yellow { color: #e3b341; text-shadow: 0 0 5px rgba(227, 179, 65, 0.5); }
                .pillar-card { background: #161b22; padding: 10px; border-radius: 6px; margin-bottom: 10px; border: 1px solid #21262d; }
                .pillar-title { font-weight: bold; color: #c9d1d9; margin-bottom: 5px; }
                .pillar-focus { font-size: 0.8rem; color: #8b949e; margin-bottom: 10px; height: 40px; overflow: hidden; }
                .pillar-progress-bar { width: 100%; height: 5px; border-radius: 2px; }
                .pillar-score { float: right; font-size: 0.8rem; font-weight: bold; color: #58a6ff; }
                .goal-card { background: #161b22; padding: 12px; border-radius: 6px; margin-bottom: 10px; border-left: 3px solid #3fb950; }
                .goal-title { font-weight: bold; color: #c9d1d9; display: inline-block; margin-right: 10px; }
                .pillar-tag-small { background-color: #21262d; color: #58a6ff; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: normal; }
                .priority-tag { font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; font-weight: bold; margin-left: 5px; }
                .P1 { background-color: #6e1c25; color: #f85149; border: 1px solid #f85149; }
                .P2 { background-color: #66501a; color: #e3b341; border: 1px solid #e3b341; }
                .P3 { background-color: #1c2b39; color: #58a6ff; border: 1px solid #58a6ff; }
                .task-completed-label { color: #3fb950; text-decoration: line-through; margin-top: 5px; font-size: 0.9rem; }
                .user-id-display { font-size: 0.75rem; color: #8b949e; margin-top: 15px; }
                .user-id-display span { font-family: monospace; color: #58a6ff; }
                .chat-container { height: 70vh; overflow-y: auto; padding: 10px; border: 1px solid #21262d; border-radius: 8px; margin-bottom: 10px; }
                .user-message { background-color: #0c1a26; padding: 10px; border-radius: 15px 15px 5px 15px; margin-bottom: 10px; max-width: 80%; margin-left: auto; color: #c9d1d9; }
                .assistant-message { background-color: #161b22; padding: 10px; border-radius: 15px 15px 15px 5px; margin-bottom: 10px; max-width: 80%; color: #c9d1d9; }
            </style>
        """, unsafe_allow_html=True)


def set_page(page_name: str):
    """Changes the current page."""
    st.session_state.page = page_name

def render_sidebar():
    """Renders the persistent sidebar navigation and controls."""
    st.sidebar.markdown(f"<div class='os-title'>V3 Sovereign OS</div>", unsafe_allow_html=True)

    # Navigation Buttons
    st.sidebar.button('📈 Dashboard', on_click=set_page, args=('Dashboard',), use_container_width=True)
    st.sidebar.button('🛡️ Pillars & Shadows', on_click=set_page, args=('Pillars & Shadows',), use_container_width=True)
    st.sidebar.button('🎯 Goals', on_click=set_page, args=('Goals',), use_container_width=True)
    st.sidebar.button('📋 Tasks', on_click=set_page, args=('Tasks',), use_container_width=True)
    
    st.sidebar.markdown('---')
    st.sidebar.markdown("<div class='subheader' style='margin:0; padding-left: 5px;'>AI ADVISORS</div>", unsafe_allow_html=True)
    st.sidebar.button('💬 V3 Advisor (General)', on_click=set_page, args=('V3 Advisor',), use_container_width=True)
    st.sidebar.button('🧬 Super AI (Analysis)', on_click=set_page, args=('Super AI',), use_container_width=True)
    st.sidebar.button('🔮 BOL Academy (Tutor)', on_click=set_page, args=('BOL Academy',), use_container_width=True)

    st.sidebar.markdown('---')
    st.sidebar.markdown("<div class='subheader' style='margin:0; padding-left: 5px;'>PILLAR COACHES</div>", unsafe_allow_html=True)
    st.sidebar.button('💼 Business Coach (Hybrid)', on_click=set_page, args=('Business Coach',), use_container_width=True)
    st.sidebar.button('💪 Health Coach (Hybrid)', on_click=set_page, args=('Health Coach',), use_container_width=True)
    # 3. (TEMPLATE) Add a button for the new coach
    st.sidebar.button('⚡ Energy & Somatic Coach (Hybrid)', on_click=set_page, args=('Energy & Somatic Coach',), use_container_width=True)


    st.sidebar.markdown('---')
    st.sidebar.button('💾 Ingest Data', on_click=set_page, args=('Ingest Data',), use_container_width=True)
    st.sidebar.button('⚙️ Settings', on_click=set_page, args=('Settings',), use_container_width=True)

    # Save Control
    st.sidebar.markdown("<div class='save-section'>", unsafe_allow_html=True)
    save_label = "💾 Save All Changes"
    if st.session_state.unsaved_changes:
        save_label = "🚨 Unsaved Changes! Click to Save."
    
    st.sidebar.button(save_label, on_click=save_all_data, use_container_width=True, key="save_button")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    
    st.sidebar.markdown(f"<div class='user-id-display'>User ID: <span>{st.session_state.user_id}</span></div>", unsafe_allow_html=True)


# --- Page Functions ---

def render_dashboard():
    """Dashboard page showing high-level metrics."""
    st.markdown("## Command Center Dashboard")
    st.markdown("<div class='subheader'>Real-Time System Overview</div>", unsafe_allow_html=True)

    pillars = st.session_state.pillars_data['pillars']
    shadows = st.session_state.shadows_data['shadows']
    goals = st.session_state.goals_data['goals']

    # --- 1. Top Metrics (Overall Health) ---
    goal_progress = 0
    if goals:
        valid_progresses = [g.get('progress', 0) for g in goals if isinstance(g.get('progress'), (int, float))]
        if valid_progresses:
            goal_progress = sum(valid_progresses) / len(valid_progresses)

    sovereign_score = sum([p['score'] for p in pillars]) / len(pillars) if pillars else 0

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>Sovereign Score</div>
            <div class='metric-value score-glow-blue'>{sovereign_score:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>Goal Completion</div>
            <div class='metric-value score-glow-green'>{goal_progress:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        shadow_progress = sum([s['score'] for s in shadows]) / len(shadows) if shadows else 0
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>Shadow Tamed</div>
            <div class='metric-value score-glow-yellow'>{shadow_progress:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- 2. Pillar Status ---
    st.markdown("### 🛡️ Pillar Status")
    
    if pillars:
        pillar_cols = st.columns(len(pillars))
        for i, p in enumerate(pillars):
            with pillar_cols[i]:
                st.markdown(f"""
                <div class='pillar-card'>
                    <div class='pillar-title'>{p['name']}</div>
                    <div class='pillar-focus'>{p['focus']}</div>
                    <div class='pillar-progress'>
                        <progress class='pillar-progress-bar' value='{p['score']}' max='100'></progress>
                        <span class='pillar-score'>{p['score']}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No Pillars defined. Go to 'Pillars & Shadows' to set them up.")


    st.markdown("---")

    # --- 3. Active Goals ---
    st.markdown("### 🎯 Active Goals")
    
    if not goals:
        st.info("No active goals found. Go to the 'Goals' page to set your targets.")
    else:
        active_goals = [g for g in goals if g.get('progress', 0) < 100]
        if not active_goals:
            st.info("All goals completed! Time to set new targets.")
        else:
            goal_cols_count = min(len(active_goals), 3)
            if goal_cols_count > 0:
                goal_cols = st.columns(goal_cols_count)
                for i, g in enumerate(active_goals[:goal_cols_count]):
                    with goal_cols[i % goal_cols_count]:
                        st.markdown(f"""
                        <div class='goal-card'>
                            <div class='goal-title'>{g['name']}</div>
                            <div class='goal-pillar'><span class='pillar-tag-small'>{g['pillar']}</span></div>
                            <div class='goal-progress-display'>{g['progress']}% Complete</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("All active goals are displayed.")


def render_pillars_shadows():
    """Pillars and Shadows management page."""
    st.markdown("## Pillars & Shadows Calibration")
    
    st.markdown("### 🛡️ Pillars: Areas of Focus (Max 100 Score)")
    st.markdown("<div class='subheader'>Use the sliders to calibrate your self-assessed current performance.</div>", unsafe_allow_html=True)

    if st.session_state.pillars_data['pillars']:
        cols = st.columns(len(st.session_state.pillars_data['pillars']))
        for i, p in enumerate(st.session_state.pillars_data['pillars']):
            with cols[i]:
                st.subheader(p['name'])
                new_score = st.slider('Current Score', 0, 100, p['score'], key=f"pillar_score_{p['name']}")
                if new_score != p['score']:
                    st.session_state.pillars_data['pillars'][i]['score'] = new_score
                    st.session_state.unsaved_changes = True

                new_focus = st.text_area('Core Focus', p['focus'], key=f"pillar_focus_{p['name']}")
                if new_focus != p['focus']:
                    st.session_state.pillars_data['pillars'][i]['focus'] = new_focus
                    st.session_state.unsaved_changes = True
    else:
        st.warning("No Pillars found. Add default pillars?") # Placeholder for future "add pillar" logic

    st.markdown("---")
    
    st.markdown("### 🌑 Shadows: Limiting Behaviors (Score is Taming Progress)")
    st.markdown("<div class='subheader'>Assess your control over limiting traits. 100% means fully tamed.</div>", unsafe_allow_html=True)
    
    if st.session_state.shadows_data['shadows']:
        shadow_cols_count = len(st.session_state.shadows_data['shadows'])
        if shadow_cols_count > 0:
            shadow_cols = st.columns(shadow_cols_count)
            for i, s in enumerate(st.session_state.shadows_data['shadows']):
                with shadow_cols[i]:
                    st.subheader(s['name'])
                    new_score = st.slider('Taming Progress (%)', 0, 100, s['score'], key=f"shadow_score_{s['name']}")
                    if new_score != s['score']:
                        st.session_state.shadows_data['shadows'][i]['score'] = new_score
                        st.session_state.unsaved_changes = True

                    new_focus = st.text_area('Integration Focus', s['focus'], key=f"shadow_focus_{s['name']}")
                    if new_focus != s['focus']:
                        st.session_state.shadows_data['shadows'][i]['focus'] = new_focus
                        st.session_state.unsaved_changes = True
        else:
            st.warning("No Shadows found.") # Placeholder for future "add shadow" logic
    else:
         st.warning("No Shadows found.") # Placeholder for future "add shadow" logic

def render_goals():
    """Goals management page."""
    st.markdown("## Goals Management")
    st.markdown("<div class='subheader'>Set, track, and manage your high-level outcomes.</div>", unsafe_allow_html=True)

    pillars = [p['name'] for p in st.session_state.pillars_data['pillars']]
    if not pillars:
        st.error("No Pillars defined. You must define Pillars before you can add Goals.")
        return

    def add_new_goal(name, pillar, deadline):
        """Adds a new goal to the session state."""
        if name and pillar:
            st.session_state.goals_data['goals'].append({
                'id': str(time.time()),
                'name': name,
                'pillar': pillar,
                'progress': 0,
                'deadline': deadline.strftime('%Y-%m-%d') if deadline else 'N/A'
            })
            st.session_state.unsaved_changes = True
            st.toast("Goal added!", icon="🎯")

    # --- Add New Goal Form ---
    with st.expander("➕ Add New Goal", expanded=False):
        with st.form("new_goal_form", clear_on_submit=True):
            goal_name = st.text_input("Goal Name (e.g., Launch SaaS product in 6 months)")
            goal_pillar = st.selectbox("Linked Pillar", pillars)
            default_date = datetime.now().date()
            goal_deadline = st.date_input("Target Deadline", min_value=default_date, value=default_date)
            submitted = st.form_submit_button("Create Goal")
            
            if submitted:
                add_new_goal(goal_name, goal_pillar, goal_deadline)

    st.markdown("---")

    # --- Goal List and Progress Tracking ---
    st.markdown("### Active Goal Tracking")
    
    goals = st.session_state.goals_data['goals']
    
    if not goals:
        st.info("No goals defined yet. Use the form above to get started.")
        return

    goals.sort(key=lambda g: (g.get('progress', 0) == 100, g.get('progress', 0)))

    for i, g in enumerate(goals):
        col1, col2, col3 = st.columns([0.6, 0.3, 0.1])
        
        with col1:
            st.markdown(f"#### {g['name']} <span class='pillar-tag-small'>{g['pillar']}</span>", unsafe_allow_html=True)
            st.progress(g.get('progress', 0) / 100)
        
        with col2:
            new_progress = st.slider('Progress (%)', 0, 100, g.get('progress', 0), key=f"goal_progress_{g['id']}")
            if new_progress != g.get('progress', 0):
                st.session_state.goals_data['goals'][i]['progress'] = new_progress
                st.session_state.unsaved_changes = True
                
            st.caption(f"Deadline: {g.get('deadline', 'N/A')}")
            
        with col3:
            if st.button("🗑️", key=f"delete_goal_{g['id']}"):
                st.session_state.goals_data['goals'].pop(i)
                st.session_state.unsaved_changes = True
                st.rerun()

    st.markdown("---")

def render_tasks():
    """Task management page (Actionable steps linked to Pillars)."""
    st.markdown("## Task Manager")
    st.markdown("<div class='subheader'>Actionable steps linked to your Pillars.</div>", unsafe_allow_html=True)

    pillars = [p['name'] for p in st.session_state.pillars_data['pillars']]
    if not pillars:
        st.error("No Pillars defined. You must define Pillars before you can add Tasks.")
        return
    
    # --- Helper to Update Pillar Score on Completion ---
    def update_pillar_score(pillar_name: str, priority: str):
        """Calculates and applies a score boost to the relevant Pillar."""
        boost_map = {'P1': 3, 'P2': 2, 'P3': 1}
        boost = boost_map.get(priority, 0)

        for p_idx, p in enumerate(st.session_state.pillars_data['pillars']):
            if p['name'] == pillar_name:
                new_score = min(100, p['score'] + boost)
                st.session_state.pillars_data['pillars'][p_idx]['score'] = new_score
                st.session_state.unsaved_changes = True
                st.toast(f"🎉 Task Completed! +{boost} points added to {pillar_name} Pillar.", icon="🚀")
                return

    # --- Add New Task Form ---
    with st.expander("➕ Add New Task", expanded=False):
        with st.form("new_task_form", clear_on_submit=True):
            task_name = st.text_input("Task Description")
            task_pillar = st.selectbox("Linked Pillar", pillars)
            task_priority = st.radio("Priority", ['P1 (Urgent)', 'P2 (Important)', 'P3 (Minor)'], horizontal=True)
            task_due_date = st.date_input("Due Date", min_value=datetime.now().date(), value=datetime.now().date())
            submitted = st.form_submit_button("Create Task")
            
            if submitted and task_name and task_pillar:
                st.session_state.tasks_data['tasks'].append({
                    'id': str(time.time()),
                    'name': task_name,
                    'pillar': task_pillar,
                    'priority': task_priority.split(' ')[0], # e.g., 'P1'
                    'due': task_due_date.strftime('%Y-%m-%d'),
                    'completed': False
                })
                st.session_state.unsaved_changes = True
                st.rerun() 

    st.markdown("---")

    # --- Task List Display ---
    st.markdown("### Task List")
    tasks = st.session_state.tasks_data['tasks']
    
    if not tasks:
        st.info("No active tasks. Add a task to initiate your daily flow.")
        return
    
    active_tasks = [t for t in tasks if not t.get('completed')]
    completed_tasks = [t for t in tasks if t.get('completed')]
    
    active_tasks.sort(key=lambda t: t['priority'])

    st.markdown("#### Active Tasks")
    
    if not active_tasks:
        st.info("All tasks complete! Excellent work.")
    
    for i, task in enumerate(active_tasks):
        key_prefix = f"active_task_{task['id']}"
        
        col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
        
        with col1:
            initial_value = task.get('completed', False)
            is_completed_check = col1.checkbox("", key=f"checkbox_{key_prefix}", value=initial_value)
            
        with col2:
            task_style = 'task-completed-label' if task.get('completed') else 'task-pending'
            task_name_display = task['name']
            if task.get('completed'):
                 task_name_display = f"✅ {task_name_display}"

            st.markdown(f"""
            <div class='{task_style}'>
                **{task_name_display}**
                <span class='pillar-tag-small'>{task['pillar']}</span> 
                <span class='priority-tag {task['priority']}'>{task['priority']}</span>
            </div>
            """, unsafe_allow_html=True)
            st.caption(f"Due: {task['due']}")

        with col3:
            if st.button("🗑️", key=f"delete_{key_prefix}"):
                task_index = next((j for j, t in enumerate(st.session_state.tasks_data['tasks']) if t['id'] == task['id']), None)
                if task_index is not None:
                    st.session_state.tasks_data['tasks'].pop(task_index)
                    st.session_state.unsaved_changes = True
                    st.rerun()

        if is_completed_check and not initial_value:
            for t_idx, t in enumerate(st.session_state.tasks_data['tasks']):
                if t['id'] == task['id']:
                    st.session_state.tasks_data['tasks'][t_idx]['completed'] = True
                    update_pillar_score(t['pillar'], t['priority'])
                    st.rerun() 

    st.markdown("---")
    st.markdown("#### Completed Tasks")
    
    if not completed_tasks:
        st.caption("No tasks completed yet.")
    else:
        for task in completed_tasks:
            st.markdown(f"<div class='task-completed-label'>✅ {task['name']} <span class='pillar-tag-small'>{task['pillar']}</span></div>", unsafe_allow_html=True)

# --- NEW DATA INGESTION PAGE ---

def render_ingest_data():
    """Renders the data ingestion page for ChromaDB."""
    st.markdown("## 💾 Ingest Data into Vector Store")
    st.markdown("<div class='subheader'>Add knowledge to your Pillar Coaches.</div>", unsafe_allow_html=True)
    
    if not st.session_state.chroma_client:
        st.error("ChromaDB connection failed. Please check your secrets and restart.")
        return

    client = st.session_state.chroma_client

    # --- Collection Management ---
    st.markdown("### Manage Collections")
    
    try:
        collections = client.list_collections()
        if collections:
            st.markdown("Existing Collections:")
            # Handle potential for many collections gracefully
            num_cols = min(len(collections), 4) # Max 4 columns
            cols = st.columns(num_cols)
            for i, col in enumerate(collections):
                with cols[i % num_cols]:
                    st.info(f"**{col.name}**\n\n`{col.count()} items`")
        else:
            st.info("No collections found in this database yet.")
            
    except Exception as e:
        st.error(f"Error listing collections: {e}")

    st.markdown("---")
    
    # --- Ingestion Form ---
    st.markdown("### Add New Knowledge")
    with st.form("ingest_form"):
        collection_name = st.text_input("Collection Name (e.g., 'business_coach_notes' or 'health_coach_notes')", "business_coach_notes")
        
        notes_text = st.text_area("Paste Your Notes Here", height=300, 
                                  placeholder="Paste your notes here. Separate thoughts or paragraphs with a double newline (Enter key twice) for best results.")
        
        submitted = st.form_submit_button("Ingest Notes")
        
        if submitted:
            if not collection_name:
                st.error("Collection Name is required.")
                return
            if not notes_text:
                st.error("Notes text is required.")
                return

            with st.spinner(f"Ingesting data into '{collection_name}'..."):
                try:
                    # 1. Get or create collection
                    collection = client.get_or_create_collection(name=collection_name)
                    
                    # 2. Chunk text (split by double newline)
                    chunks = re.split(r'\n\s*\n', notes_text.strip())
                    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
                    
                    if not chunks:
                        st.error("No valid text chunks found. Ensure you are using double newlines to separate paragraphs.")
                        return

                    # 3. Prepare data for upload
                    documents = []
                    metadatas = []
                    ids = []
                    
                    # Get current count to offset IDs
                    base_id = collection.count()
                    
                    for i, chunk in enumerate(chunks):
                        documents.append(chunk)
                        metadatas.append({"source": "streamlit_ingest", "chunk_num": i})
                        # Create a unique ID
                        ids.append(f"doc_{base_id + i}_{time.time_ns()}")

                    # 4. Add to collection
                    collection.add(
                        documents=documents,
                        metadatas=metadatas,
                        ids=ids
                    )
                    
                    st.success(f"--- SUCCESS! ---")
                    st.success(f"Added {len(documents)} new documents to the '{collection_name}' collection.")
                    st.success(f"Total items in collection: {collection.count()}.")
                    st.info("You can now chat with the corresponding coach!")

                except Exception as e:
                    st.error(f"Error during ingestion: {e}")
                    st.error("This may be due to exceeding the free-tier quota for your vector database.")


# --- AI Coach Functions ---

async def call_gemini_api(history: List[Dict[str, Any]], system_prompt: str, use_search: bool = False) -> Dict[str, Any]:
    """
    Handles the async API call to Gemini with backoff.
    CRITICAL FIX: This function is now guaranteed to return a dictionary 
    with 'text' and 'sources' keys on both success and failure, preventing KeyError.
    
    --- MODIFIED FOR LOCAL EXECUTION ---
    This function now reads the GEMINI_API_KEY from st.secrets.
    """
    
    # --- MODIFICATION FOR LOCAL RUN ---
    try:
        apiKey = st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        return {"text": "Error: `GEMINI_API_KEY` not found. Please create a file named `.streamlit/secrets.toml` in your app's root directory and add `GEMINI_API_KEY = \"YOUR_API_KEY_HERE\"`.", "sources": []}
    except Exception as e:
         return {"text": f"Error loading Streamlit secrets: {e}", "sources": []}
    
    # --- END MODIFICATION ---

    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={apiKey}"

    contents = []
    for message in history:
        role = "user" if message.get('is_user') else "model"
        message_text = message.get('text', 'Placeholder for missing text.')
        
        contents.append({
            "role": role,
            "parts": [{"text": message_text}]
        })

    payload = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": system_prompt}]}
    }

    if use_search:
        payload["tools"] = [{"google_search": {}}]

    for attempt in range(4): # up to 4 attempts
        try:
            response = await asyncio.to_thread(
                lambda: requests.post(
                    apiUrl, 
                    headers={'Content-Type': 'application/json'}, 
                    data=json.dumps(payload),
                    timeout=30 
                )
            )
            response.raise_for_status() 
            
            result = response.json()
            candidate = result.get('candidates', [{}])[0]
            
            if candidate and candidate.get('content', {}).get('parts', [{}])[0].get('text'):
                text = candidate['content']['parts'][0]['text']
                sources = []
                
                grounding_metadata = candidate.get('groundingMetadata')
                if use_search and grounding_metadata and grounding_metadata.get('groundingAttributions'):
                    sources = []
                    for attr in grounding_metadata['groundingAttributions']:
                        uri = attr.get('web', {}).get('uri')
                        title = attr.get('web', {}).get('title')
                        if uri and title:
                            sources.append(f"[{title}]({uri})")
                    
                    if sources:
                        text += "\n\n---\n**Sources:** " + " | ".join(sources)
                
                return {"text": text, "sources": sources}
            else:
                return {"text": "Error: Could not retrieve a valid text response from the AI model.", "sources": []}

        except requests.exceptions.RequestException as e:
            if attempt < 3:
                delay = 2 ** attempt
                await asyncio.sleep(delay)
            else:
                error_text = f"Error: Failed to connect to AI service after multiple retries (Status: {e}). **This often indicates your GEMINI_API_KEY in secrets.toml is invalid, expired, or has insufficient permissions.**"
                return {"text": error_text, "sources": []}
        except Exception as e:
            error_text = f"An unexpected error occurred during AI call processing: {e}"
            return {"text": error_text, "sources": []}

    return {"text": "Error: Maximum retry attempts reached.", "sources": []}


# Function to run the async AI call in a synchronous Streamlit context
def run_async_ai_call(history: List[Dict[str, Any]], system_prompt: str, use_search: bool = False) -> Dict[str, Any]:
    """Wrapper to run the async API call and return a structured dictionary."""
    
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        response_dict = loop.run_until_complete(call_gemini_api(history, system_prompt, use_search))
        return response_dict
    except Exception as e:
        return {"text": f"Error executing async call wrapper: {e}", "sources": []}

# Standard chat interface renderer
def render_chat_interface(title: str, history_key: str, system_prompt: str, use_search: bool = False):
    """Renders the AI chat interface for a specific advisor mode."""
    st.markdown(f"## {title}")
    st.markdown("<div class='subheader'>Engage the Sovereign AI interface.</div>", unsafe_allow_html=True)

    history = st.session_state[history_key]

    # --- Display Chat History ---
    with st.container(height=400, border=True):
        for message in history:
            role = "user" if message.get('is_user') else "assistant"
            
            with st.chat_message(role):
                text_content = message.get('text', 'Error: Message content missing.')
                st.markdown(text_content)

    # --- Chat Input and Logic ---
    user_query = st.chat_input("Submit your query...")

    if user_query:
        user_message = {
            "role": "user",
            "text": user_query,
            "is_user": True
        }
        st.session_state[history_key].append(user_message)
        
        with st.spinner(f"{title} thinking..."):
            ai_response_dict = run_async_ai_call(st.session_state[history_key], system_prompt, use_search)

        assistant_message = {
            "role": "model",
            "text": ai_response_dict.get('text', 'AI response failed.'),
            "is_user": False
        }
        st.session_state[history_key].append(assistant_message)
        
        st.rerun()

# --- NEW RAG CHAT INTERFACE (NOW HYBRID) ---

def render_rag_chat_interface(title: str, history_key: str, collection_name: str, base_system_prompt: str):
    """
    Renders a chat interface that uses Retrieval-Augmented Generation (RAG)
    by querying a ChromaDB collection.
    
    --- UPDATED TO "HYBRID" MODE ---
    Now also enables Google Search (`use_search=True`) and updates the system
    prompt to instruct the AI on how to use both its internal notes and external search.
    """
    st.markdown(f"## {title}")
    st.markdown(f"<div class='subheader'>Your personal coach, powered by your notes in <strong>'{collection_name}'</strong> (and Google Search).</div>", unsafe_allow_html=True)

    if not st.session_state.chroma_client:
        st.error("ChromaDB connection not established. Cannot use RAG coach.")
        return
        
    client = st.session_state.chroma_client
    
    try:
        collection = client.get_collection(name=collection_name)
    except Exception as e:
        st.error(f"Error: Collection '{collection_name}' not found or ChromaDB error.")
        st.error(f"Details: {e}")
        st.info("Please go to the 'Ingest Data' page to create this collection and add your notes.")
        return

    history = st.session_state[history_key]

    # --- Display Chat History ---
    with st.container(height=400, border=True):
        for message in history:
            role = "user" if message.get('is_user') else "assistant"
            with st.chat_message(role):
                text_content = message.get('text', 'Error: Message content missing.')
                st.markdown(text_content)

    # --- Chat Input and Logic ---
    user_query = st.chat_input(f"Ask the {title}...")

    if user_query:
        user_message = {
            "role": "user",
            "text": user_query,
            "is_user": True
        }
        st.session_state[history_key].append(user_message)
        
        with st.spinner(f"{title} is searching your notes and the web..."):
            try:
                # 2. Retrieve relevant documents from ChromaDB
                st.toast("Searching vector notes...")
                retrieved_docs = collection.query(
                    query_texts=[user_query],
                    n_results=5 
                )
                
                knowledge_chunks = retrieved_docs['documents'][0]
                
                if knowledge_chunks:
                    knowledge = "\n\n---\n\n".join(knowledge_chunks)
                    knowledge_prompt = f"""
Here is the relevant internal knowledge I found in your notes:
---
{knowledge}
---
"""
                else:
                    knowledge_prompt = "I couldn't find any relevant information in your internal notes for this specific query."
                
                # 3. Construct the final prompt for Gemini
                final_system_prompt = f"""
{base_system_prompt}

You have two sources of information:
1.  **Internal Knowledge (Your Notes):** This is your primary source of truth.
2.  **External Knowledge (Google Search):** This is your backup for general information.

**Your directive is:**
First, answer the user's query *only* using the "Internal Knowledge" provided below.
If that internal knowledge does not contain the answer, and *only* then, use your external Google Search ability to find a general answer.
Always state whether your answer is from the internal notes or from an external search.

{knowledge_prompt}
"""
                
                # 4. Call the Gemini API (NOW WITH SEARCH ENABLED)
                st.toast("Sending notes and query to AI...")
                ai_response_dict = run_async_ai_call(
                    st.session_state[history_key], 
                    final_system_prompt, 
                    use_search=True # <-- THIS IS THE UPGRADE
                )

                # 5. Add assistant message
                assistant_message = {
                    "role": "model",
                    "text": ai_response_dict.get('text', 'AI response failed.'),
                    "is_user": False
                }
                st.session_state[history_key].append(assistant_message)

            except Exception as e:
                st.error(f"An error occurred during RAG chat: {e}")
                assistant_message = {
                    "role": "model",
                    "text": f"Sorry, I encountered an error trying to search your notes: {e}",
                    "is_user": False
                }
                st.session_state[history_key].append(assistant_message)

        # Rerun to display the new messages
        st.rerun()


# --- Render Functions for each AI Coach ---

def render_v3_advisor():
    """Renders the V3 Advisor chat interface."""
    render_chat_interface(
        title="V3 Advisor (General)", 
        history_key='v3_advisor_history', 
        system_prompt="You are the V3 Advisor, a helpful and analytical coach providing guidance on personal development, productivity, and life planning, always referencing the user's Pillars and Shadows. You have access to Google Search.", 
        use_search=True
    )

def render_super_ai():
    """Renders the Super AI interface."""
    render_chat_interface(
        title="Super AI (Analysis)", 
        history_key='super_ai_history', 
        system_prompt="You are the Super AI. Your role is to analyze complex, unstructured data or queries through the lens of the user's Pillars and Shadows structure, providing deep, actionable insights and strategic analysis. You have access to Google Search.", 
        use_search=True
    )

def render_bol_academy():
    """Renders the BOL Academy interface."""
    render_chat_interface(
        title="BOL Academy (Tutor)", 
        history_key='bol_academy_history', 
        system_prompt="You are the BOL Academy dedicated tutor for the 21 Brotherhood of Light Courses, guiding the user through lessons on occultism, inner plane theory, and psychic phenomena.", 
        use_search=False # Keep this one firewalled, as it's a specific tutor
    )

def render_business_coach():
    """Renders the Business Coach RAG interface."""
    render_rag_chat_interface(
        title="💼 Business Coach (Hybrid)",
        history_key='business_coach_history',
        collection_name='business_coach_notes', # This MUST match the collection name from ingestion
        base_system_prompt="You are the V3 Business Coach for the 'Phoenix Boss of Antares'. Your role is to provide specific, actionable business advice. Your primary duty is to use the user's internal notes (their 'Sovereign OS') first. If the notes don't have the answer, use Google Search as a backup."
    )

def render_health_coach():
    """Renders the Health Coach RAG interface."""
    render_rag_chat_interface(
        title="💪 Health Coach (Hybrid)",
        history_key='health_coach_history',
        collection_name='health_coach_notes', # This MUST match the collection name from ingestion
        base_system_prompt="You are the V3 Health Coach for the 'Phoenix Boss of Antares'. Your role is to provide protocols for 'Hardware' stabilization and 'Somatic' integration. Your primary duty is to use the user's internal notes (e.g., 'Dorsal Vagal state', 'Armored Body') first. If the notes don't have the answer, use Google Search as a backup."
    )

# 4. (TEMPLATE) Create a render function for the new coach
def render_energy_somatic_coach():
    """Renders the Energy & Somatic Coach RAG interface."""
    render_rag_chat_interface(
        title="⚡ Energy & Somatic Coach (Hybrid)",
        history_key='energy_somatic_history',
        collection_name='energy_somatic_notes', # This MUST match the collection name from ingestion
        base_system_prompt="You are the V3 Energy & Somatic Coach. Your role is to provide protocols for nervous system regulation, breath, and energy projection. Your primary duty is to use the user's internal notes (e.g., 'Polyvagal Theory', 'Somatic Shaking') first. If the notes don't have the answer, use Google Search as a backup."
    )


def render_settings():
    """Renders the Settings page."""
    st.markdown("## ⚙️ System Settings & Maintenance")
    st.markdown("<div class='subheader'>Manage data integrity and system configuration.</div>", unsafe_allow_html=True)

    st.markdown("### Data Management")
    st.button("📦 Create Data Backup", on_click=create_backup, use_container_width=True)
    st.warning("Note: Full data load/restore functions are currently disabled for stability.")

    st.markdown("---")
    st.markdown("### Environment Status")
    st.json({
        "APP_ID": APP_ID,
        "User_ID": st.session_state.user_id,
        "GEMINI_MODEL": GEMINI_MODEL,
        "Firebase_Config_Loaded": bool(firebaseConfig),
        "Chroma_Client_Initialized": bool(st.session_state.chroma_client)
    })
    st.info("**AI Key Check:** If you are seeing `403 Forbidden` errors in the chat interfaces, the AI service is not receiving a valid API key. Please ensure your key is correctly set in your execution environment.", icon="🚨")

# --- Main Application Logic ---

def main_app():
    # Streamlit configuration must be the first command
    st.set_page_config(
        page_title="V3 Sovereign OS",
        page_icon="🎯",
        layout="wide"
    )

    # 1. Initialization and Data Loading
    initialize_session_state()
    load_css(get_base_path('style.css')) # Load CSS after session state setup

    # 2. Sidebar Navigation
    render_sidebar()
    
    # 3. Main Content Router
    if st.session_state.page == "Dashboard":
        render_dashboard()
    elif st.session_state.page == "Pillars & Shadows":
        render_pillars_shadows()
    elif st.session_state.page == "Goals":
        render_goals()
    elif st.session_state.page == "Tasks":
        render_tasks()
    elif st.session_state.page == "V3 Advisor":
        render_v3_advisor()
    elif st.session_state.page == "Super AI":
        render_super_ai()
    elif st.session_state.page == "BOL Academy":
        render_bol_academy()
    elif st.session_state.page == "Business Coach":
        render_business_coach() 
    elif st.session_state.page == "Health Coach":
        render_health_coach()
    # 5. (TEMPLATE) Add the new coach to the router
    elif st.session_state.page == "Energy & Somatic Coach":
        render_energy_somatic_coach()
    elif st.session_state.page == "Ingest Data":
        render_ingest_data()
    elif st.session_state.page == "Settings":
        render_settings()
    else:
        render_dashboard() # Default to dashboard if page not found

# Execute the main app function
if __name__ == "__main__":
    main_app()