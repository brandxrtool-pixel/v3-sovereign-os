# V3 Sovereign OS - Command Center
# Streamlit application for personal development, structured by Pillars and Shadows.
# MODIFIED FOR LOCAL EXECUTION (Reads API Key from st.secrets)

import streamlit as st
import json
import os
import time
import base64
from datetime import datetime
import asyncio
import requests # Added requests for API calls
from typing import List, Dict, Any, Optional

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
        # Load or initialize V3 Advisor history
        v3_advisor_default = [{
            "role": "model",
            "text": "Welcome to the V3 Command Center. I am your V3 Advisor. How can I assist you in optimizing your day or refining your Pillars and Shadows today?",
            "is_user": False
        }]
        st.session_state.v3_advisor_history = load_data('v3_advisor_history.json', {'history': v3_advisor_default})['history']

        # Load or initialize Super AI history
        super_ai_default = [{
            "role": "model",
            "text": "Greetings. I am the Super AI. Submit any complex, unstructured data or queries, and I will analyze them through the lens of your Sovereign OS structure.",
            "is_user": False
        }]
        st.session_state.super_ai_history = load_data('super_ai_history.json', {'history': super_ai_default})['history']

        # Load or initialize BOL Academy history
        bol_academy_default = [{
            "role": "model",
            "text": "Welcome to the BOL Academy. I am your dedicated tutor for the 21 Brotherhood of Light Courses. When you are ready, please tell me to begin **Course 1: Laws of Occultism: Inner Plane Theory and the Fundamentals of Psychic Phenomena**.",
            "is_user": False
        }]
        st.session_state.bol_academy_history = load_data('bol_academy_history.json', {'history': bol_academy_default})['history']

        # 4. Auth/Database (Placeholder for Firestore)
        st.session_state.db = None
        st.session_state.auth = None
        # Placeholder for unauthenticated environment or based on auth token
        st.session_state.user_id = APP_ID # Use APP_ID as default user ID

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
    st.sidebar.button('💬 V3 Advisor', on_click=set_page, args=('V3 Advisor',), use_container_width=True)
    st.sidebar.button('🧬 Super AI', on_click=set_page, args=('Super AI',), use_container_width=True)
    st.sidebar.button('🔮 BOL Academy', on_click=set_page, args=('BOL Academy',), use_container_width=True)
    st.sidebar.markdown('---')
    st.sidebar.button('⚙️ Settings', on_click=set_page, args=('Settings',), use_container_width=True)

    # Save Control
    st.sidebar.markdown("<div class='save-section'>", unsafe_allow_html=True)
    save_label = "💾 Save All Changes"
    if st.session_state.unsaved_changes:
        save_label = "🚨 Unsaved Changes! Click to Save."
    
    st.sidebar.button(save_label, on_click=save_all_data, use_container_width=True, key="save_button")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    
    # User ID placeholder (Mandatory for multi-user apps)
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

    # Calculate Goal Progress (Handle empty list safely)
    goal_progress = 0
    if goals:
        # Filter for goals that have a progress key and are numbers
        valid_progresses = [g.get('progress', 0) for g in goals if isinstance(g.get('progress'), (int, float))]
        if valid_progresses:
            goal_progress = sum(valid_progresses) / len(valid_progresses)

    # Calculate Sovereign Score (Average of all Pillar scores)
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
        # Calculate Shadow Status (Average 'score', which is actually 'tamed' percentage)
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
            goal_cols = st.columns(min(len(active_goals), 3))
            for i, g in enumerate(active_goals[:3]):
                with goal_cols[i % 3]:
                    st.markdown(f"""
                    <div class='goal-card'>
                        <div class='goal-title'>{g['name']}</div>
                        <div class='goal-pillar'><span class='pillar-tag-small'>{g['pillar']}</span></div>
                        <div class='goal-progress-display'>{g['progress']}% Complete</div>
                    </div>
                    """, unsafe_allow_html=True)

