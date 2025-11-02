# V3 Sovereign OS - Command Center
# Streamlit application for personal development, structured by Pillars and Shadows.
# Includes real-time task management and two dedicated AI coaches (V3 Advisor and BOL Academy).

import streamlit as st
import json
import os
import time
import base64
from datetime import datetime
import asyncio
from typing import List, Dict, Any, Optional

# --- Configuration ---
# Set the model name for text generation tasks
GEMINI_MODEL = "gemini-2.5-flash-preview-09-2025"

# --- Global Variables for Firestore (MUST BE USED) ---
# These variables are injected by the environment. If running locally, provide defaults.
appId = os.environ.get('__app_id', 'default-sovereign-os-id')
firebaseConfig = json.loads(os.environ.get('__firebase_config', '{}'))
initialAuthToken = os.environ.get('__initial_auth_token')

# --- Helper Functions for File/Data Management ---

def get_base_path(filename: str) -> str:
    """Gets the path for the data file."""
    # This design uses local files for demonstration.
    # For a persistent, collaborative app, this would be Firestore access.
    return os.path.join(os.path.dirname(__file__), filename)

def load_data(filename: str, default_data: Dict[str, Any]) -> Dict[str, Any]:
    """Loads data from a JSON file with error handling."""
    filepath = get_base_path(filename)
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            # Ensure the structure exists (e.g., 'goals' key is present)
            for key, default_value in default_data.items():
                if key not in data:
                    data[key] = default_value
            return data
    except FileNotFoundError:
        st.warning(f"Data file not found: {filename}. Initializing with default data.")
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

        # Save Chat Histories
        with open(get_base_path('v3_advisor_history.json'), 'w') as f:
            json.dump(st.session_state.v3_advisor_history, f, indent=4)
        with open(get_base_path('super_ai_history.json'), 'w') as f:
            json.dump(st.session_state.super_ai_history, f, indent=4)
        with open(get_base_path('bol_academy_history.json'), 'w') as f:
            json.dump(st.session_state.bol_academy_history, f, indent=4)

        st.toast("✅ All data saved successfully!", icon="💾")
        st.session_state.unsaved_changes = False

    except Exception as e:
        st.error(f"An error occurred during save: {e}")

def create_backup():
    """Creates a zip archive of all current JSON data files."""
    st.info("Backup functionality would typically create a ZIP file of all JSONs here.")
    st.toast("Backup data created!", icon="📦")
    # In a real environment, you would use 'zipfile' module here.
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

        # 3. Chat Histories
        # Load or initialize V3 Advisor history
        v3_advisor_default = [{
            "role": "assistant",
            "text": "Welcome to the V3 Command Center. I am your V3 Advisor. How can I assist you in optimizing your day or refining your Pillars and Shadows today?",
            "is_user": False
        }]
        st.session_state.v3_advisor_history = load_data('v3_advisor_history.json', {'history': v3_advisor_default})['history']

        # Load or initialize Super AI history
        super_ai_default = [{
            "role": "assistant",
            "text": "Greetings. I am the Super AI. Submit any complex, unstructured data or queries, and I will analyze them through the lens of your Sovereign OS structure.",
            "is_user": False
        }]
        st.session_state.super_ai_history = load_data('super_ai_history.json', {'history': super_ai_default})['history']

        # Load or initialize BOL Academy history
        bol_academy_default = [{
            "role": "assistant",
            "text": "Welcome to the BOL Academy. I am your dedicated tutor for the 21 Brotherhood of Light Courses. When you are ready, please tell me to begin **Course 1: Laws of Occultism: Inner Plane Theory and the Fundamentals of Psychic Phenomena**.",
            "is_user": False
        }]
        st.session_state.bol_academy_history = load_data('bol_academy_history.json', {'history': bol_academy_default})['history']

        # 4. Auth/Database (Placeholder for Firestore)
        st.session_state.db = None
        st.session_state.auth = None
        st.session_state.user_id = "default_user" # Placeholder for unauthenticated environment

# --- Styling and UI Functions ---

