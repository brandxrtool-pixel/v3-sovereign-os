import streamlit as st
import json
import os
import requests
from datetime import datetime, date

# NEW IMPORTS FOR FIRESTORE
import firebase_admin
from firebase_admin import credentials, firestore

# --- Global Configs and Constants ---

# Access environment variables/secrets for configuration
# In the Canvas environment, __firebase_config is available in st.secrets.
# We access it via st.secrets for Streamlit Cloud deployment compatibility.
try:
    FIREBASE_CONFIG_DICT = st.secrets["__firebase_config"]
except:
    # Fallback for local testing if secrets are not set up.
    # NOTE: You MUST set up secrets for deployment to Streamlit Cloud!
    st.error("FATAL: '__firebase_config' not found in Streamlit secrets. Persistence will fail.")
    FIREBASE_CONFIG_DICT = {"type": "mock", "project_id": "mock-v3-sovereign-os"}

# Access App ID (Mandatory for Canvas path structure)
APP_ID = st.secrets.get("__app_id", "default-v3-app-id")

# Placeholder for user ID. In a real multi-user Streamlit app, this would come from an Auth flow.
# For now, we hardcode it since the Canvas environment provides a secure, single-user context.
USER_ID = "default_user" 

# Base URL for the AI Coach backend (using a mock/placeholder endpoint)
# NOTE: Replace this with your actual, secured endpoint when ready.
AI_ENDPOINT = "https://mock-ai-coach-api.com/v3"

# --- FIRESTORE UTILITIES (Replacing File I/O) ---

@st.cache_resource(show_spinner=False)
def initialize_firebase():
    """Initializes the Firebase Admin SDK once."""
    if not firebase_admin._apps:
        try:
            # Initialize with Service Account credentials
            cred = credentials.Certificate(FIREBASE_CONFIG_DICT)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            return db
        except Exception as e:
            st.error(f"Error initializing Firebase: {e}")
            return None
    return firestore.client()

def get_data_path(doc_name):
    """Generates the secure Firestore document path."""
    # Path format for private data: /artifacts/{appId}/users/{userId}/{docName}
    return f"artifacts/{APP_ID}/users/{USER_ID}/{doc_name}"

def load_firestore_data(doc_name, default_data):
    """
    Loads data from Firestore. If the document does not exist, it creates it
    and returns the default data.

    Returns: A dictionary with the loaded data.
    """
    db = st.session_state.db
    if db is None:
        st.warning("Database connection failed. Using default data locally.")
        return default_data

    doc_path = get_data_path(doc_name)
    doc_ref = db.document(doc_path)

    try:
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            # Safety check: Ensure loaded data is a dict before returning
            if isinstance(data, dict):
                return data
            else:
                st.warning(f"Data from Firestore for {doc_name} is corrupted (not a dictionary). Using default data.")
                doc_ref.set(default_data) # Overwrite corrupted data
                return default_data

        else:
            # Document doesn't exist, create it with default data
            doc_ref.set(default_data)
            return default_data
    except Exception as e:
        st.error(f"Error loading data from Firestore ({doc_name}): {e}")
        return default_data


def save_firestore_data(doc_name, data):
    """Saves data to a Firestore document."""
    db = st.session_state.db
    if db is None:
        st.warning("Database connection failed. Cannot save data.")
        return False

    doc_path = get_data_path(doc_name)
    doc_ref = db.document(doc_path)

    try:
        # Use set to overwrite the entire document
        doc_ref.set(data)
        return True
    except Exception as e:
        st.error(f"Error saving data to Firestore ({doc_name}): {e}")
        return False

# --- DATA STRUCTURES (Defaults) ---

default_pillars = [
    {"id": "p1", "name": "Health", "description": "Physical, mental, and nutritional well-being.", "goals": 0, "completed": 0, "color": "#10B981"},
    {"id": "p2", "name": "Wealth", "description": "Financial independence and resource management.", "goals": 0, "completed": 0, "color": "#F59E0B"},
    {"id": "p3", "name": "Wisdom", "description": "Continuous learning and intellectual growth.", "goals": 0, "completed": 0, "color": "#3B82F6"},
]

default_shadows = [
    {"id": "s1", "name": "Procrastination", "description": "The shadow of delay.", "tamed": False},
    {"id": "s2", "name": "Impatience", "description": "The shadow of haste.", "tamed": False},
]