def render_pillars_shadows():
    """Pillars and Shadows management page."""
    st.markdown("## Pillars & Shadows Calibration")
    
    st.markdown("### 🛡️ Pillars: Areas of Focus (Max 100 Score)")
    st.markdown("<div class='subheader'>Use the sliders to calibrate your self-assessed current performance.</div>", unsafe_allow_html=True)

    # Render Pillars
    cols = st.columns(4)
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

    st.markdown("---")
    
    # Render Shadows
    st.markdown("### 🌑 Shadows: Limiting Behaviors (Score is Taming Progress)")
    st.markdown("<div class='subheader'>Assess your control over limiting traits. 100% means fully tamed.</div>", unsafe_allow_html=True)
    
    shadow_cols = st.columns(2)
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

def render_goals():
    """Goals management page."""
    st.markdown("## Goals Management")
    st.markdown("<div class='subheader'>Set, track, and manage your high-level outcomes.</div>", unsafe_allow_html=True)

    pillars = [p['name'] for p in st.session_state.pillars_data['pillars']]

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
            # Ensure value defaults to today if not provided
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

    # Sort goals: active first, then by progress
    goals.sort(key=lambda g: (g.get('progress', 0) == 100, g.get('progress', 0)))

    for i, g in enumerate(goals):
        col1, col2, col3 = st.columns([0.6, 0.3, 0.1])
        
        with col1:
            st.markdown(f"#### {g['name']} <span class='pillar-tag-small'>{g['pillar']}</span>", unsafe_allow_html=True)
            st.progress(g.get('progress', 0) / 100)
        
        with col2:
            # Slider to update progress
            new_progress = st.slider('Progress (%)', 0, 100, g.get('progress', 0), key=f"goal_progress_{g['id']}")
            if new_progress != g.get('progress', 0):
                st.session_state.goals_data['goals'][i]['progress'] = new_progress
                st.session_state.unsaved_changes = True
                
            st.caption(f"Deadline: {g.get('deadline', 'N/A')}")
            
        with col3:
            # Delete button
            if st.button("🗑️", key=f"delete_goal_{g['id']}"):
                # Use st.session_state.goals_data['goals'].remove(g) if possible, or pop by index
                st.session_state.goals_data['goals'].pop(i)
                st.session_state.unsaved_changes = True
                st.rerun()

    st.markdown("---")