def load_css(filepath: str):
    """Injects custom CSS from a file."""
    try:
        with open(filepath) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file not found at {filepath}")

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
    if goals and goals[0] and goals[0].get('progress') is not None:
        goal_progress = sum([g.get('progress', 0) for g in goals]) / len(goals)
    else:
        goal_progress = 0

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
            st.session_state.pillars_data['pillars'][i]['score'] = new_score
            
            new_focus = st.text_area('Core Focus', p['focus'], key=f"pillar_focus_{p['name']}")
            st.session_state.pillars_data['pillars'][i]['focus'] = new_focus
            
            if new_score != p['score'] or new_focus != p['focus']:
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
            st.session_state.shadows_data['shadows'][i]['score'] = new_score
            
            new_focus = st.text_area('Integration Focus', s['focus'], key=f"shadow_focus_{s['name']}")
            st.session_state.shadows_data['shadows'][i]['focus'] = new_focus
            
            if new_score != s['score'] or new_focus != s['focus']:
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
            goal_deadline = st.date_input("Target Deadline", min_value=datetime.now().date(), value=datetime.now().date())
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
            is_completed = col1.checkbox("", key=f"checkbox_{key_prefix}", value=False)
            
        # Task Details
        with col2:
            task_style = 'task-completed' if task.get('completed') else 'task-pending'
            st.markdown(f"""
            <div class='{task_style}'>
                **{task['name']}**
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

        # Handle Completion Logic
        if is_completed:
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
            st.markdown(f"<div class='task-completed-label'>✅ {task['name']} <span class='pillar-tag-small'>{task['pillar']}</span></div>", unsafe_allow_html=True)


# --- AI Coach Functions ---

async def call_gemini_api(history: List[Dict[str, Any]], system_prompt: str, use_search: bool = False) -> str:
    """Handles the async API call to Gemini with backoff."""
    apiKey = ""
    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={apiKey}"

    # Format history for API payload
    contents = []
    for message in history:
        contents.append({
            "role": "user" if message['is_user'] else "model",
            "parts": [{"text": message['text']}]
        })
    
    # Get the latest user message content
    user_query = contents[-1]["parts"][0]["text"]
    
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
            response = await asyncio.to_thread(
                lambda: requests.post(
                    apiUrl, 
                    headers={'Content-Type': 'application/json'}, 
                    data=json.dumps(payload)
                )
            )
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            
            result = response.json()
            candidate = result.get('candidates', [{}])[0]
            
            if candidate and candidate.get('content', {}).get('parts', [{}])[0].get('text'):
                text = candidate['content']['parts'][0]['text']
                
                # Append sources if search grounding was used
                sources_text = ""
                grounding_metadata = candidate.get('groundingMetadata')
                if use_search and grounding_metadata and grounding_metadata.get('groundingAttributions'):
                    sources = []
                    for attr in grounding_metadata['groundingAttributions']:
                        uri = attr.get('web', {}).get('uri')
                        title = attr.get('web', {}).get('title')
                        if uri and title:
                            sources.append(f"[{title}]({uri})")
                    
                    if sources:
                        sources_text = "\n\n---\n**Sources:** " + " | ".join(sources)
                
                return text + sources_text
            else:
                return "Error: Could not retrieve a valid response from the AI model."

        except requests.exceptions.RequestException as e:
            if attempt < 3:
                delay = 2 ** attempt
                # print(f"API Error: {e}. Retrying in {delay} seconds...") # Do not log retries
                await asyncio.sleep(delay)
            else:
                return f"Error: Failed to connect to AI service after multiple retries. ({e})"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    return "Error: Maximum retry attempts reached."

# Function to run the async AI call in a synchronous Streamlit context
def run_async_ai_call(history: List[Dict[str, Any]], system_prompt: str, use_search: bool = False):
    """Wrapper to run the async API call and handle result update."""
    
    # Placeholder for requests library check (needed for the API call)
    try:
        global requests
        import requests
    except ImportError:
        st.error("The 'requests' library is required for the AI Coach functionality. Please install it.")
        return "Error: 'requests' library not installed."

    # Run the async function using asyncio.run
    try:
        response = asyncio.run(call_gemini_api(history, system_prompt, use_search))
        return response
    except Exception as e:
        return f"Error executing async call: {e}"

# Standard chat interface renderer
def render_chat_interface(title: str, history_key: str, system_prompt: str, use_search: bool = False):
    """Renders the standard chat UI."""
    st.markdown(f"## {title}")
    st.markdown("<div class='subheader'>Your dedicated AI interface.</div>", unsafe_allow_html=True)

    # Display chat messages from history
    for message in st.session_state[history_key]:
        with st.chat_message("user" if message['is_user'] else "assistant"):
            st.markdown(message['text'])
            
    # Input field for user
    if user_prompt := st.chat_input("Ask your coach..."):
        # Add user message to history
        st.session_state[history_key].append({"role": "user", "text": user_prompt, "is_user": True})
        
        # Display the user message immediately
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                response = run_async_ai_call(st.session_state[history_key], system_prompt, use_search)
                st.markdown(response)
        
        # Add assistant response to history
        st.session_state[history_key].append({"role": "assistant", "text": response, "is_user": False})
        st.session_state.unsaved_changes = True
        st.rerun() # Rerun to refresh the chat window properly

def render_v3_advisor():
    """Renders the V3 Advisor (General Coaching) chat page."""
    system_prompt = (
        "You are the V3 Advisor, a highly structured, analytical life coach and system optimizer. "
        "Your role is to help the user refine their Pillars, mitigate their Shadows, and achieve their Goals. "
        "Always respond concisely, focusing on practical actions, clear frameworks, and strategic thinking. "
        "Do not use emojis unless specifically requested."
    )
    render_chat_interface(
        title="💬 V3 Advisor (General Coaching)", 
        history_key='v3_advisor_history', 
        system_prompt=system_prompt, 
        use_search=False
    )

def render_super_ai():
    """Renders the Super AI (Data Analysis) chat page."""
    system_prompt = (
        "You are the Super AI. Your function is to analyze complex data, unstructured text, or vast information "
        "and distill it through a highly rational, objective, and strategic filter. "
        "Assume the user is a high-level sovereign operator. Use cold, logical, and highly concise language. "
        "Your goal is to extract key insights, highlight hidden risks, and suggest optimal strategies. "
        "You have access to Google Search for grounding your analysis."
    )
    render_chat_interface(
        title="🧬 Super AI (Strategic Analysis)", 
        history_key='super_ai_history', 
        system_prompt=system_prompt, 
        use_search=True
    )

def render_bol_academy():
    """Renders the Brotherhood of Light Academy page."""
    system_prompt = (
        "You are the dedicated tutor for the 21 Brotherhood of Light (Church of Light) Courses. "
        "Your mission is to deliver the course material chapter-by-chapter, based on publicly available sources. "
        "When the user asks to start a course or chapter, use Google Search to find the specific content. "
        "Structure each lesson clearly, and conclude with a small reflective exercise or a few comprehension questions. "
        "Only move to the next chapter or course when the user indicates they are ready. "
        "The first course is: 'Laws of Occultism: Inner Plane Theory and the Fundamentals of Psychic Phenomena'."
    )
    render_chat_interface(
        title="🔮 BOL Academy (Course Tutor)", 
        history_key='bol_academy_history', 
        system_prompt=system_prompt, 
        use_search=True
    )

# --- Settings Page ---

def render_settings():
    """Renders the settings and maintenance page."""
    st.markdown("## System Settings")
    st.markdown("<div class='subheader'>Maintenance and Configuration</div>", unsafe_allow_html=True)
    
    st.markdown("### Data Management")
    st.button("📦 Create Data Backup (Download all JSONs)", on_click=create_backup, use_container_width=True)
    st.caption("Creates a snapshot of your current Pillars, Shadows, Goals, and Chat histories.")

    st.markdown("### Clear History")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Clear V3 Advisor History", use_container_width=True):
            st.session_state.v3_advisor_history = [{"role": "assistant", "text": "Welcome back! History cleared.", "is_user": False}]
            st.session_state.unsaved_changes = True
            st.rerun()
            
    with col2:
        if st.button("Clear Super AI History", use_container_width=True):
            st.session_state.super_ai_history = [{"role": "assistant", "text": "Rebooting analysis engine. History cleared.", "is_user": False}]
            st.session_state.unsaved_changes = True
            st.rerun()

    with col3:
        if st.button("Clear BOL Academy History", use_container_width=True):
            st.session_state.bol_academy_history = [{"role": "assistant", "text": "Academy history reset. Ready for Course 1.", "is_user": False}]
            st.session_state.unsaved_changes = True
            st.rerun()
            
    st.markdown("---")
    
    st.markdown("### System Information")
    st.markdown(f"""
    - **App ID:** `{appId}`
    - **Model Used:** `{GEMINI_MODEL}`
    - **Authentication Status:** {'Authenticated' if initialAuthToken else 'Unauthenticated/Anonymous'}
    - **Firebase Config Loaded:** {'Yes' if firebaseConfig else 'No'}
    """)


# --- Main Application Execution ---

def main():
    """Main entry point for the Streamlit application."""
    st.set_page_config(layout="wide", page_title="V3 Sovereign OS")
    
    # 1. Load CSS
    load_css(get_base_path('style.css'))
    
    # 2. Initialize Data and State
    initialize_session_state()

    # 3. Render Sidebar
    render_sidebar()

    # 4. Render Main Content based on State
    if st.session_state.page == 'Dashboard':
        render_dashboard()
    elif st.session_state.page == 'Pillars & Shadows':
        render_pillars_shadows()
    elif st.session_state.page == 'Goals':
        render_goals()
    elif st.session_state.page == 'Tasks':
        render_tasks()
    elif st.session_state.page == 'V3 Advisor':
        render_v3_advisor()
    elif st.session_state.page == 'Super AI':
        render_super_ai()
    elif st.session_state.page == 'BOL Academy':
        render_bol_academy()
    elif st.session_state.page == 'Settings':
        render_settings()
        
    # 5. Check for missing packages (requests for AI)
    try:
        import requests
    except ImportError:
        st.sidebar.warning("🚨 Missing 'requests' package. AI coaches are disabled. Run `pip install requests`.")


if __name__ == '__main__':
    main()