default_goals = []
default_tasks = []

# Initial chat messages for history
initial_v3_advisor_message = {"role": "ai", "content": "Welcome back, Sovereign. How can I assist you in optimizing your operational flow today?"}
initial_super_ai_message = {"role": "ai", "content": "Query initiated. What complex system or data requires Super AI analysis?"}
initial_bol_academy_message = {"role": "ai", "content": "Ready for instruction. Which knowledge segment shall we activate?"}

# --- KPI Calculation ---

def calculate_kpis():
    """Calculates Sovereign Score, Goal Completion, and Shadow Taming metrics."""
    total_goals = sum(p['goals'] for p in st.session_state.pillars)
    completed_goals = sum(p['completed'] for p in st.session_state.pillars)

    goal_completion_pct = (completed_goals / total_goals) * 100 if total_goals > 0 else 0.0

    total_shadows = len(st.session_state.shadows)
    tamed_shadows = sum(1 for s in st.session_state.shadows if s['tamed'])
    shadow_tamed_pct = (tamed_shadows / total_shadows) * 100 if total_shadows > 0 else 0.0

    # Simplified Sovereign Score calculation
    sovereign_score = (goal_completion_pct * 0.4) + (shadow_tamed_pct * 0.6)
    
    st.session_state.kpis = {
        "sovereign_score": f"{sovereign_score:.1f}%",
        "goal_completion": f"{goal_completion_pct:.1f}%",
        "shadow_tamed": f"{shadow_tamed_pct:.1f}%",
    }


# --- State Management and Firestore I/O ---

def save_all_data():
    """Saves all current session state data to Firestore."""
    save_firestore_data('pillars', {'pillars': st.session_state.pillars})
    save_firestore_data('shadows', {'shadows': st.session_state.shadows})
    save_firestore_data('goals_detailed', {'goals': st.session_state.goals_detailed})
    save_firestore_data('tasks', {'tasks': st.session_state.tasks})
    save_firestore_data('v3_advisor_history', {'history': st.session_state.v3_advisor_history})
    save_firestore_data('super_ai_history', {'history': st.session_state.super_ai_history})
    save_firestore_data('bol_academy_history', {'history': st.session_state.bol_academy_history})


def initialize_session_state():
    """Initializes Streamlit session state variables and connects to Firestore."""
    if 'initialized' not in st.session_state:
        # 1. Initialize DB Connection
        st.session_state.db = initialize_firebase()

        # 2. Load Core Data using Firestore
        st.session_state.pillars = load_firestore_data('pillars', {'pillars': default_pillars})['pillars']
        st.session_state.shadows = load_firestore_data('shadows', {'shadows': default_shadows})['shadows']
        st.session_state.goals_detailed = load_firestore_data('goals_detailed', {'goals': default_goals})['goals']
        st.session_state.tasks = load_firestore_data('tasks', {'tasks': default_tasks})['tasks']

        # 3. Load Chat History Data using Firestore
        v3_advisor_default = {"history": [initial_v3_advisor_message]}
        super_ai_default = {"history": [initial_super_ai_message]}
        bol_academy_default = {"history": [initial_bol_academy_message]}

        st.session_state.v3_advisor_history = load_firestore_data('v3_advisor_history', v3_advisor_default)['history']
        st.session_state.super_ai_history = load_firestore_data('super_ai_history', super_ai_default)['history']
        st.session_state.bol_academy_history = load_firestore_data('bol_academy_history', bol_academy_default)['history']

        # 4. Initialize UI State
        st.session_state.selected_tab = 'Dashboard'
        st.session_state.show_add_pillar = False
        st.session_state.show_add_goal = False
        st.session_state.show_add_task = False
        st.session_state.edit_mode = False
        st.session_state.initialized = True
        st.session_state.user_id = USER_ID # Setting placeholder user ID

    # 5. Calculate KPIs after loading/initialization
    calculate_kpis()


# --- Action Handlers (All call save_all_data) ---