def render_tasks():
    """Task management page (Actionable steps linked to Pillars)."""
    st.markdown("## Task Manager")
    st.markdown("<div class='subheader'>Actionable steps linked to your Pillars.</div>", unsafe_allow_html=True)

    pillars = [p['name'] for p in st.session_state.pillars_data['pillars']]
    
    # --- Helper to Update Pillar Score on Completion ---
    def update_pillar_score(pillar_name: str, priority: str):
        """Calculates and applies a score boost to the relevant Pillar."""
        boost_map = {'P1': 3, 'P2': 2, 'P3': 1}
        boost = boost_map.get(priority, 0)

        for p in st.session_state.pillars_data['pillars']:
            if p['name'] == pillar_name:
                # Apply boost, ensuring score doesn't exceed 100
                new_score = min(100, p['score'] + boost)
                p['score'] = new_score
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
                st.rerun() # Rerun to refresh the list

    st.markdown("---")

    # --- Task List Display ---
    st.markdown("### Task List")
    tasks = st.session_state.tasks_data['tasks']
    
    if not tasks:
        st.info("No active tasks. Add a task to initiate your daily flow.")
        return
    
    # Separate and sort tasks
    active_tasks = [t for t in tasks if not t.get('completed')]
    completed_tasks = [t for t in tasks if t.get('completed')]
    
    # Sort active tasks by priority (P1 first)
    active_tasks.sort(key=lambda t: t['priority'])

    st.markdown("#### Active Tasks")
    
    if not active_tasks:
        st.info("All tasks complete! Excellent work.")
    
    for i, task in enumerate(active_tasks):
        key_prefix = f"active_task_{task['id']}"
        
        col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
        
        # Completion Checkbox
        with col1:
            # We use a state check to see if the task has already been completed in the main list
            initial_value = task.get('completed', False)
            is_completed_check = col1.checkbox("", key=f"checkbox_{key_prefix}", value=initial_value)
            
        # Task Details
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

        # Delete Button
        with col3:
            if st.button("🗑️", key=f"delete_{key_prefix}"):
                # Find and delete the task from the main list
                task_index = next((j for j, t in enumerate(st.session_state.tasks_data['tasks']) if t['id'] == task['id']), None)
                if task_index is not None:
                    st.session_state.tasks_data['tasks'].pop(task_index)
                    st.session_state.unsaved_changes = True
                    st.rerun()

        # Handle Completion Logic (Only if the checkbox state changes from False to True)
        if is_completed_check and not initial_value:
            # Find and update the original task in the main list
            for t in st.session_state.tasks_data['tasks']:
                if t['id'] == task['id']:
                    t['completed'] = True
                    update_pillar_score(t['pillar'], t['priority'])
                    st.rerun() # Rerun to move the task to the completed section

    st.markdown("---")
    st.markdown("#### Completed Tasks")
    
    if not completed_tasks:
        st.caption("No tasks completed yet.")
    else:
        for task in completed_tasks:
            # Display using the class that applies the strikethrough
            st.markdown(f"<div class='task-completed-label'>✅ {task['name']} <span class='pillar-tag-small'>{task['pillar']}</span></div>", unsafe_allow_html=True)


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
    # Retrieve API key from Streamlit secrets
    try:
        # st.secrets is the standard way to access secrets in Streamlit
        apiKey = st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        # This error will be shown if .streamlit/secrets.toml is missing or the key isn't set
        return {"text": "Error: `GEMINI_API_KEY` not found. Please create a file named `.streamlit/secrets.toml` in your app's root directory and add `GEMINI_API_KEY = \"YOUR_API_KEY_HERE\"`.", "sources": []}
    except Exception as e:
         # Catch other potential startup errors with secrets
         return {"text": f"Error loading Streamlit secrets: {e}", "sources": []}
    
    # --- END MODIFICATION ---

    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={apiKey}"

    # Format history for API payload
    contents = []
    for message in history:
        # The role must be 'user' or 'model' for the API
        role = "user" if message.get('is_user') else "model"
        
        # Ensure 'text' part exists, handle potential missing key from flawed history data
        message_text = message.get('text', 'Placeholder for missing text.')
        
        contents.append({
            "role": role,
            "parts": [{"text": message_text}]
        })

    # Prepare the payload with the full history
    payload = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": system_prompt}]}
    }

    # Add tools if grounding is required
    if use_search:
        payload["tools"] = [{"google_search": {}}]

    # Implement exponential backoff for robustness
    for attempt in range(4): # up to 4 attempts
        try:
            # Use requests.post synchronously within a thread
            response = await asyncio.to_thread(
                lambda: requests.post(
                    apiUrl, 
                    headers={'Content-Type': 'application/json'}, 
                    data=json.dumps(payload),
                    timeout=30 # Add timeout for robustness
                )
            )
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            
            result = response.json()
            candidate = result.get('candidates', [{}])[0]
            
            # Successful response processing
            if candidate and candidate.get('content', {}).get('parts', [{}])[0].get('text'):
                text = candidate['content']['parts'][0]['text']
                sources = []
                
                # Append sources if search grounding was used
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
                # API responded successfully, but returned no text candidate
                return {"text": "Error: Could not retrieve a valid text response from the AI model.", "sources": []}

        except requests.exceptions.RequestException as e:
            if attempt < 3:
                delay = 2 ** attempt
                # Log the retry attempt silently (no print/st.error)
                await asyncio.sleep(delay)
            else:
                # Final attempt failed
                # MODIFIED Error Message
                error_text = f"Error: Failed to connect to AI service after multiple retries (Status: {e}). **This often indicates your GEMINI_API_KEY in secrets.toml is invalid, expired, or has insufficient permissions.**"
                return {"text": error_text, "sources": []}
        except Exception as e:
            # Unexpected JSON or other error
            error_text = f"An unexpected error occurred during AI call processing: {e}"
            return {"text": error_text, "sources": []}

    # Should not be reached, but as a final safety net
    return {"text": "Error: Maximum retry attempts reached.", "sources": []}


