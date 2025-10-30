# v3_command_center.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import date, datetime, timedelta
import json
import time
import os

st.set_page_config(page_title="V3 Command Center", layout="wide")

# Data files - PRESERVING ALL YOUR EXISTING DATA
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

DAILY_LOG_CSV = os.path.join(DATA_DIR, "daily_log.csv")
BUSINESS_CSV = os.path.join(DATA_DIR, "business.csv") 
SHADOWS_JSON = os.path.join(DATA_DIR, "shadows.json")
PILLARS_JSON = os.path.join(DATA_DIR, "pillars.json")
DRILLS_CSV = os.path.join(DATA_DIR, "drills.csv")

# Initialize ALL your existing data
if not os.path.exists(DAILY_LOG_CSV):
    pd.DataFrame(columns=["Date", "Focus_Score", "Energy_Score", "Business_Progress", "Notes"]).to_csv(DAILY_LOG_CSV, index=False)
if not os.path.exists(BUSINESS_CSV):
    pd.DataFrame({"Date": [date.today().isoformat()], "Revenue": [8450], "Clients": [6], "Pipeline": [24000]}).to_csv(BUSINESS_CSV, index=False)
if not os.path.exists(SHADOWS_JSON):
    json.dump({"1.1": {"name": "Wounded Perfectionist", "progress": 0}, "7.1": {"name": "Imposter Syndrome", "progress": 0}}, open(SHADOWS_JSON, 'w'))

# Initialize enhanced pillar data
default_pillars = {
    "P1": {
        "name": "Shadow & Emotional Mastery", 
        "metrics": {"emotional_sovereignty": 0, "explanations_to_actions": 0, "shadow_progress": 0},
        "drills": ["Neural Override", "3-Second Pause", "Shadow Journaling"],
        "color": "#FF6B6B"
    },
    "P2": {
        "name": "Self-Mastery & Somatic", 
        "metrics": {"action_latency": 0, "energy_management": 0, "drill_completion": 0},
        "drills": ["Action Latency", "Somatic Drills", "Energy Management"],
        "color": "#4ECDC4"
    },
    "P3": {
        "name": "Erotic Intelligence", 
        "metrics": {"relational_dynamics": 0, "polarity_mastery": 0, "intimacy_capacity": 0},
        "drills": ["Polarity Drills", "Relational Experiments", "Boundary Setting"],
        "color": "#45B7D1"
    },
    "P4": {
        "name": "Spiritual Practices", 
        "metrics": {"ritual_adherence": 0, "meditation_consistency": 0, "alpha_state": 0},
        "drills": ["Morning Ritual", "Evening Alignment", "Meditation Timer"],
        "color": "#96CEB4"
    },
    "P5": {
        "name": "Strategy & Leadership", 
        "metrics": {"strategic_clarity": 0, "execution_velocity": 0, "decision_quality": 0},
        "drills": ["Pre-Mortem", "Scenario Planning", "Decision Drills"],
        "color": "#FFEAA7"
    },
    "P6": {
        "name": "Financial & Business", 
        "metrics": {"revenue_growth": 0, "pipeline_health": 0, "cash_flow": 0},
        "drills": ["Pipeline Conversion", "Financial Scenarios", "Abundance Mindset"],
        "color": "#DDA0DD"
    }
}