def handle_task_completion(task_id):
    """Marks a task as complete and updates relevant goals/pillars."""
    # Find and mark task
    for task in st.session_state.tasks:
        if task['id'] == task_id:
            task['completed'] = True
            break
    
    # Update goal progress (simplified: check if all tasks in a goal are done)
    # Goal logic can be complex; simplified here for demonstration.
    for goal in st.session_state.goals_detailed:
        goal_tasks = [t for t in st.session_state.tasks if t['goal_id'] == goal['id']]
        if goal_tasks and all(t['completed'] for t in goal_tasks):
            goal['completed'] = True

            # Update pillar progress
            for pillar in st.session_state.pillars:
                if pillar['id'] == goal['pillar_id']:
                    pillar['completed'] += 1
                    break
    
    save_all_data()
    calculate_kpis()

def handle_goal_completion(goal_id):
    """Marks a goal as complete and updates the parent pillar count."""
    for goal in st.session_state.goals_detailed:
        if goal['id'] == goal_id:
            if not goal['completed']:
                goal['completed'] = True
                
                # Update pillar completion count
                for pillar in st.session_state.pillars:
                    if pillar['id'] == goal['pillar_id']:
                        pillar['completed'] += 1
                        break
            break
    save_all_data()
    calculate_kpis()

def handle_pillar_completion(pillar_id):
    """Marks all goals/tasks under a pillar as complete."""
    # Simplified: This action marks all related goals as complete.
    for goal in st.session_state.goals_detailed:
        if goal['pillar_id'] == pillar_id and not goal['completed']:
            goal['completed'] = True
            
            # Update pillar count
            for pillar in st.session_state.pillars:
                if pillar['id'] == pillar_id:
                    pillar['completed'] += 1
                    break
    save_all_data()
    calculate_kpis()


def handle_task_delete(task_id):
    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task_id]
    save_all_data()
    calculate_kpis()

def handle_goal_delete(goal_id):
    # Decrement goal count on parent pillar
    goal_to_delete = next((g for g in st.session_state.goals_detailed if g['id'] == goal_id), None)
    if goal_to_delete:
        for pillar in st.session_state.pillars:
            if pillar['id'] == goal_to_delete['pillar_id']:
                pillar['goals'] -= 1
                if goal_to_delete['completed']:
                    pillar['completed'] -= 1
                break
        
        # Delete goal
        st.session_state.goals_detailed = [g for g in st.session_state.goals_detailed if g['id'] != goal_id]
        
        # Delete related tasks
        st.session_state.tasks = [t for t in st.session_state.tasks if t['goal_id'] != goal_to_delete['id']] # Ensure we use the deleted goal ID
    
    save_all_data()
    calculate_kpis()

def handle_pillar_delete(pillar_id):
    # Delete associated goals and tasks first
    goals_to_delete = [g for g in st.session_state.goals_detailed if g['pillar_id'] == pillar_id]
    goal_ids_to_delete = [g['id'] for g in goals_to_delete]
    
    st.session_state.goals_detailed = [g for g in st.session_state.goals_detailed if g['pillar_id'] != pillar_id]
    st.session_state.tasks = [t for t in st.session_state.tasks if t['goal_id'] not in goal_ids_to_delete]

    # Delete pillar
    st.session_state.pillars = [p for p in st.session_state.pillars if p['id'] != pillar_id]

    save_all_data()
    calculate_kpis()

def handle_pillar_submit(name, description, color):
    new_id = f"p{len(st.session_state.pillars) + 1}"
    st.session_state.pillars.append({
        "id": new_id,
        "name": name,
        "description": description,
        "goals": 0,
        "completed": 0,
        "color": color,
    })
    st.session_state.show_add_pillar = False
    save_all_data()
    calculate_kpis()

def handle_goal_submit(pillar_id, name, description, priority):
    new_id = f"g{len(st.session_state.goals_detailed) + 1}"
    st.session_state.goals_detailed.append({
        "id": new_id,
        "pillar_id": pillar_id,
        "name": name,
        "description": description,
        "priority": priority,
        "created_date": date.today().isoformat(),
        "completed": False
    })
    # Increment goal count on parent pillar
    for pillar in st.session_state.pillars:
        if pillar['id'] == pillar_id:
            pillar['goals'] += 1
            break
            
    st.session_state.show_add_goal = False
    save_all_data()
    calculate_kpis()

def handle_task_submit(goal_id, name, description):
    new_id = f"t{len(st.session_state.tasks) + 1}"
    st.session_state.tasks.append({
        "id": new_id,
        "goal_id": goal_id,
        "name": name,
        "description": description,
        "completed": False
    })
    st.session_state.show_add_task = False
    save_all_data()
    calculate_kpis()

