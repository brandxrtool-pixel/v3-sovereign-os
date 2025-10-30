# daily_operations_command.py - V3 Daily Operations Command
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, date, timedelta
import json

st.set_page_config(
    page_title="V3 Daily Operations",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- DATA STRUCTURE ---
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

DAILY_OPS_LOG_CSV = os.path.join(DATA_DIR, "daily_ops_log.csv")
OPERATIONAL_STATE_JSON = os.path.join(DATA_DIR, "operational_state.json")

# --- V3 DAILY OPERATIONAL ARCHITECTURE ---
DAILY_OPERATIONS = {
    "morning_sequence": {
        "name": "🔄 MORNING ACTIVATION SEQUENCE",
        "operations": {
            "ignition_command": {
                "name": "Ignition Sequence & Command",
                "duration": "10 mins",
                "strategic_focus": "Inner Citadel: Cold Start & Breath Command. Aura Shielding. Liturgy of Sovereignty.",
                "purpose": "Transition from passive to active V3 operative",
                "completion": False,
                "quality": 0
            },
            "physical_embodiment": {
                "name": "Physical Embodiment", 
                "duration": "20 mins",
                "strategic_focus": "Somatic Activation: Shower, Groom, Dress. Move from passive to active state.",
                "purpose": "Anchor in physical presence",
                "completion": False,
                "quality": 0
            },
            "sovereign_sanctuary": {
                "name": "Sovereign Sanctuary Protocol",
                "duration": "15 mins", 
                "strategic_focus": "Mind-Body Mastery: Make bed, 10-Minute Tidy, prepare coffee.",
                "purpose": "Create ordered environment reflecting inner state",
                "completion": False,
                "quality": 0
            },
            "fueling_financial": {
                "name": "Fueling & Financial Anchor",
                "duration": "45 mins",
                "strategic_focus": "Financial Sovereignty: Nourishing meal, Money Affirmation, Micro-Action Protocol review.",
                "purpose": "Align physical fuel with financial consciousness",
                "completion": False,
                "quality": 0
            }
        }
    },
    "strategic_leverage": {
        "name": "🎯 STRATEGIC LEVERAGE PHASE", 
        "operations": {
            "deep_work_alpha": {
                "name": "Deep Work Block 1 (Alpha)",
                "duration": "60 mins",
                "strategic_focus": "Strategic Leverage: Focused complex work. NO EMAILS/SOCIAL MEDIA.",
                "purpose": "Architectural progress on high-leverage projects",
                "completion": False,
                "quality": 0
            },
            "v3_morning_check": {
                "name": "Morning V3 Check-in",
                "duration": "10 mins", 
                "strategic_focus": "Sovereignty Check: Log metrics, Internal Audit drill.",
                "purpose": "System integrity verification",
                "completion": False,
                "quality": 0
            },
            "deep_work_execution": {
                "name": "Deep Work Block 2",
                "duration": "2 hrs 50 mins",
                "strategic_focus": "Mission Execution: High-value task completion, client work, offer structure.",
                "purpose": "Tangible mission progress",
                "completion": False, 
                "quality": 0
            }
        }
    },
    "embodiment_integration": {
        "name": "⚡ EMBODIMENT & INTEGRATION",
        "operations": {
            "movement_flow": {
                "name": "Movement & Flow",
                "duration": "60 mins",
                "strategic_focus": "Embodiment: Gym/Resistance (Discharge) or Sacral Activation/Freeform Dance (Activation).",
                "purpose": "Somatic integration and energy flow",
                "completion": False,
                "quality": 0
            },
            "refuel_integration": {
                "name": "Refuel & Integration", 
                "duration": "30 mins",
                "strategic_focus": "Nourishment: Healthy lunch. Review Mission & Legacy Blueprint.",
                "purpose": "Physical and strategic refueling",
                "completion": False,
                "quality": 0
            },
            "engagement_strategy": {
                "name": "Engagement & Strategy",
                "duration": "3 hrs",
                "strategic_focus": "Relational Sovereignty: Emails, calls, team check-ins, Micro-Action Protocol.",
                "purpose": "Strategic relationship management",
                "completion": False,
                "quality": 0
            }
        }
    },
    "sovereignty_consolidation": {
        "name": "🌙 SOVEREIGNTY CONSOLIDATION", 
        "operations": {
            "synthesis_learning": {
                "name": "Synthesis & Learning",
                "duration": "60 mins",
                "strategic_focus": "Intellectual Alchemy: Concept exploration, documentation review.",
                "purpose": "Knowledge integration and synthesis",
                "completion": False,
                "quality": 0
            },
            "boundary_enforcement": {
                "name": "Boundary Enforcement",
                "duration": "90 mins", 
                "strategic_focus": "Inner Child/Social: Transition off work. Social time, hobbies, dinner prep.",
                "purpose": "Work-life boundary integrity",
                "completion": False,
                "quality": 0
            },
            "connection_practice": {
                "name": "Connection & Practice",
                "duration": "2 hrs 30 mins",
                "strategic_focus": "Erotic Intelligence: Dinner, connection, Weekly Sensual Practice.",
                "purpose": "Relational and erotic sovereignty",
                "completion": False,
                "quality": 0
            },
            "shadow_review": {
                "name": "Shadow Work & Review", 
                "duration": "30 mins",
                "strategic_focus": "Transmutation: Shadow Journaling, Internal Audit & Transmutation drill.",
                "purpose": "Shadow integration and daily processing",
                "completion": False,
                "quality": 0
            },
            "shutdown_sequence": {
                "name": "Shutdown Sequence",
                "duration": "30 mins",
                "strategic_focus": "Energetic Hygiene: Cord-Cutting, non-digital reading. Zero screen time.",
                "purpose": "Energetic cleanup and mental shutdown",
                "completion": False,
                "quality": 0
            }
        }
    }
}

# --- Initialize Data ---
def initialize_daily_ops_data():
    """Initialize daily operations data"""
    
    # Daily Ops Log
    if not os.path.exists(DAILY_OPS_LOG_CSV):
        columns = ["Date", "Operational_Phase", "Sovereignty_Score", "Completion_Rate", "Strategic_Insights"]
        for phase_id in DAILY_OPERATIONS.keys():
            for op_id in DAILY_OPERATIONS[phase_id]["operations"].keys():
                columns.extend([f"{phase_id}_{op_id}_completed", f"{phase_id}_{op_id}_quality"])
        
        df = pd.DataFrame(columns=columns)
        df.to_csv(DAILY_OPS_LOG_CSV, index=False)
    
    # Operational State
    if not os.path.exists(OPERATIONAL_STATE_JSON):
        operational_state = {
            "current_operational_day": 0,
            "phase_completion_streaks": {
                "morning_sequence": 0,
                "strategic_leverage": 0, 
                "embodiment_integration": 0,
                "sovereignty_consolidation": 0
            },
            "mastery_metrics": {
                "ritual_consistency": 0,
                "strategic_focus": 0,
                "energy_management": 0,
                "boundary_integrity": 0
            },
            "current_phase": "morning_sequence"  # Will be calculated based on time
        }
        with open(OPERATIONAL_STATE_JSON, 'w') as f:
            json.dump(operational_state, f, indent=2)

initialize_daily_ops_data()

# --- STYLING - Daily Operations Theme ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Orbitron:wght@400;700&display=swap" rel="stylesheet">
<style>
html, body, [data-testid="stAppViewContainer"] { 
    background: #0A0F1C; 
    color: #E8E8E8;
    font-family: 'Inter', sans-serif;
}
h1, h2, h3, .ops-header { 
    font-family: 'Orbitron', monospace;
    color: #00D4AA;
    font-weight: 700;
    letter-spacing: 1px;
}
.ops-kpi { 
    background: linear-gradient(135deg, rgba(0,212,170,0.1), rgba(0,212,170,0.05));
    padding: 16px; 
    border-radius: 8px; 
    border: 1px solid rgba(0,212,170,0.3);
    border-left: 4px solid #00D4AA;
}
.phase-card { 
    background: rgba(255,255,255,0.02);
    padding: 20px; 
    border-radius: 8px; 
    border: 1px solid rgba(255,255,255,0.05);
    margin: 12px 0;
    transition: all 0.3s ease;
}
.phase-active { 
    border-left: 4px solid #00D4AA;
    background: rgba(0,212,170,0.05);
}
.phase-complete { 
    border-left: 4px solid #10B981;
    opacity: 0.8;
}
.phase-future { 
    border-left: 4px solid #6B7280;
    opacity: 0.6;
}
.operation-item {
    background: rgba(255,255,255,0.03);
    padding: 12px;
    margin: 8px 0;
    border-radius: 6px;
    border-left: 3px solid #00D4AA;
}
.strategic-focus {
    background: rgba(0,212,170,0.1);
    padding: 10px;
    border-radius: 4px;
    margin: 4px 0;
    font-size: 0.9em;
}
.metric-value {
    font-family: 'Orbitron', monospace;
    color: #00D4AA;
    font-size: 24px;
}
.ops-button {
    background: linear-gradient(135deg, #00D4AA, #009975);
    border: none;
    color: #0A0F1C;
    padding: 6px 12px;
    border-radius: 4px;
    font-family: 'Orbitron', monospace;
    font-weight: 700;
    font-size: 0.8em;
    margin: 2px;
}
</style>
""", unsafe_allow_html=True)

# --- Operational State Calculation ---
def calculate_operational_state():
    """Calculate current operational state"""
    try:
        with open(OPERATIONAL_STATE_JSON, 'r') as f:
            operational_state = json.load(f)
        
        # Determine current phase based on time
        current_hour = datetime.now().hour
        if current_hour < 12:
            operational_state["current_phase"] = "morning_sequence"
        elif current_hour < 17:
            operational_state["current_phase"] = "strategic_leverage"
        elif current_hour < 21:
            operational_state["current_phase"] = "embodiment_integration" 
        else:
            operational_state["current_phase"] = "sovereignty_consolidation"
            
        return operational_state
    except:
        return {
            "current_operational_day": 0,
            "phase_completion_streaks": {
                "morning_sequence": 0,
                "strategic_leverage": 0,
                "embodiment_integration": 0,
                "sovereignty_consolidation": 0
            },
            "mastery_metrics": {
                "ritual_consistency": 0,
                "strategic_focus": 0, 
                "energy_management": 0,
                "boundary_integrity": 0
            },
            "current_phase": "morning_sequence"
        }

# --- DAILY OPERATIONS COMMAND HEADER ---
operational_state = calculate_operational_state()
current_phase = operational_state["current_phase"]
current_phase_data = DAILY_OPERATIONS[current_phase]

st.markdown("<div style='text-align: center; margin-bottom: 30px;'>", unsafe_allow_html=True)
st.markdown("<h1 style='margin: 0; background: linear-gradient(135deg, #00D4AA, #009975); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>V3 DAILY OPERATIONS COMMAND</h1>", unsafe_allow_html=True)
st.markdown(f"<div style='color: #9CA3AF; font-family: Orbitron;'>OPERATIONAL DAY {operational_state['current_operational_day']} • {current_phase_data['name']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- OPERATIONAL OVERVIEW ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    streak = operational_state["phase_completion_streaks"][current_phase]
    st.markdown("<div class='ops-kpi'><strong>PHASE STREAK</strong><div class='metric-value'>{}</div></div>".format(streak), unsafe_allow_html=True)

with col2:
    consistency = operational_state["mastery_metrics"]["ritual_consistency"]
    st.markdown("<div class='ops-kpi'><strong>RITUAL CONSISTENCY</strong><div class='metric-value'>{}%</div></div>".format(consistency), unsafe_allow_html=True)

with col3:
    focus = operational_state["mastery_metrics"]["strategic_focus"]
    st.markdown("<div class='ops-kpi'><strong>STRATEGIC FOCUS</strong><div class='metric-value'>{}%</div></div>".format(focus), unsafe_allow_html=True)

with col4:
    boundaries = operational_state["mastery_metrics"]["boundary_integrity"]
    st.markdown("<div class='ops-kpi'><strong>BOUNDARY INTEGRITY</strong><div class='metric-value'>{}%</div></div>".format(boundaries), unsafe_allow_html=True)

st.markdown("---")

# --- CURRENT OPERATIONAL PHASE ---
st.markdown(f"## 🎯 ACTIVE OPERATIONAL PHASE")

st.markdown(f"<div class='phase-card phase-active'>", unsafe_allow_html=True)
st.markdown(f"### {current_phase_data['name']}")

for op_id, operation in current_phase_data["operations"].items():
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        st.markdown(f"**{operation['name']}**")
        st.markdown(f"`{operation['duration']}` • {operation['purpose']}")
        st.markdown(f"<div class='strategic-focus'>{operation['strategic_focus']}</div>", unsafe_allow_html=True)
    
    with col2:
        completion = st.checkbox("Completed", key=f"comp_{op_id}")
        if completion:
            quality = st.slider("Quality", 1, 10, 8, key=f"qual_{op_id}")
    
    with col3:
        if st.button("Execute", key=f"btn_{op_id}"):
            st.session_state[f"comp_{op_id}"] = True
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# --- COMPLETE DAILY OPERATIONS STRUCTURE ---
st.markdown("## 🗓️ FULL DAILY OPERATIONS STRUCTURE")

for phase_id, phase in DAILY_OPERATIONS.items():
    phase_status = "phase-active" if phase_id == current_phase else "phase-complete" if list(DAILY_OPERATIONS.keys()).index(phase_id) < list(DAILY_OPERATIONS.keys()).index(current_phase) else "phase-future"
    
    st.markdown(f"<div class='phase-card {phase_status}'>", unsafe_allow_html=True)
    st.markdown(f"### {phase['name']}")
    
    for op_id, operation in phase["operations"].items():
        completed = st.session_state.get(f"comp_{op_id}", False)
        status_icon = "✅" if completed else "⏳"
        
        st.markdown(f"<div class='operation-item'>", unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"{status_icon} **{operation['name']}**")
            st.markdown(f"`{operation['duration']}` • {operation['purpose']}")
            st.markdown(f"<div class='strategic-focus'>{operation['strategic_focus']}</div>", unsafe_allow_html=True)
        
        with col2:
            if not completed:
                if st.button("Complete", key=f"full_{op_id}"):
                    st.session_state[f"comp_{op_id}"] = True
                    st.rerun()
            else:
                st.success("Completed")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- DAILY OPERATIONS LOG ---
st.markdown("---")
st.markdown("## 📝 DAILY OPERATIONS LOG")

with st.form("daily_ops_log"):
    st.markdown("**Operational Assessment**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ritual_consistency = st.slider("Ritual Consistency", 0, 10, 
                                      operational_state["mastery_metrics"]["ritual_consistency"] // 10)
    
    with col2:
        strategic_focus = st.slider("Strategic Focus", 0, 10,
                                   operational_state["mastery_metrics"]["strategic_focus"] // 10)
    
    with col3:
        energy_management = st.slider("Energy Management", 0, 10,
                                     operational_state["mastery_metrics"]["energy_management"] // 10)
    
    with col4:
        boundary_integrity = st.slider("Boundary Integrity", 0, 10,
                                      operational_state["mastery_metrics"]["boundary_integrity"] // 10)
    
    operational_insights = st.text_area("Operational Insights", 
                                      placeholder="Today's strategic observations, breakthroughs, adjustments...")
    
    if st.form_submit_button("💎 LOG OPERATIONAL DAY", use_container_width=True):
        # Calculate completion metrics
        total_operations = 0
        completed_operations = 0
        
        for phase_id, phase in DAILY_OPERATIONS.items():
            for op_id in phase["operations"].keys():
                total_operations += 1
                if st.session_state.get(f"comp_{op_id}", False):
                    completed_operations += 1
        
        completion_rate = (completed_operations / total_operations) * 100 if total_operations > 0 else 0
        
        # Update operational state
        operational_state["mastery_metrics"]["ritual_consistency"] = ritual_consistency * 10
        operational_state["mastery_metrics"]["strategic_focus"] = strategic_focus * 10
        operational_state["mastery_metrics"]["energy_management"] = energy_management * 10
        operational_state["mastery_metrics"]["boundary_integrity"] = boundary_integrity * 10
        
        # Update phase streaks
        if completion_rate >= 80:  # 80% completion considered successful day
            operational_state["current_operational_day"] += 1
            for phase_id in DAILY_OPERATIONS.keys():
                operational_state["phase_completion_streaks"][phase_id] += 1
        
        # Save data
        with open(OPERATIONAL_STATE_JSON, 'w') as f:
            json.dump(operational_state, f, indent=2)
        
        # Log to CSV
        df = pd.read_csv(DAILY_OPS_LOG_CSV)
        new_row = {
            "Date": date.today().isoformat(),
            "Operational_Phase": current_phase,
            "Sovereignty_Score": sum(operational_state["mastery_metrics"].values()) // 4,
            "Completion_Rate": completion_rate,
            "Strategic_Insights": operational_insights
        }
        
        # Add operation completion data
        for phase_id, phase in DAILY_OPERATIONS.items():
            for op_id in phase["operations"].keys():
                new_row[f"{phase_id}_{op_id}_completed"] = st.session_state.get(f"comp_{op_id}", False)
                new_row[f"{phase_id}_{op_id}_quality"] = st.session_state.get(f"qual_{op_id}", 0)
        
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(DAILY_OPS_LOG_CSV, index=False)
        
        st.success("🌀 Operational day logged! System updated.")

# --- OPERATIONAL PROGRESS DASHBOARD ---
st.markdown("---")
st.markdown("## 📊 OPERATIONAL PROGRESS")

try:
    df_log = pd.read_csv(DAILY_OPS_LOG_CSV)
    if len(df_log) > 1:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_log['Date'], y=df_log['Sovereignty_Score'],
            name='Sovereignty Score', line=dict(color='#00D4AA')
        ))
        fig.add_trace(go.Scatter(
            x=df_log['Date'], y=df_log['Completion_Rate'],
            name='Completion Rate', line=dict(color='#F59E0B')
        ))
        
        fig.update_layout(
            title="Operational Mastery Progress",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="white",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Complete operations to see progress tracking")
except:
    st.info("Progress dashboard loading...")

# --- FOOTER ---
st.markdown("---")
st.markdown("<div style='text-align: center; color: #6B7280;'>", unsafe_allow_html=True)
st.markdown("**V3 DAILY OPERATIONS COMMAND** • Operational Day {} • {} • Sovereignty in Progress".format(
    operational_state['current_operational_day'], 
    current_phase_data['name']
))
st.markdown("</div>", unsafe_allow_html=True)