if not os.path.exists(PILLARS_JSON):
    json.dump(default_pillars, open(PILLARS_JSON, 'w'), indent=2)

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] { background: #0A0F1C; color: #E8E8E8; }
h1, h2, h3 { font-family: 'Orbitron', monospace; color: #00D4AA; }
.kpi { background: rgba(0,212,170,0.1); padding: 16px; border-radius: 8px; border-left: 4px solid #00D4AA; margin: 8px; }
.card { background: rgba(255,255,255,0.02); padding: 20px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); margin: 12px 0; }
.metric { font-family: 'Orbitron', monospace; color: #00D4AA; font-size: 24px; }
.pillar-card { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; border-left: 4px solid; margin: 8px 0; }
.drill-active { background: rgba(0,212,170,0.2); border: 2px solid #00D4AA; }
.business-kpi { background: rgba(221,160,221,0.15); padding: 12px; border-radius: 6px; margin: 4px; }
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown("<h1 style='text-align: center;'>V3 COMMAND CENTER</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #9CA3AF;'>6-PILLAR MASTERY + BUSINESS + 90-DAY + SHADOWS</div>", unsafe_allow_html=True)

# Load ALL your data
pillars = json.load(open(PILLARS_JSON))
biz_df = pd.read_csv(BUSINESS_CSV)
shadows = json.load(open(SHADOWS_JSON))

# OVERALL KPI DASHBOARD - WITH YOUR EXISTING BUSINESS NUMBERS
st.markdown("## 📊 V3 MASTERY DASHBOARD")

# Calculate overall scores
overall_scores = {}
for pillar_id, pillar in pillars.items():
    avg_score = sum(pillar['metrics'].values()) / len(pillar['metrics']) if pillar['metrics'] else 0
    overall_scores[pillar_id] = avg_score

total_score = sum(overall_scores.values()) / len(overall_scores)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"<div class='kpi'><strong>OVERALL V3 SCORE</strong><div class='metric'>{total_score:.0f}%</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='kpi'><strong>REVENUE</strong><div class='metric'>${biz_df['Revenue'].iloc[-1]:,}</div></div>", unsafe_allow_html=True)
with col3:
    shadow_progress = sum([s['progress'] for s in shadows.values()]) // len(shadows)
    st.markdown(f"<div class='kpi'><strong>SHADOW PROGRESS</strong><div class='metric'>{shadow_progress}%</div></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='kpi'><strong>DAY STREAK</strong><div class='metric'>12</div></div>", unsafe_allow_html=True)

# 6-PILLAR MASTERY GRID
st.markdown("## 🛡️ 6-PILLAR MASTERY TRACKING")

cols = st.columns(3)
pillar_cols = [cols[i % 3] for i in range(6)]

for i, (pillar_id, pillar) in enumerate(pillars.items()):
    with pillar_cols[i]:
        score = overall_scores[pillar_id]
        st.markdown(f"<div class='pillar-card' style='border-left-color: {pillar['color']}'>", unsafe_allow_html=True)
        st.markdown(f"**{pillar_id} - {pillar['name']}**")
        st.progress(score/100)
        st.markdown(f"`{score:.0f}%`")
        
        # Quick metrics update
        with st.expander("Update Metrics"):
            for metric, value in pillar['metrics'].items():
                new_val = st.slider(metric.replace('_', ' ').title(), 0, 100, value, key=f"{pillar_id}_{metric}")
                pillars[pillar_id]['metrics'][metric] = new_val
        
        # Drill launcher
        if st.button(f"🚀 Run {pillar['drills'][0]}", key=f"drill_{pillar_id}"):
            st.session_state[f'active_drill_{pillar_id}'] = True
        
        st.markdown("</div>", unsafe_allow_html=True)

# Save updated metrics
if st.button("💾 Save All Pillar Updates"):
    json.dump(pillars, open(PILLARS_JSON, 'w'), indent=2)
    st.success("Pillar metrics updated!")

# DRILL SIMULATIONS
st.markdown("## 🎯 ACTIVE DRILL SIMULATIONS")

# P1: Neural Override Drill
if st.session_state.get('active_drill_P1'):
    st.markdown("<div class='card drill-active'>", unsafe_allow_html=True)
    st.markdown("### 🧠 P1: Neural Override Drill")
    st.info("When triggered emotionally: PAUSE (3s) → OBSERVE → CHOOSE response")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start 3-Second Timer"):
            with st.empty():
                for i in range(3, 0, -1):
                    st.markdown(f"# {i}")
                    time.sleep(1)
                st.markdown("# 🎉 RESPONSE TIME!")
    
    with col2:
        trigger = st.text_input("Current Emotional Trigger:")
        response = st.selectbox("Choose Response:", ["Defend/Explain", "Observe/Curious", "Pause/Redirect"])
        if st.button("Log Override"):
            st.success(f"Override logged: {trigger} → {response}")
    st.markdown("</div>", unsafe_allow_html=True)

# P2: Action Latency Drill  
if st.session_state.get('active_drill_P2'):
    st.markdown("<div class='card drill-active'>", unsafe_allow_html=True)
    st.markdown("### ⚡ P2: Action Latency Drill")
    tasks = ["Do 10 pushups NOW", "Send that email you're avoiding", "Clean one surface immediately"]
    task = np.random.choice(tasks)
    st.warning(f"**Random Task:** {task}")
    
    if st.button("Start Execution Timer"):
        start_time = time.time()
        st.info("Timer running... complete the task!")
        if st.button("Task Completed"):
            end_time = time.time()
            latency = end_time - start_time
            st.success(f"Action Latency: {latency:.1f}s - {'Elite' if latency < 3 else 'Good' if latency < 10 else 'Needs Work'}")
    st.markdown("</div>", unsafe_allow_html=True)
# P6: BUSINESS DRILL - FIXED
if st.session_state.get('active_drill_P6'):
    st.markdown("<div class='card drill-active'>", unsafe_allow_html=True)
    st.markdown("### 💰 P6: Business Conversion Drill")
    
    st.markdown(f"**Current Business:** ${revenue:,} revenue | {clients} clients | ${pipeline:,} pipeline | {close_rate*100:.0f}% close rate")
    
    scenario = st.selectbox("Business Scenario:", 
                           ["Client wants 20% discount for annual contract",
                            "Competitor launches similar service at 40% price",
                            "Your top client threatens to leave"])
    
    if st.button("Generate Strategic Response"):
        responses = {
            "Client wants 20% discount for annual contract": "**Strategy:** Offer 15% for 2-year commitment + add-on services. Protect value positioning.",
            "Competitor launches similar service at 40% price": "**Strategy:** Double down on premium differentiation - focus on results, not price.",
            "Your top client threatens to leave": "**Strategy:** Schedule emergency value review call. Show ROI and create recovery plan."
        }
        st.info(responses[scenario])
    
    if st.button("Update Business Numbers"):
        with st.form("update_business_p6"):
            new_rev = st.number_input("Revenue", value=biz_df['Revenue'].iloc[-1])
            new_clients = st.number_input("Clients", value=biz_df['Clients'].iloc[-1])
            new_pipeline = st.number_input("Pipeline", value=biz_df['Pipeline'].iloc[-1])
            if st.form_submit_button("Save Business Update"):
                new_row = {"Date": date.today().isoformat(), "Revenue": new_rev, "Clients": new_clients, "Pipeline": new_pipeline}
                pd.concat([biz_df, pd.DataFrame([new_row])], ignore_index=True).to_csv(BUSINESS_CSV, index=False)
                st.success("Business updated!")
    st.markdown("</div>", unsafe_allow_html=True)
# ENHANCED BUSINESS SECTION WITH OUTREACH TRACKING
st.markdown("## 💼 BUSINESS & OUTREACH DASHBOARD")

# Read business data with correct column names
try:
    biz_df = pd.read_csv(BUSINESS_CSV)
    last_row = biz_df.iloc[-1]
    
    revenue = last_row['Revenue']
    clients = last_row['Active_Clients']
    pipeline = last_row['Pipeline_Value']
    close_rate = last_row.get('Close_Rate', 0)

    biz_col1, biz_col2, biz_col3, biz_col4 = st.columns(4)
    with biz_col1:
        st.markdown(f"<div class='business-kpi'><strong>REVENUE</strong><br><div class='metric'>${revenue:,}</div></div>", unsafe_allow_html=True)
    with biz_col2:
        st.markdown(f"<div class='business-kpi'><strong>CLIENTS</strong><br><div class='metric'>{clients}</div></div>", unsafe_allow_html=True)
    with biz_col3:
        st.markdown(f"<div class='business-kpi'><strong>PIPELINE</strong><br><div class='metric'>${pipeline:,}</div></div>", unsafe_allow_html=True)
    with biz_col4:
        st.markdown(f"<div class='business-kpi'><strong>CLOSE RATE</strong><br><div class='metric'>{close_rate*100:.0f}%</div></div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Business data error: {e}")

# DAILY OUTREACH TRACKER - NEW FEATURE
st.markdown("### 📈 DAILY OUTREACH TRACKER")

# Initialize outreach data
OUTREACH_CSV = os.path.join(DATA_DIR, "outreach.csv")
if not os.path.exists(OUTREACH_CSV):
    pd.DataFrame(columns=["Date", "Calls", "Emails", "LinkedIn", "Meetings", "Follow_Ups", "Notes"]).to_csv(OUTREACH_CSV, index=False)

# Today's outreach form
with st.form("daily_outreach"):
    st.markdown("**Today's Outreach Numbers:**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        calls = st.number_input("Calls Made", 0, 100, 0)
    with col2:
        emails = st.number_input("Emails Sent", 0, 100, 0)
    with col3:
        linkedin = st.number_input("LinkedIn DMs", 0, 100, 0)
    with col4:
        meetings = st.number_input("Meetings Booked", 0, 20, 0)
    
    follow_ups = st.number_input("Follow-ups Scheduled", 0, 50, 0)
    outreach_notes = st.text_area("Outreach Insights")
    
    if st.form_submit_button("💌 LOG TODAY'S OUTREACH"):
        outreach_df = pd.read_csv(OUTREACH_CSV)
        new_outreach = {
            "Date": date.today().isoformat(),
            "Calls": calls,
            "Emails": emails, 
            "LinkedIn": linkedin,
            "Meetings": meetings,
            "Follow_Ups": follow_ups,
            "Notes": outreach_notes
        }
        pd.concat([outreach_df, pd.DataFrame([new_outreach])], ignore_index=True).to_csv(OUTREACH_CSV, index=False)
        st.success("Outreach logged!")

# Outreach metrics and trends
try:
    outreach_df = pd.read_csv(OUTREACH_CSV)
    if len(outreach_df) > 0:
        st.markdown("#### 📊 Outreach Performance")
        
        # Weekly metrics
        recent_outreach = outreach_df.tail(7)  # Last 7 days
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_daily_contacts = recent_outreach[['Calls', 'Emails', 'LinkedIn']].sum(axis=1).mean()
            st.metric("Avg Daily Contacts", f"{avg_daily_contacts:.0f}")
        with col2:
            meeting_rate = (recent_outreach['Meetings'].sum() / recent_outreach[['Calls', 'Emails', 'LinkedIn']].sum().sum() * 100) if recent_outreach[['Calls', 'Emails', 'LinkedIn']].sum().sum() > 0 else 0
            st.metric("Meeting Rate", f"{meeting_rate:.1f}%")
        with col3:
            total_follow_ups = recent_outreach['Follow_Ups'].sum()
            st.metric("Active Follow-ups", total_follow_ups)
        with col4:
            streak = len(outreach_df[outreach_df[['Calls', 'Emails', 'LinkedIn']].sum(axis=1) > 0])
            st.metric("Outreach Streak", f"{streak} days")
        
        # Outreach trend chart
        if len(outreach_df) > 1:
            outreach_df['Date'] = pd.to_datetime(outreach_df['Date'])
            outreach_df['Total_Contacts'] = outreach_df['Calls'] + outreach_df['Emails'] + outreach_df['LinkedIn']
            
            fig = px.line(outreach_df, x='Date', y='Total_Contacts', 
                         title="Daily Outreach Trend", markers=True)
            st.plotly_chart(fig, use_container_width=True)
            
except Exception as e:
    st.info("Log outreach data to see performance metrics")

# Business update form
with st.expander("📈 Update Business Metrics"):
    with st.form("business_update"):
        new_rev = st.number_input("Monthly Revenue", value=revenue)
        new_clients = st.number_input("Active Clients", value=clients)
        new_pipeline = st.number_input("Pipeline Value", value=pipeline)
        new_close_rate = st.number_input("Close Rate %", value=close_rate*100, min_value=0.0, max_value=100.0, step=1.0) / 100
        if st.form_submit_button("💾 Save Business Update"):
            new_row = {
                "Date": date.today().isoformat(), 
                "Revenue": new_rev, 
                "Active_Clients": new_clients, 
                "Pipeline_Value": new_pipeline,
                "Close_Rate": new_close_rate
            }
            pd.concat([biz_df, pd.DataFrame([new_row])], ignore_index=True).to_csv(BUSINESS_CSV, index=False)
            st.success("Business metrics updated!")

# SHADOW WORK SECTION - Your original shadow tracking
st.markdown("## 🕵️ SHADOW WORK")

shadow_col1, shadow_col2 = st.columns(2)
with shadow_col1:
    for shadow_id, shadow in shadows.items():
        st.markdown(f"**{shadow_id} - {shadow['name']}**")
        st.progress(shadow['progress'] / 100)
        st.write(f"Progress: {shadow['progress']}%")

with shadow_col2:
    with st.form("update_shadows"):
        st.markdown("### Update Shadow Progress")
        for shadow_id, shadow in shadows.items():
            new_progress = st.slider(f"{shadow['name']}", 0, 100, shadow['progress'], key=f"shadow_{shadow_id}")
            shadows[shadow_id]['progress'] = new_progress
        if st.form_submit_button("Update Shadow Progress"):
            json.dump(shadows, open(SHADOWS_JSON, 'w'))
            st.success("Shadow progress updated!")

# 90-DAY ROADMAP - Your original V3 plan
st.markdown("## 🗺️ 90-DAY V3 ROADMAP")

phases = [
    {"name": "🛡️ Days 1-30: Foundation & Nervous System", "progress": 100},
    {"name": "💰 Days 31-60: Business Integration", "progress": 45}, 
    {"name": "👑 Days 61-90: Sovereignty Mastery", "progress": 0}
]

for phase in phases:
    st.write(f"**{phase['name']}**")
    st.progress(phase['progress'] / 100)

# DAILY LOGGING - Your original daily tracking
st.markdown("## 📝 DAILY COMMAND LOG")

with st.form("daily_log"):
    col1, col2, col3 = st.columns(3)
    with col1:
        focus = st.slider("Strategic Focus", 0, 10, 8)
    with col2:
        energy = st.slider("Energy Management", 0, 10, 7)
    with col3:
        business_progress = st.slider("Business Progress", 0, 10, 6)
    
    notes = st.text_area("Today's Insights & Wins")
    
    if st.form_submit_button("💎 LOG TODAY'S COMMAND"):
        df = pd.read_csv(DAILY_LOG_CSV)
        new_row = {
            "Date": date.today().isoformat(), 
            "Focus_Score": focus, 
            "Energy_Score": energy, 
            "Business_Progress": business_progress, 
            "Notes": notes
        }
        pd.concat([df, pd.DataFrame([new_row])], ignore_index=True).to_csv(DAILY_LOG_CSV, index=False)
        st.success("Daily command logged!")

# PROGRESS VISUALIZATION
try:
    df_log = pd.read_csv(DAILY_LOG_CSV)
    if len(df_log) > 1:
        st.markdown("## 📈 PROGRESS TRACKING")
        fig = px.line(df_log, x='Date', y=['Focus_Score', 'Energy_Score', 'Business_Progress'], 
                     title="Daily V3 Metrics", markers=True)
        st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.info("Log more days to see progress charts!")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #6B7280;'>V3 COMMAND CENTER • Everything Preserved & Enhanced</div>", unsafe_allow_html=True)