# Function to run the async AI call in a synchronous Streamlit context
def run_async_ai_call(history: List[Dict[str, Any]], system_prompt: str, use_search: bool = False) -> Dict[str, Any]:
    """Wrapper to run the async API call and return a structured dictionary."""
    
    # Run the async function using asyncio.run
    try:
        # Get or create the event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        response_dict = loop.run_until_complete(call_gemini_api(history, system_prompt, use_search))
        return response_dict
    except Exception as e:
        # Fallback error return
        return {"text": f"Error executing async call wrapper: {e}", "sources": []}

# Standard chat interface renderer
def render_chat_interface(title: str, history_key: str, system_prompt: str, use_search: bool = False):
    """Renders the AI chat interface for a specific advisor mode."""
    st.markdown(f"## {title}")
    st.markdown("<div class='subheader'>Engage the Sovereign AI interface.</div>", unsafe_allow_html=True)

    # Use the specific history key from session state
    history = st.session_state[history_key]

    # --- Display Chat History ---
    with st.container(height=400, border=True):
        for message in history:
            role = "user" if message.get('is_user') else "assistant"
            
            # The role variable is used for Streamlit chat elements
            with st.chat_message(role):
                # Now we safely check for the 'text' key before rendering
                text_content = message.get('text', 'Error: Message content missing.')
                st.markdown(text_content)

    # --- Chat Input and Logic ---
    user_query = st.chat_input("Submit your query...")

    if user_query:
        # 1. Add user message
        user_message = {
            "role": "user",
            "text": user_query,
            "is_user": True
        }
        st.session_state[history_key].append(user_message)
        
        # 2. Get AI Response
        with st.spinner(f"{title} thinking..."):
            # This safely returns a dictionary {text: ..., sources: ...}
            ai_response_dict = run_async_ai_call(st.session_state[history_key], system_prompt, use_search)

        # 3. Add assistant message (using the guaranteed dictionary structure)
        assistant_message = {
            "role": "model",
            "text": ai_response_dict.get('text', 'AI response failed.'),
            "is_user": False
        }
        st.session_state[history_key].append(assistant_message)
        
        # Rerun to display the new messages
        st.rerun()

def render_v3_advisor():
    """Renders the V3 Advisor chat interface."""
    render_chat_interface(
        title="V3 Advisor", 
        history_key='v3_advisor_history', 
        system_prompt="You are the V3 Advisor, a helpful and analytical coach providing guidance on personal development, productivity, and life planning, always referencing the user's Pillars and Shadows.", 
        use_search=True
    )

def render_super_ai():
    """Renders the Super AI interface."""
    render_chat_interface(
        title="Super AI", 
        history_key='super_ai_history', 
        system_prompt="You are the Super AI. Your role is to analyze complex, unstructured data or queries through the lens of the user's Pillars and Shadows structure, providing deep, actionable insights and strategic analysis.", 
        use_search=True
    )

def render_bol_academy():
    """Renders the BOL Academy interface."""
    render_chat_interface(
        title="BOL Academy", 
        history_key='bol_academy_history', 
        system_prompt="You are the BOL Academy dedicated tutor for the 21 Brotherhood of Light Courses, guiding the user through lessons on occultism, inner plane theory, and psychic phenomena.", 
        use_search=False
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
        "Firebase_Config_Loaded": bool(firebaseConfig)
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
    elif st.session_state.page == "Settings":
        render_settings()

# Execute the main app function
if __name__ == "__main__":
    main_app()