def handle_shadow_tame(shadow_id):
    for shadow in st.session_state.shadows:
        if shadow['id'] == shadow_id:
            shadow['tamed'] = not shadow['tamed']
            break
    save_all_data()
    calculate_kpis()

# --- Utility Functions for Rendering ---

def get_pillar_color(pillar_id):
    """Returns the color hex for a given pillar ID."""
    pillar = next((p for p in st.session_state.pillars if p['id'] == pillar_id), None)
    return pillar['color'] if pillar else "#CCCCCC"

# --- UI Rendering (Tab Functions) ---

def render_dashboard_tab():
    st.header("Command Center Dashboard")
    st.markdown("---")
    
    # KPI Metrics
    st.subheader("Real-Time System Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Sovereign Score", st.session_state.kpis['sovereign_score'], delta="System Status")
    with col2:
        st.metric("Goal Completion", st.session_state.kpis['goal_completion'], delta="Operational Progress")
    with col3:
        st.metric("Shadow Tamed", st.session_state.kpis['shadow_tamed'], delta="Inner Mastery")
        
    st.markdown("---")

    # Pillar Overview
    st.subheader("Pillar Status (Foundational Pillars)")
    
    # Calculate the number of columns based on the number of pillars, min 1, max 4 (for small screens)
    num_pillars = len(st.session_state.pillars)
    num_cols = min(num_pillars, 4) if num_pillars > 0 else 1
    cols = st.columns(num_cols)
    
    if st.session_state.pillars:
        for i, pillar in enumerate(st.session_state.pillars):
            # Use modulo to cycle through the columns
            with cols[i % num_cols]:
                progress_pct = (pillar['completed'] / pillar['goals']) * 100 if pillar['goals'] > 0 else 0
                st.markdown(
                    f"""
                    <div class="pillar-card" style="border-left: 5px solid {pillar['color']};">
                        <p style='font-size: 1.2rem; font-weight: 600; color: #111827;'>{pillar['name']}</p>
                        <p style='font-size: 0.85rem; margin-top: -10px; color: #4B5563;'>{pillar['description']}</p>
                        <p style='font-size: 0.8rem; margin-top: 10px; color: #4B5563;'>Goals: {pillar['completed']} / {pillar['goals']}</p>
                        <p style='font-size: 1.5rem; font-weight: 700; color: {pillar['color']}; margin-top: -10px;'>{progress_pct:.0f}%</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
    else:
        st.info("No Pillars defined. Navigate to Pillars to begin your foundation.")

    st.markdown("---")

    # Task Snapshot (Show highest priority tasks)
    st.subheader("Immediate Operational Focus (Tasks)")
    if st.session_state.tasks:
        priority_tasks = sorted(
            [t for t in st.session_state.tasks if not t['completed']], 
            key=lambda t: t['goal_id']
        )[:5] # Show top 5
        
        for task in priority_tasks:
            goal = next((g for g in st.session_state.goals_detailed if g['id'] == task['goal_id']), None)
            pillar_color = get_pillar_color(goal['pillar_id']) if goal else "#CCCCCC"
            
            st.markdown(
                f"""
                <div class="protocol-item" style="border-left: 4px solid {pillar_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <p style='font-weight: 600; margin: 0;'>{task['name']}</p>
                        <span style='font-size: 0.75rem; color: #6B7280;'>Goal: {goal['name'] if goal else 'N/A'}</span>
                    </div>
                    <p style='font-size: 0.8rem; color: #4B5563; margin: 5px 0 0 0;'>{task['description']}</p>
                </div>
                """, unsafe_allow_html=True
            )
    else:
        st.info("No active tasks found. Time to define your first objective.")
        
def render_pillars_tab():
    st.header("Pillars and Goals Management")
    st.markdown("---")
    
    # Pillar Addition Form
    if st.session_state.show_add_pillar:
        with st.form("new_pillar_form", clear_on_submit=True):
            st.subheader("Define New Pillar")
            name = st.text_input("Pillar Name (e.g., Health, Wealth)", max_chars=30)
            description = st.text_area("Pillar Directive (Brief Description)")
            color = st.color_picker("Accent Color", "#10B981")
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                submitted = st.form_submit_button("Submit Pillar")
            with col_b2:
                if st.form_submit_button("Cancel"):
                    st.session_state.show_add_pillar = False
                    st.rerun()

            if submitted and name and description:
                handle_pillar_submit(name, description, color)
                st.session_state.show_add_pillar = False
                st.success(f"Pillar '{name}' created.")
                st.rerun()
    else:
        st.button("➕ Add New Pillar", on_click=lambda: st.session_state.update(show_add_pillar=True, show_add_goal=False))
        
    st.markdown("---")

    # Pillar and Goal Display
    for pillar in st.session_state.pillars:
        with st.expander(f"**{pillar['name']}** | {pillar['description']} ({pillar['completed']}/{pillar['goals']} Goals Complete)", expanded=True):
            
            # Action buttons for Pillar
            col_p1, col_p2, col_p3 = st.columns([1, 1, 4])
            with col_p1:
                st.button("➕ Add Goal", key=f"add_goal_{pillar['id']}", on_click=lambda p_id=pillar['id']: st.session_state.update(show_add_goal=True, selected_pillar_id=p_id, show_add_pillar=False))
            with col_p2:
                if st.button("🗑️ Delete Pillar", key=f"del_pillar_{pillar['id']}"):
                    handle_pillar_delete(pillar['id'])
                    st.success(f"Pillar '{pillar['name']}' deleted.")
                    st.rerun()
            
            st.markdown(f"<div style='border-top: 2px solid {pillar['color']}; margin-top: 15px; margin-bottom: 20px;'></div>", unsafe_allow_html=True)
            
            # Goal Display / Addition Form
            
            if st.session_state.show_add_goal and st.session_state.selected_pillar_id == pillar['id']:
                 with st.form(f"new_goal_form_{pillar['id']}", clear_on_submit=True):
                    st.subheader(f"Define New Goal for {pillar['name']}")
                    name = st.text_input("Goal Directive (Name)", max_chars=50)
                    description = st.text_area("Detailed Objective")
                    priority = st.selectbox("Priority Level", ["High", "Medium", "Low"])
                    
                    col_g1, col_g2 = st.columns(2)
                    with col_g1:
                        submitted = st.form_submit_button("Submit Goal")
                    with col_g2:
                        if st.form_submit_button("Cancel Goal"):
                            st.session_state.show_add_goal = False
                            st.rerun()

                    if submitted and name and description:
                        handle_goal_submit(pillar['id'], name, description, priority)
                        st.session_state.show_add_goal = False
                        st.success(f"Goal '{name}' created for {pillar['name']}.")
                        st.rerun()
            
            # List Existing Goals
            pillar_goals = sorted(
                [g for g in st.session_state.goals_detailed if g['pillar_id'] == pillar['id']], 
                key=lambda x: x['priority'], reverse=True
            )
            
            if not pillar_goals:
                st.info("No goals defined for this Pillar.")
            
            for goal in pillar_goals:
                st.markdown(
                    f"""
                    <div style="background-color: {'#F0FDF4' if goal['completed'] else '#FFFFFF'}; 
                                border: 1px solid {'#BBF7D0' if goal['completed'] else '#E5E7EB'};
                                border-radius: 8px; padding: 1rem; margin-bottom: 10px;
                                border-left: 4px solid {pillar['color']};
                                box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <p style='font-size: 1.1rem; font-weight: 600; color: #111827; margin: 0;'>
                                {'✅' if goal['completed'] else ''} {goal['name']}
                            </p>
                            <span style='font-size: 0.75rem; color: #6B7280;'>Priority: {goal['priority']}</span>
                        </div>
                        <p style='font-size: 0.85rem; color: #4B5563; margin: 5px 0;'>{goal['description']}</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                col_g_act1, col_g_act2, col_g_act3 = st.columns([1, 1, 4])
                with col_g_act1:
                    st.button("✅ Complete", key=f"comp_goal_{goal['id']}", disabled=goal['completed'], on_click=lambda g_id=goal['id']: handle_goal_completion(g_id))
                with col_g_act2:
                    st.button("🗑️ Delete", key=f"del_goal_{goal['id']}", on_click=lambda g_id=goal['id']: handle_goal_delete(g_id))
                
            st.markdown("</div>", unsafe_allow_html=True) # Close the expander styling div if any

def render_tasks_tab():
    st.header("Task Management")
    st.markdown("---")
    
    # Task Addition Form
    if st.session_state.show_add_task:
        with st.form("new_task_form", clear_on_submit=True):
            st.subheader("Define New Task")
            
            # Dropdown for selecting parent goal
            goal_options = {g['id']: f"{g['name']} ({next((p['name'] for p in st.session_state.pillars if p['id'] == g['pillar_id']), 'N/A')})" for g in st.session_state.goals_detailed}
            selected_goal_name = st.selectbox("Assign to Goal", list(goal_options.values()))
            
            # Reverse map to get the ID
            selected_goal_id = next((k for k, v in goal_options.items() if v == selected_goal_name), None)

            name = st.text_input("Task Name (Action Item)", max_chars=50)
            description = st.text_area("Task Details")
            
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                submitted = st.form_submit_button("Submit Task")
            with col_t2:
                if st.form_submit_button("Cancel Task"):
                    st.session_state.show_add_task = False
                    st.rerun()

            if submitted and selected_goal_id and name and description:
                handle_task_submit(selected_goal_id, name, description)
                st.session_state.show_add_task = False
                st.success(f"Task '{name}' created.")
                st.rerun()
    else:
        if st.session_state.goals_detailed:
            st.button("➕ Add New Task", on_click=lambda: st.session_state.update(show_add_task=True, show_add_goal=False))
        else:
            st.warning("You must define a Pillar and a Goal before adding tasks.")
    
    st.markdown("---")
    
    # Task Display
    st.subheader("Active Tasks")
    
    tasks_display = sorted(
        st.session_state.tasks, 
        key=lambda x: x['completed']
    ) # Sort incomplete tasks first
    
    if not tasks_display:
        st.info("The operational flow is clear. No tasks currently active.")
        
    for task in tasks_display:
        goal = next((g for g in st.session_state.goals_detailed if g['id'] == task['goal_id']), None)
        pillar_color = get_pillar_color(goal['pillar_id']) if goal else "#CCCCCC"

        with st.container():
            st.markdown(
                f"""
                <div class="protocol-item" style="border-left: 4px solid {pillar_color}; background-color: {'#F0FDF4' if task['completed'] else '#FFFFFF'};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <p style='font-weight: 600; margin: 0; color: #111827;'>
                            {'✅' if task['completed'] else ''} {task['name']}
                        </p>
                        <span style='font-size: 0.75rem; color: #6B7280;'>Goal: {goal['name'] if goal else 'N/A'}</span>
                    </div>
                    <p style='font-size: 0.8rem; color: #4B5563; margin: 5px 0 0 0;'>{task['description']}</p>
                </div>
                """, unsafe_allow_html=True
            )
            
            col_t_act1, col_t_act2, col_t_act3 = st.columns([1, 1, 4])
            with col_t_act1:
                st.button("✅ Complete", key=f"comp_task_{task['id']}", disabled=task['completed'], on_click=lambda t_id=task['id']: handle_task_completion(t_id))
            with col_t_act2:
                st.button("🗑️ Delete", key=f"del_task_{task['id']}", on_click=lambda t_id=task['id']: handle_task_delete(t_id))
            
            st.markdown("</div>", unsafe_allow_html=True) # Close the container styling div
            st.markdown("") # Add a small spacer

def render_shadow_work_tab():
    st.header("Shadow Work and Inner Mastery")
    st.markdown("---")

    st.subheader("Shadows for Integration")
    st.info("Address these shadows by implementing protocols, boundaries, and habits to minimize their influence on your operational flow.")

    for shadow in st.session_state.shadows:
        is_tamed = shadow['tamed']
        
        # Use a single column for the primary layout
        col_s1, col_s2, col_s3 = st.columns([1, 4, 1.5])
        
        with col_s1:
            st.markdown(f"**{'✅' if is_tamed else '🕳️'}**", unsafe_allow_html=True)
            
        with col_s2:
            st.markdown(
                f"""
                <div class="shadow-work-card" style="background-color: {'#E0F7FA' if is_tamed else '#FFFBEB'}; 
                                                    border-left: 5px solid {'#00BCD4' if is_tamed else '#F59E0B'};">
                    <p style='font-size: 1.1rem; font-weight: 600; color: #111827; margin: 0;'>
                        {shadow['name']}
                    </p>
                    <p style='font-size: 0.85rem; color: #4B5563; margin: 5px 0 0 0;'>
                        {shadow['description']}
                    </p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
        with col_s3:
            button_label = "✅ Untame" if is_tamed else "🎯 Tame Shadow"
            if st.button(button_label, key=f"tame_shadow_{shadow['id']}", on_click=lambda s_id=shadow['id']: handle_shadow_tame(s_id)):
                st.rerun()
                
    st.markdown("---")

def render_chat_tab(coach_name, history_key, initial_message_content):
    st.header(f"{coach_name} Protocol Interface")
    st.info(f"Interacting with {coach_name} via secure, asynchronous protocols. Your chat history is cloud-persistent.")
    st.markdown("---")

    # Display Chat History
    history = st.session_state.get(history_key, [{"role": "ai", "content": initial_message_content}])

    for message in history:
        if message["role"] == "ai":
            st.markdown(f"<div class='chat-message-ai'>**{coach_name}:** {message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-message-user'>**Sovereign:** {message['content']}</div>", unsafe_allow_html=True)

    # Chat Input
    prompt = st.chat_input("Input command or question...")
    
    if prompt:
        chat_response(coach_name, prompt, history_key, history)
        st.rerun()

def chat_response(coach_name, prompt, history_key, history):
    """Handles the user prompt and gets a response from the mock AI."""
    
    # 1. Add User Message
    history.append({"role": "user", "content": prompt})

    # 2. Mock AI Call (Replace with real API call later)
    with st.spinner(f"Awaiting response from {coach_name}..."):
        
        # This is a mock API call using the 'requests' library
        try:
            # Mock request payload for demonstration
            mock_payload = {
                "coach": coach_name,
                "prompt": prompt,
                "history": history
            }
            # Mock API response data
            mock_response_data = {
                "response": f"Affirmative. I have processed your input for {coach_name}. A detailed analysis is being generated.",
                "status": "success"
            }
            
            # Simulate network latency
            import time
            time.sleep(1) 
            
            ai_response = mock_response_data["response"]
            
        except Exception as e:
            ai_response = f"Protocol Failure: Connection to {coach_name} endpoint failed. Error: {e}"

    # 3. Add AI Response
    history.append({"role": "ai", "content": ai_response})

    # 4. Save updated history to session state and Firestore
    st.session_state[history_key] = history
    save_all_data()


# --- Main Application Setup ---

def main():
    # Load custom CSS
    try:
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("Error: style.css not found. Ensure it is in the same directory as the main script.")
        
    st.set_page_config(layout="wide")

    # Initialize all session states and connect to Firestore
    initialize_session_state()

    # --- Sidebar (Navigation) ---
    with st.sidebar:
        st.title("V3 Sovereign OS")
        
        # Display User ID (Moved to flow naturally after the title)
        st.markdown(
            f"""
            <div class="user-id-display">
                User ID:
                <span>{st.session_state.user_id}</span>
            </div>
            """, 
            unsafe_allow_html=True
        )

        # Navigation Tabs
        selected_tab = st.radio(
            "Operational Focus",
            ('Dashboard', 'Pillars', 'Tasks', 'Shadow Work', 'V3 Advisor', 'Super AI', 'BoL Academy'),
            index=['Dashboard', 'Pillars', 'Tasks', 'Shadow Work', 'V3 Advisor', 'Super AI', 'BoL Academy'].index(st.session_state.selected_tab)
        )
        st.session_state.selected_tab = selected_tab

    # --- Main Content Rendering ---
    
    if st.session_state.selected_tab == 'Dashboard':
        render_dashboard_tab()
    elif st.session_state.selected_tab == 'Pillars':
        render_pillars_tab()
    elif st.session_state.selected_tab == 'Tasks':
        render_tasks_tab()
    elif st.session_state.selected_tab == 'Shadow Work':
        render_shadow_work_tab()
    elif st.session_state.selected_tab == 'V3 Advisor':
        render_chat_tab("V3 Advisor", 'v3_advisor_history', initial_v3_advisor_message['content'])
    elif st.session_state.selected_tab == 'Super AI':
        render_chat_tab("Super AI", 'super_ai_history', initial_super_ai_message['content'])
    elif st.session_state.selected_tab == 'BoL Academy':
        render_chat_tab("BoL Academy", 'bol_academy_history', initial_bol_academy_message['content'])

if __name__ == '__main__':
    main()
