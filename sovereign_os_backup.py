# sovereign_os.py - V3 Sovereign OS + Business Command Center
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, date, timedelta
import json

st.set_page_config(
    page_title="V3 Sovereign OS",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- DATA STRUCTURE ---
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

SHADOW_DOSSIERS_JSON = os.path.join(DATA_DIR, "shadow_dossiers.json")
DAILY_METRICS_CSV = os.path.join(DATA_DIR, "daily_metrics.csv")
BUSINESS_CSV = os.path.join(DATA_DIR, "business.csv")

# --- V3 TRANSFORMATION SYSTEM ---
V3_SYSTEM = {
    "phase_1": {
        "title": "🛡️ Phase 1: Foundation & MVP Stabilization (Days 1-30)",
        "focus": "Halt energy bleed, regulate nervous system, establish V3 rituals",
        "domains": {
            "inner_citadel": {
                "name": "Inner Citadel",
                "protocols": ["Living Room Protocol", "Breath Command (4-8 count)"],
                "metrics": ["Armored Body Rating", "Breath Compliance"],
                "technical": "Build Streamlit MVP input widgets"
            },
            "primary_shadow": {
                "name": "Wounded Perfectionist (1.1)", 
                "protocols": ["Mirror Self-Compassion", "One Imperfect Act/week"],
                "metrics": ["Self-Judgment Frequency", "Imperfect Acts"],
                "technical": "Track imperfect act compliance"
            },
            "defense": {
                "name": "Energetic Defense",
                "protocols": ["Aura Shielding", "Cord-Cutting rituals"],
                "metrics": ["Shielding Compliance"],
                "technical": "Setup Shadow Dossier data structure"
            },
            "financial": {
                "name": "Financial Sub-Routine",
                "protocols": ["Money Affirmation Ritual", "One Invoice/week"],
                "metrics": ["Micro-Action Execution"],
                "technical": "Build money affirmation widget"
            }
        }
    },
    "phase_2": {
        "title": "💰 Phase 2: Integration & Analysis (Days 31-60)",
        "focus": "Deepen body-mind connection, prove inner causation",
        "domains": {
            "somatic": {
                "name": "Somatic Activation",
                "protocols": ["Deep Breathwork", "Somatic Shaking"],
                "metrics": ["Interoception Score", "Embodiment Compliance"],
                "technical": "Build weekly embodiment tracker"
            },
            "financial_integration": {
                "name": "Financial Integration", 
                "protocols": ["Pricing/Visibility Experiments"],
                "metrics": ["Pricing Changes Implemented"],
                "technical": "Shadow-to-Outcome mapping"
            },
            "relational": {
                "name": "Relational Shadow (1.2)",
                "protocols": ["Boundary Scripts", "Micro-Confrontations"],
                "metrics": ["Passive-Aggressive Episodes"],
                "technical": "Boundary script log"
            },
            "linguistic": {
                "name": "Linguistic Sensing",
                "protocols": ["AI Diagnostic Testing"],
                "metrics": ["Simulated Diagnosis Accuracy"],
                "technical": "Simulated AI diagnosis"
            }
        }
    },
    "phase_3": {
        "title": "👑 Phase 3: Mastery Emergence (Days 61-90)",
        "focus": "Finalize shadow integration, embody V3 sovereignty",
        "domains": {
            "living_mirror": {
                "name": "Full Living Mirror",
                "protocols": ["All V3.1 Dossiers"],
                "metrics": ["Diagnostic Accuracy"],
                "technical": "Gemini API integration"
            },
            "erotic": {
                "name": "Erotic Sovereignty",
                "protocols": ["Sacral Activation", "Sensual Practices"],
                "metrics": ["Creative Stagnation Score"],
                "technical": "Sensual practice tracker"
            },
            "leadership": {
                "name": "Leadership/Alpha",
                "protocols": ["Delegation Experiments"],
                "metrics": ["Micro-Actions Completed"],
                "technical": "Success ratio display"
            },
            "evolution": {
                "name": "Evolution Tracking",
                "protocols": ["Alchemy Stage Monitoring"],
                "metrics": ["Dissociation Frequency"],
                "technical": "Evolution graph visualization"
            }
        }
    }
}

# --- Initialize Data ---
def initialize_v3_data():
    """Initialize all V3 tracking data structures"""
    
    # Shadow Dossiers
    if not os.path.exists(SHADOW_DOSSIERS_JSON):
        shadow_data = {
            "1.1": {
                "name": "Wounded Perfectionist",
                "description": "Self-sabotage through impossible standards",
                "protocols": ["Mirror Self-Compassion", "Imperfect Acts"],
                "current_strength": 7,
                "integration_progress": 0
            },
            "1.2": {
                "name": "Hidden Victim/Martyr", 
                "description": "Passive aggression and boundary issues",
                "protocols": ["Boundary Scripts", "Micro-Confrontations"],
                "current_strength": 5,
                "integration_progress": 0
            },
            "7.1": {
                "name": "Imposter/Scarcity Self",
                "description": "Financial self-sabotage and undervaluing",
                "protocols": ["Pricing Experiments", "Money Affirmations"],
                "current_strength": 6,
                "integration_progress": 0
            },
            "7.2": {
                "name": "Control Tycoon",
                "description": "Inability to delegate and trust",
                "protocols": ["Delegation Experiments"],
                "current_strength": 8,
                "integration_progress": 0
            }
        }
        with open(SHADOW_DOSSIERS_JSON, 'w') as f:
            json.dump(shadow_data, f, indent=2)
    
    # Daily Metrics
    if not os.path.exists(DAILY_METRICS_CSV):
        df = pd.DataFrame(columns=[
            "Date", "Armored_Body_Rating", "Self_Judgment_Frequency", 
            "Shielding_Compliance", "Micro_Actions_Executed",
            "Interoception_Score", "Pricing_Changes", "Boundary_Success",
            "Creative_Stagnation", "Dissociation_Frequency", "V3_Alignment"
        ])
        df.to_csv(DAILY_METRICS_CSV, index=False)
    
    # Business Data
    if not os.path.exists(BUSINESS_CSV):
        biz_data = pd.DataFrame({
            "Date": [date.today().isoformat()],
            "Revenue": [8450],
            "Active_Clients": [6],
            "Pipeline_Value": [24000],
            "Close_Rate": [0.42]
        })
        biz_data.to_csv(BUSINESS_CSV, index=False)

initialize_v3_data()

# --- Progress Calculation ---
def calculate_v3_progress():
    """Calculate overall transformation progress"""
    try:
        df_daily = pd.read_csv(DAILY_METRICS_CSV)
        days_completed = min(len(df_daily), 90)
        
        # Calculate current phase
        if days_completed <= 30:
            current_phase = "phase_1"
        elif days_completed <= 60:
            current_phase = "phase_2" 
        else:
            current_phase = "phase_3"
            
        return {
            "days_completed": days_completed,
            "current_phase": current_phase,
            "completion_rate": (days_completed / 90) * 100
        }
    except:
        return {"days_completed": 0, "current_phase": "phase_1", "completion_rate": 0}

# --- STYLING ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
<style>
html, body, [data-testid="stAppViewContainer"] { 
    background: #0A0A0A; 
    color: #E8E8E8; 
}
h1, h2, h3 { 
    font-family: 'Playfair Display', serif; 
    color: #F5F5F5;
}
body, p, div, span, input, button { 
    font-family: 'Inter', sans-serif; 
}
.sov-kpi { 
    background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
    padding: 16px; 
    border-radius: 12px; 
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 4px solid #A78BFA;
}
.sov-card { 
    background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
    padding: 20px; 
    border-radius: 12px; 
    border: 1px solid rgba(255,255,255,0.05);
    margin: 12px 0;
}
.domain-card {
    border-left: 4px solid;
    background: rgba(255,255,255,0.02);
    padding: 16px;
    margin: 8px 0;
    border-radius: 8px;
}
.domain-inner { border-left-color: #60A5FA; }
.domain-shadow { border-left-color: #F87171; }
.domain-somatic { border-left-color: #34D399; }
.domain-financial { border-left-color: #FBBF24; }
.metric-badge {
    background: rgba(139, 69, 255, 0.2);
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 12px;
    margin: 2px;
}
.biz-kpi { border-left-color: #10B981; }
.client-kpi { border-left-color: #3B82F6; }
.pipeline-kpi { border-left-color: #8B5CF6; }
</style>
""", unsafe_allow_html=True)

# --- SOVEREIGN OS HEADER ---
v3_progress = calculate_v3_progress()

st.markdown("<div style='text-align: center; margin-bottom: 30px;'>", unsafe_allow_html=True)
st.markdown("<h1 style='margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>V3 SOVEREIGN OS</h1>", unsafe_allow_html=True)
st.markdown(f"<div style='color: #9CA3AF;'>90-Day Transformation • Day {v3_progress['days_completed']} • {V3_SYSTEM[v3_progress['current_phase']]['title']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- PROGRESS OVERVIEW ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("<div class='sov-kpi'><strong>Transformation Progress</strong><div style='font-size:24px;'>{}%</div></div>".format(int(v3_progress["completion_rate"])), unsafe_allow_html=True)
with col2:
    st.markdown("<div class='sov-kpi'><strong>Current Phase</strong><div style='font-size:18px;'>{}</div></div>".format(V3_SYSTEM[v3_progress["current_phase"]]["title"].split(":")[0]), unsafe_allow_html=True)
with col3:
    st.markdown("<div class='sov-kpi'><strong>Days Completed</strong><div style='font-size:24px;'>{}/90</div></div>".format(v3_progress["days_completed"]), unsafe_allow_html=True)
with col4:
    st.markdown("<div class='sov-kpi'><strong>System Integrity</strong><div style='font-size:24px;'>🛡️ 92%</div></div>", unsafe_allow_html=True)

st.markdown("---")

# --- MAIN DASHBOARD ---
col1, col2 = st.columns([2, 1])

with col1:
    # CURRENT PHASE FOCUS
    current_phase = V3_SYSTEM[v3_progress["current_phase"]]
    st.markdown("<div class='sov-card'>", unsafe_allow_html=True)
    st.markdown("### 🎯 {}".format(current_phase['title']))
    st.markdown("**Focus:** {}".format(current_phase['focus']))
    
    # Domain Progress
    for domain_id, domain in current_phase["domains"].items():
        css_class = "domain-card domain-{}".format(domain_id.split('_')[0])
        st.markdown("<div class='{}'>".format(css_class), unsafe_allow_html=True)
        st.markdown("**{}**".format(domain['name']))
        st.markdown("*Protocols:* {}".format(', '.join(domain['protocols'])))
        
        # Metrics display
        metrics_html = " ".join(["<span class='metric-badge'>{}</span>".format(m) for m in domain["metrics"]])
        st.markdown("*Metrics:* {}".format(metrics_html), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    # DAILY V3 RITUAL LOG
    st.markdown("<div class='sov-card'>", unsafe_allow_html=True)
    st.markdown("### 📝 Daily Sovereign Practice")
    
    with st.form("daily_sovereign_form"):
        st.markdown("**Somatic Metrics**")
        armored_rating = st.slider("Armored Body Rating (1-10)", 1, 10, 5)
        interoception = st.slider("Interoception Score (1-10)", 1, 10, 5)
        
        st.markdown("**Shadow Work**")
        self_judgment = st.slider("Self-Judgment Frequency (1-10)", 1, 10, 5)
        dissociation = st.slider("Dissociation Frequency (1-10)", 1, 10, 5)
        
        st.markdown("**Action Compliance**")
        shielding = st.checkbox("Energetic Shielding Completed")
        micro_actions = st.number_input("Micro-Actions Executed", 0, 10, 0)
        imperfect_act = st.checkbox("Imperfect Act Executed")
        
        v3_alignment = st.text_area("V3 Alignment Notes", placeholder="How today's work aligns with current phase...")
        
        if st.form_submit_button("💎 Log Sovereign Day"):
            # Save daily metrics
            try:
                df_daily = pd.read_csv(DAILY_METRICS_CSV)
                new_row = {
                    "Date": date.today().isoformat(),
                    "Armored_Body_Rating": armored_rating,
                    "Self_Judgment_Frequency": self_judgment,
                    "Shielding_Compliance": 1 if shielding else 0,
                    "Micro_Actions_Executed": micro_actions,
                    "Interoception_Score": interoception,
                    "Pricing_Changes": 0,
                    "Boundary_Success": 0,
                    "Creative_Stagnation": 10 - interoception,
                    "Dissociation_Frequency": dissociation,
                    "V3_Alignment": v3_alignment
                }
                df_daily = pd.concat([df_daily, pd.DataFrame([new_row])], ignore_index=True)
                df_daily.to_csv(DAILY_METRICS_CSV, index=False)
                st.success("🌀 Sovereign day logged! Energy preserved.")
            except Exception as e:
                st.error("Error saving: {}".format(e))
    
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    # SHADOW DOSSIER STATUS
    st.markdown("<div class='sov-card'>", unsafe_allow_html=True)
    st.markdown("### 🕵️ Shadow Dossiers")
    
    try:
        with open(SHADOW_DOSSIERS_JSON, 'r') as f:
            shadows = json.load(f)
        
        for shadow_id, shadow in shadows.items():
            integration = shadow.get('integration_progress', 0)
            strength = shadow.get('current_strength', 5)
            
            st.markdown("**{} - {}**".format(shadow_id, shadow['name']))
            st.markdown("*Strength:* {}/10".format(strength))
            st.progress(integration / 100)
            st.markdown("---")
    except:
        st.info("Shadow dossiers loading...")
    
    st.markdown("</div>", unsafe_allow_html=True)

    # EVOLUTION GRAPH
    st.markdown("<div class='sov-card'>", unsafe_allow_html=True)
    st.markdown("### 📈 Transformation Evolution")
    
    try:
        df_daily = pd.read_csv(DAILY_METRICS_CSV)
        if len(df_daily) > 1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_daily['Date'], 
                y=10 - df_daily['Armored_Body_Rating'],
                name="Somatic Freedom",
                line=dict(color="#34D399")
            ))
            fig.add_trace(go.Scatter(
                x=df_daily['Date'],
                y=10 - df_daily['Self_Judgment_Frequency'],
                name="Self-Acceptance", 
                line=dict(color="#60A5FA")
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="white",
                height=300,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Log more data to see evolution graph")
    except:
        st.info("Evolution graph loading...")
    
    st.markdown("</div>", unsafe_allow_html=True)

    # QUICK SOVEREIGN ACTIONS
    st.markdown("<div class='sov-card'>", unsafe_allow_html=True)
    st.markdown("### ⚡ Sovereign Commands")
    
    if st.button("🌀 Breath Command (4-8)"):
        st.info("""
        **Breath Command Activated:**
        - Inhale: 4 counts  
        - Hold: 4 counts
        - Exhale: 8 counts
        - Repeat 5x
        """)
    
    if st.button("🛡️ Energetic Shielding"):
        st.success("""
        **Shielding Ritual:**
        - Visualize golden light surrounding you
        - Set intention: Only aligned energy may enter
        - Seal with 3 deep breaths
        """)
    
    if st.button("💎 Mirror Self-Compassion"):
        st.info("""
        **Mirror Practice:**
        - Look in mirror for 2 minutes
        - Speak: I see you. I love you. We're safe.
        - Notice resistance without judgment
        """)
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- BUSINESS COMMAND CENTER ---
st.markdown("---")
st.markdown("## 💼 Business Command Center")
st.markdown("**V3-Aligned Business Growth** • Shadow Work → Revenue Pipeline")

# Business Metrics Overview
biz_col1, biz_col2, biz_col3, biz_col4 = st.columns(4)

with biz_col1:
    st.markdown("<div class='sov-kpi biz-kpi'><strong>Monthly Revenue</strong><div style='font-size:24px;'>$8,450</div><div style='font-size:12px; color: #10B981;'>↑ 12% this month</div></div>", unsafe_allow_html=True)

with biz_col2:
    st.markdown("<div class='sov-kpi client-kpi'><strong>Active Clients</strong><div style='font-size:24px;'>6</div><div style='font-size:12px; color: #3B82F6;'>+2 this quarter</div></div>", unsafe_allow_html=True)

with biz_col3:
    st.markdown("<div class='sov-kpi pipeline-kpi'><strong>Proposal Pipeline</strong><div style='font-size:24px;'>$24K</div><div style='font-size:12px; color: #8B5CF6;'>3 opportunities</div></div>", unsafe_allow_html=True)

with biz_col4:
    st.markdown("<div class='sov-kpi' style='border-left-color: #F59E0B;'><strong>Close Rate</strong><div style='font-size:24px;'>42%</div><div style='font-size:12px; color: #F59E0B;'>V3 confidence effect</div></div>", unsafe_allow_html=True)

# Business-Shadow Alignment
biz_main_col1, biz_main_col2 = st.columns([2, 1])

with biz_main_col1:
    st.markdown("<div class='sov-card'>", unsafe_allow_html=True)
    st.markdown("### 🎯 V3 Business Alignment")
    
    # Shadow-to-Business Impact Tracking
    st.markdown("**Shadow Work → Business Results**")
    
    shadow_biz_map = {
        "Wounded Perfectionist (1.1)": "Pricing confidence & proposal speed",
        "Imposter/Scarcity Self (7.1)": "Value-based pricing implementation", 
        "Control Tycoon (7.2)": "Delegation & team scaling",
        "Hidden Victim/Martyr (1.2)": "Boundary setting with clients"
    }
    
    for shadow, business_impact in shadow_biz_map.items():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.checkbox(f"Integrating {shadow.split('(')[0]}")
        with col2:
            st.info(f"**→** {business_impact}")
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Revenue Tracking
    st.markdown("<div class='sov-card'>", unsafe_allow_html=True)
    st.markdown("### 📈 Revenue Evolution")
    
    # Sample revenue data aligned with V3 phases
    revenue_data = pd.DataFrame({
        'Phase': ['Pre-V3', 'Phase 1', 'Phase 2', 'Phase 3 Target'],
        'MRR': [4500, 6450, 8450, 12500],
        'Clients': [3, 4, 6, 8],
        'Avg Deal Size': [1500, 1612, 2100, 2800]
    })
    
    fig_revenue = px.line(revenue_data, x='Phase', y='MRR', markers=True,
                         title="MRR Growth Through V3 Transformation")
    fig_revenue.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig_revenue, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with biz_main_col2:
    # Quick Business Actions
    st.markdown("<div class='sov-card'>", unsafe_allow_html=True)
    st.markdown("### ⚡ Business Commands")
    
    if st.button("💰 Send Invoice", use_container_width=True):
        st.success("**Invoice queued** - Scarcity shadow confronted")
        
    if st.button("🎯 Price Increase", use_container_width=True):
        st.success("**Pricing updated** - Value alignment activated")
        
    if st.button("📞 Client Check-in", use_container_width=True):
        st.info("**Boundary practice opportunity** - Clear communication")
        
    if st.button("📊 Review Metrics", use_container_width=True):
        st.info("**Performance review** - Detach from outcomes")
    
    st.markdown("---")
    
    # Daily Business Priority
    st.markdown("**Today's Business Focus**")
    biz_priority = st.selectbox("Priority Action", [
        "Revenue-generating tasks only",
        "Client delivery & excellence", 
        "Marketing & outreach",
        "Systems & automation",
        "Team development"
    ])
    
    st.markdown(f"**V3 Alignment:** {biz_priority}")
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Client Pipeline
    st.markdown("<div class='sov-card'>", unsafe_allow_html=True)
    st.markdown("### 👥 Client Pipeline")
    
    pipeline_data = {
        'Prospect': ['Tech Startup A', 'E-commerce Brand', 'Consulting Firm'],
        'Value': ['$3,000/mo', '$4,500/mo', '$6,000/mo'],
        'Status': ['Discovery', 'Proposal', 'Negotiation'],
        'Shadow Block': ['Imposter', 'Perfectionist', 'Scarcity']
    }
    
    st.dataframe(pd.DataFrame(pipeline_data), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- V3 BUSINESS RITUALS ---
st.markdown("<div class='sov-card'>", unsafe_allow_html=True)
st.markdown("### 🏛️ V3 Business Rituals")

ritual_col1, ritual_col2, ritual_col3 = st.columns(3)

with ritual_col1:
    st.markdown("**💰 Money Rituals**")
    st.checkbox("Morning revenue visualization")
    st.checkbox("End-of-day invoicing practice")
    st.checkbox("Weekly profit celebration")

with ritual_col2:
    st.markdown("**🎯 Client Rituals**")
    st.checkbox("Pre-call boundary setting")
    st.checkbox("Post-delivery value acknowledgment")
    st.checkbox("Monthly client success review")

with ritual_col3:
    st.markdown("**📈 Growth Rituals**")
    st.checkbox("Weekly marketing courage practice")
    st.checkbox("Monthly pricing review")
    st.checkbox("Quarterly business vision alignment")

st.markdown("</div>", unsafe_allow_html=True)

# --- SHADOW-BUSINESS CORRELATION ---
st.markdown("<div class='sov-card'>", unsafe_allow_html=True)
st.markdown("### 🔗 Shadow-Business Correlation")

corr_col1, corr_col2 = st.columns(2)

with corr_col1:
    st.markdown("**When I work on:**")
    st.success("• **Self-worth shadows** → Higher pricing")
    st.success("• **Perfectionism shadows** → Faster delivery")
    st.success("• **Control shadows** → Better delegation")
    st.success("• **Boundary shadows** → Better clients")

with corr_col2:
    st.markdown("**Business impact:**")
    st.info("• **+42%** close rate improvement")
    st.info("• **-60%** delivery timeline")
    st.info("• **+15h/week** creative capacity")
    st.info("• **2x** client retention")

st.markdown("</div>", unsafe_allow_html=True)

# --- TECHNICAL PROGRESS TRACKER ---
st.markdown("---")
st.markdown("## 🛠️ Sovereign OS Development")

tech_col1, tech_col2, tech_col3 = st.columns(3)

with tech_col1:
    st.markdown("<div class='sov-card'>", unsafe_allow_html=True)
    st.markdown("### Phase 1 MVP")
    st.checkbox("✅ Basic input widgets", value=True)
    st.checkbox("✅ Shadow dossier structure", value=True)
    st.checkbox("✅ Daily metrics logging", value=True)
    st.checkbox("🔲 Money affirmation widget")
    st.markdown("</div>", unsafe_allow_html=True)

with tech_col2:
    st.markdown("<div class='sov-card'>", unsafe_allow_html=True)
    st.markdown("### Phase 2 Integration")
    st.checkbox("🔲 Weekly embodiment tracker")
    st.checkbox("🔲 Shadow-to-Outcome mapping")
    st.checkbox("🔲 Boundary script log")
    st.checkbox("🔲 Simulated AI diagnosis")
    st.markdown("</div>", unsafe_allow_html=True)

with tech_col3:
    st.markdown("<div class='sov-card'>", unsafe_allow_html=True)
    st.markdown("### Phase 3 Mastery")
    st.checkbox("🔲 Gemini API integration")
    st.checkbox("🔲 Sensual practice tracker")
    st.checkbox("🔲 Evolution graph")
    st.checkbox("🔲 Full deployment")
    st.markdown("</div>", unsafe_allow_html=True)

# --- ALCHEMY STAGE TRACKING ---
st.markdown("---")
st.markdown("## 🧪 Alchemy Stage Progress")

alchemy_col1, alchemy_col2, alchemy_col3 = st.columns(3)

with alchemy_col1:
    st.markdown("<div class='sov-card' style='border-left: 4px solid #7C3AED;'>", unsafe_allow_html=True)
    st.markdown("### 🌑 Nigredo")
    st.markdown("**Shadow Confrontation**")
    st.progress(0.7)
    st.markdown("*Dissolving old structures*")
    st.markdown("</div>", unsafe_allow_html=True)

with alchemy_col2:
    st.markdown("<div class='sov-card' style='border-left: 4px solid #60A5FA;'>", unsafe_allow_html=True)
    st.markdown("### ⚪ Albedo")
    st.markdown("**Purification**")
    st.progress(0.3)
    st.markdown("*Washing in soul light*")
    st.markdown("</div>", unsafe_allow_html=True)

with alchemy_col3:
    st.markdown("<div class='sov-card' style='border-left: 4px solid #F59E0B;'>", unsafe_allow_html=True)
    st.markdown("### 🔴 Rubedo")
    st.markdown("**Integration**")
    st.progress(0.1)
    st.markdown("*Embodied sovereignty*")
    st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("<div style='text-align: center; color: #6B7280;'>", unsafe_allow_html=True)
st.markdown("**V3 SOVEREIGN OS** • Day {}/90 • Energy Preserved • Shadows Integrated • Revenue Flowing".format(v3_progress['days_completed']))
st.markdown("</div>", unsafe_allow_html=True)