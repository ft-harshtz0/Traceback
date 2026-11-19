"""
TraceBack — Network Incident Investigation Simulator
High-Aesthetic Modern Cybersecurity / SOC Platform Interface.
Strictly conforms to PRD.md specifications.
"""

import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from engine import (
    parse_and_validate_csv,
    correlate_events,
    generate_evidence_summary
)
from database import init_db, save_events, load_events_from_db

# ── Page Configuration ─────────────────────────────────────────
st.set_page_config(
    page_title="TraceBack | Network Incident Simulator",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Aesthetic Modern Cyberpunk / High-Tech CSS Foundation ──────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Global Foundation Reset */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Ambient Deep-Space Mesh Background */
    .stApp {
        background: radial-gradient(circle at 15% 10%, rgba(22, 33, 62, 0.45) 0%, transparent 45%),
                    radial-gradient(circle at 85% 85%, rgba(13, 27, 42, 0.6) 0%, transparent 45%),
                    radial-gradient(circle at 50% 50%, rgba(10, 14, 23, 0.95) 0%, #06080d 100%);
        background-color: #06080d;
        color: #e2e8f0;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1400px;
    }

    /* Sleek Sidebar with Glassmorphism */
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 14, 24, 0.82) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.08) !important;
    }

    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        color: #ffffff !important;
    }
    
    p, span, label {
        color: #94a3b8;
    }

    code {
        font-family: 'JetBrains Mono', monospace !important;
        background: rgba(30, 41, 59, 0.7) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.2) !important;
        padding: 2px 6px !important;
        border-radius: 6px !important;
        font-size: 0.85em !important;
    }

    /* Top HUD App Banner */
    .hud-banner {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(15, 23, 42, 0.4) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 24px;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 32px -4px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }

    .hud-title-wrap {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    
    .hud-logo-icon {
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
        font-size: 22px;
    }

    .hud-title {
        font-size: 1.45rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ffffff 0%, #cbd5e1 50%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }

    .hud-subtitle {
        font-size: 0.8rem;
        color: #64748b;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin: 2px 0 0 0;
    }

    .hud-status-chip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(34, 197, 94, 0.3);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-family: 'JetBrains Mono', monospace;
        color: #4ade80;
        box-shadow: 0 0 15px rgba(34, 197, 94, 0.15);
    }

    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #22c55e;
        border-radius: 50%;
        box-shadow: 0 0 10px #22c55e;
        animation: pulseAnimation 2s infinite;
    }

    @keyframes pulseAnimation {
        0% { transform: scale(0.95); opacity: 0.6; }
        50% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 14px #22c55e; }
        100% { transform: scale(0.95); opacity: 0.6; }
    }

    /* Metric Glass Cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }

    .cyber-metric-card {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.8) 0%, rgba(15, 23, 42, 0.5) 100%);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 18px 20px;
        backdrop-filter: blur(12px);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
    }
    .cyber-metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.3);
        box-shadow: 0 8px 28px -4px rgba(56, 189, 248, 0.15);
    }

    .metric-accent-line {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
    }
    .accent-cyan { background: linear-gradient(90deg, #38bdf8, #0284c7); }
    .accent-rose { background: linear-gradient(90deg, #f43f5e, #be123c); }
    .accent-violet { background: linear-gradient(90deg, #a855f7, #6366f1); }
    .accent-amber { background: linear-gradient(90deg, #f59e0b, #d97706); }

    .metric-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .metric-label {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #94a3b8;
    }
    .metric-badge {
        font-size: 0.7rem;
        padding: 3px 8px;
        border-radius: 10px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
    }
    .badge-cyan { background: rgba(56, 189, 248, 0.12); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.25); }
    .badge-rose { background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3); }
    .badge-violet { background: rgba(168, 85, 247, 0.12); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.25); }
    .badge-amber { background: rgba(245, 158, 11, 0.12); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.25); }

    .metric-value {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #ffffff;
        line-height: 1.1;
    }
    .metric-subtext {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 6px;
    }

    /* Modern Styled Containers */
    .glass-panel {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.75) 0%, rgba(15, 23, 42, 0.45) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 22px;
        backdrop-filter: blur(16px);
        margin-bottom: 20px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    }

    /* Event Timeline Feed Items */
    .timeline-node-card {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-left: 4px solid #38bdf8;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
        backdrop-filter: blur(8px);
    }
    .timeline-node-card:hover {
        background: rgba(15, 23, 42, 0.9);
        border-color: rgba(56, 189, 248, 0.3);
        transform: translateX(4px);
    }
    .timeline-node-suspicious {
        background: linear-gradient(90deg, rgba(244, 63, 94, 0.12) 0%, rgba(15, 23, 42, 0.65) 100%);
        border: 1px solid rgba(244, 63, 94, 0.3);
        border-left: 4px solid #f43f5e;
    }
    .timeline-node-suspicious:hover {
        border-color: rgba(244, 63, 94, 0.5);
    }

    .node-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
        flex-wrap: wrap;
        gap: 8px;
    }
    .node-time {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #94a3b8;
    }
    .node-category {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 6px;
        text-transform: uppercase;
    }
    .cat-firewall { background: rgba(2, 132, 199, 0.2); color: #38bdf8; border: 1px solid rgba(2, 132, 199, 0.4); }
    .cat-dns { background: rgba(147, 51, 234, 0.2); color: #c084fc; border: 1px solid rgba(147, 51, 234, 0.4); }
    .cat-login { background: rgba(22, 163, 74, 0.2); color: #4ade80; border: 1px solid rgba(22, 163, 74, 0.4); }

    .node-desc {
        font-size: 0.92rem;
        color: #f1f5f9;
        margin-bottom: 6px;
        font-weight: 500;
    }
    .node-chips {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        align-items: center;
    }
    .ip-chip {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.76rem;
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.15);
        color: #cbd5e1;
        padding: 2px 7px;
        border-radius: 6px;
    }
    .alert-pill {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.72rem;
        font-weight: 700;
        background: rgba(244, 63, 94, 0.2);
        color: #fda4af;
        border: 1px solid rgba(244, 63, 94, 0.4);
        padding: 2px 8px;
        border-radius: 12px;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }

    .correlation-box {
        margin-top: 8px;
        padding: 8px 12px;
        background: rgba(244, 63, 94, 0.08);
        border-left: 2px solid #f43f5e;
        border-radius: 0 6px 6px 0;
        font-size: 0.8rem;
        color: #fecdd3;
    }

    /* Buttons Re-styling */
    div.stButton > button {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.2) 0%, rgba(14, 165, 233, 0.3) 100%) !important;
        border-color: rgba(56, 189, 248, 0.5) !important;
        color: #ffffff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.25) !important;
    }
    div.stButton > button[kind="primary"], div.stButton > button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        border-color: #38bdf8 !important;
        color: #ffffff !important;
        box-shadow: 0 0 20px rgba(2, 132, 199, 0.4) !important;
    }
    div.stButton > button[kind="primary"]:hover, div.stButton > button[data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important;
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.6) !important;
    }

    /* Streamlit Download Button */
    div.stDownloadButton > button {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    div.stDownloadButton > button:hover {
        background: rgba(56, 189, 248, 0.15) !important;
        border-color: #38bdf8 !important;
        color: #ffffff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.3) !important;
    }

    /* Inputs, Selectboxes, and MultiSelects */
    div[data-baseweb="select"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
    }
    div[data-baseweb="tag"] {
        background-color: rgba(56, 189, 248, 0.2) !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 6px !important;
    }

    /* Streamlit Tables / Dataframes */
    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    /* Custom Radio Navigation Bar */
    div[data-testid="stRadio"] > div {
        gap: 6px;
    }
    div[data-testid="stRadio"] label {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 8px 14px;
        margin-bottom: 4px;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    div[data-testid="stRadio"] label:hover {
        background: rgba(30, 41, 59, 0.8);
        border-color: rgba(56, 189, 248, 0.3);
    }
    div[data-testid="stRadio"] label[data-checked="true"] {
        background: linear-gradient(90deg, rgba(2, 132, 199, 0.25) 0%, rgba(15, 23, 42, 0.8) 100%) !important;
        border-color: rgba(56, 189, 248, 0.6) !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.15);
    }
</style>
""", unsafe_allow_html=True)

# ── Session State Init ─────────────────────────────────────────
for key, default in [("events", []), ("warnings", []), ("scenario", "all"), ("db_ready", False)]:
    if key not in st.session_state:
        st.session_state[key] = default

if not st.session_state.db_ready:
    init_db()
    st.session_state.db_ready = True

# ── Helpers ────────────────────────────────────────────────────
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_data")

def _read_sample(fname: str) -> pd.DataFrame:
    path = os.path.join(SAMPLE_DIR, fname)
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

def load_scenario(key: str):
    fw_df  = _read_sample("firewall.csv")
    dns_df = _read_sample("dns.csv")
    lg_df  = _read_sample("login.csv")

    ip_map = {
        "scenario_a": "192.168.1.50",
        "scenario_b": "203.0.113.15",
        "scenario_c": "192.168.1.75",
    }
    if key in ip_map:
        ip = ip_map[key]
        fw_df  = fw_df[fw_df["source_ip"]  == ip] if not fw_df.empty  else fw_df
        dns_df = dns_df[dns_df["source_ip"] == ip] if not dns_df.empty else dns_df
        lg_df  = lg_df[lg_df["source_ip"]  == ip] if not lg_df.empty  else lg_df
        if key == "scenario_b":
            dns_df = pd.DataFrame()

    events, warnings = [], []
    for df, ltype in [(fw_df, "firewall"), (dns_df, "dns"), (lg_df, "login")]:
        if not df.empty:
            evs, warns = parse_and_validate_csv(df, ltype)
            events.extend(evs)
            warnings.extend(warns)

    correlated = correlate_events(events)
    save_events(correlated)
    st.session_state.events   = correlated
    st.session_state.warnings = warnings
    st.session_state.scenario = key

# Load default dataset if none present
if not st.session_state.events and st.session_state.scenario == "all":
    load_scenario("all")

# ── Top HUD Header ─────────────────────────────────────────────
events = st.session_state.events
total_count = len(events)
susp_count = sum(1 for e in events if e.get("is_suspicious"))

scenario_names = {
    "all": "Full Telemetry Cluster (All Datasets)",
    "scenario_a": "Scenario A: Normal Baseline Traffic",
    "scenario_b": "Scenario B: SSH Credential Brute Force",
    "scenario_c": "Scenario C: C2 DNS & Beaconing",
    "custom": "Custom Uploaded Telemetry",
    "None": "No Dataset Loaded"
}
active_scenario_label = scenario_names.get(st.session_state.scenario, "Synthetic Pipeline")

st.markdown(f"""
<div class="hud-banner">
    <div class="hud-title-wrap">
        <div class="hud-logo-icon">🛡️</div>
        <div>
            <h1 class="hud-title">TraceBack // SOC Incident Simulator</h1>
            <p class="hud-subtitle">Autonomous Log Correlation &amp; Digital Forensics Engine</p>
        </div>
    </div>
    <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
        <div class="hud-status-chip">
            <div class="pulse-dot"></div>
            <span>CORRELATION ENGINE ONLINE</span>
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #94a3b8; background: rgba(15,23,42,0.6); padding: 6px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
            ACTIVE PIPELINE: <span style="color: #38bdf8;">{active_scenario_label}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar Control Station ─────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
        <span style="font-size: 1.5rem;">⚡</span>
        <div>
            <div style="font-weight: 800; color: #ffffff; font-size: 1.1rem; letter-spacing: -0.01em;">MISSION CONTROL</div>
            <div style="font-size: 0.72rem; color: #64748b; font-family: 'JetBrains Mono', monospace;">TRACEBACK V2.0 // ADVANCED SOC</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("<p style='font-weight:700; color:#cbd5e1; font-size:0.82rem; text-transform:uppercase; letter-spacing:0.04em;'>Preset Attack Scenarios</p>", unsafe_allow_html=True)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📦 All Data", use_container_width=True):
            load_scenario("all")
            st.rerun()
        if st.button("🟢 Normal", use_container_width=True, help="Scenario A: Benign DNS, Web, and Auth"):
            load_scenario("scenario_a")
            st.rerun()
    with col_btn2:
        if st.button("🔴 Brute Force", use_container_width=True, help="Scenario B: SSH Failed Logins followed by Success"):
            load_scenario("scenario_b")
            st.rerun()
        if st.button("🟡 C2 Beacon", use_container_width=True, help="Scenario C: DNS Resolution & Exfiltration"):
            load_scenario("scenario_c")
            st.rerun()

    st.markdown("---")
    st.markdown("<p style='font-weight:700; color:#cbd5e1; font-size:0.82rem; text-transform:uppercase; letter-spacing:0.04em;'>Engine Parameters</p>", unsafe_allow_html=True)
    time_window = st.slider("Correlation Window (mins)", min_value=5, max_value=60, value=15, step=5)
    if st.button("⚡ Re-Run Correlation", use_container_width=True, type="primary"):
        if st.session_state.events:
            st.session_state.events = correlate_events(st.session_state.events, window_minutes=time_window)
            save_events(st.session_state.events)
            st.rerun()

    st.markdown("---")
    st.markdown("<p style='font-weight:700; color:#cbd5e1; font-size:0.82rem; text-transform:uppercase; letter-spacing:0.04em;'>Navigation</p>", unsafe_allow_html=True)
    nav = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "⏱️ Incident Timeline",
            "📂 Telemetry Logs",
            "📋 Threat Dossier",
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.caption("🛡️ TraceBack Security Architecture • Local SQLite In-Memory DB")

# Re-read events from state
events = st.session_state.events

# =============================================================
# 1. DASHBOARD (FR-01)
# =============================================================
if nav == "📊 Dashboard":
    total = len(events)
    suspicious = sum(1 for e in events if e.get("is_suspicious"))
    unique_ips = len(set(
        [e["source_ip"] for e in events] +
        [e["destination_ip"] for e in events if e.get("destination_ip")]
    ))
    groups = len(set(e.get("group_id", "") for e in events if e.get("group_id")))

    # High-Impact Modern Metric Cards Grid
    st.markdown(f"""
    <div class="metric-grid">
        <div class="cyber-metric-card">
            <div class="metric-accent-line accent-cyan"></div>
            <div class="metric-header">
                <span class="metric-label">Ingested Telemetry</span>
                <span class="metric-badge badge-cyan">LOGS</span>
            </div>
            <div class="metric-value">{total}</div>
            <div class="metric-subtext">Events normalized in database</div>
        </div>
        <div class="cyber-metric-card">
            <div class="metric-accent-line accent-rose"></div>
            <div class="metric-header">
                <span class="metric-label">Suspicious Anomalies</span>
                <span class="metric-badge badge-rose">{'ALERT ACTIVE' if suspicious > 0 else 'QUIET'}</span>
            </div>
            <div class="metric-value" style="color: {'#fb7185' if suspicious > 0 else '#ffffff'};">{suspicious}</div>
            <div class="metric-subtext">Multi-stage correlation triggers</div>
        </div>
        <div class="cyber-metric-card">
            <div class="metric-accent-line accent-violet"></div>
            <div class="metric-header">
                <span class="metric-label">Monitored Entities</span>
                <span class="metric-badge badge-violet">IP HOSTS</span>
            </div>
            <div class="metric-value">{unique_ips}</div>
            <div class="metric-subtext">Unique endpoints identified</div>
        </div>
        <div class="cyber-metric-card">
            <div class="metric-accent-line accent-amber"></div>
            <div class="metric-header">
                <span class="metric-label">Incident Clusters</span>
                <span class="metric-badge badge-amber">SESSIONS</span>
            </div>
            <div class="metric-value">{groups}</div>
            <div class="metric-subtext">Correlated investigation groups</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not events:
        st.info("💡 No logs loaded. Use the sidebar to load a synthetic scenario, or go to Telemetry Logs to upload CSVs.")
    else:
        col_c1, col_c2 = st.columns([1.1, 1])

        with col_c1:
            st.markdown("""
            <div class="glass-panel">
                <h4 style="margin: 0 0 16px 0; font-size: 1.05rem;">Telemetry Composition</h4>
            """, unsafe_allow_html=True)

            cat_data = pd.DataFrame({"Category": [e["event_type"].upper() for e in events]})
            fig_pie = px.pie(
                cat_data, names="Category",
                color="Category",
                color_discrete_map={
                    "FIREWALL": "#0284c7",
                    "DNS": "#a855f7",
                    "LOGIN": "#10b981"
                },
                hole=0.55
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#cbd5e1",
                font_family="Plus Jakarta Sans",
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
                height=280
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_c2:
            st.markdown("""
            <div class="glass-panel">
                <h4 style="margin: 0 0 16px 0; font-size: 1.05rem;">Incident Investigation Groups</h4>
            """, unsafe_allow_html=True)

            group_ids = sorted(set(e.get("group_id", "") for e in events if e.get("group_id")))
            for gid in group_ids:
                g_events = [e for e in events if e.get("group_id") == gid]
                has_susp = any(e.get("is_suspicious") for e in g_events)
                ips = ", ".join(sorted(set(e["source_ip"] for e in g_events)))
                
                badge_html = (
                    '<span class="alert-pill">🚨 SUSPICIOUS CLUSTER</span>'
                    if has_susp else
                    '<span style="background:rgba(16,185,129,0.15); color:#6ee7b7; border:1px solid rgba(16,185,129,0.3); font-size:0.72rem; padding:2px 8px; border-radius:10px; font-weight:700;">BENIGN</span>'
                )
                border_color = "rgba(244, 63, 94, 0.4)" if has_susp else "rgba(56, 189, 248, 0.2)"
                bg_color = "rgba(244, 63, 94, 0.05)" if has_susp else "rgba(15, 23, 42, 0.5)"
                
                st.markdown(f"""
                <div style="background:{bg_color}; border:1px solid {border_color}; border-radius:10px; padding:12px 14px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                        <strong style="color:#ffffff; font-family:'JetBrains Mono', monospace; font-size:0.95rem;">{gid}</strong>
                        {badge_html}
                    </div>
                    <div style="font-size:0.8rem; color:#94a3b8;">
                        <span style="color:#cbd5e1;">{len(g_events)} events</span> • Involved: <span style="font-family:'JetBrains Mono', monospace; color:#38bdf8;">{ips}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

# =============================================================
# 2. INCIDENT TIMELINE (FR-04)
# =============================================================
elif nav == "⏱️ Incident Timeline":
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="margin: 0; font-size: 1.5rem;">Chronological Incident Timeline</h2>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.9rem;">
            Interactive timeline reconstructing the exact multi-vector attack chain across Firewall, DNS, and Identity services.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not events:
        st.info("No events loaded. Select a scenario from the sidebar.")
    else:
        tl_rows = []
        for e in events:
            tl_rows.append({
                "Timestamp": pd.to_datetime(e["timestamp"]),
                "Category": e["event_type"].upper(),
                "Source IP": e["source_ip"],
                "Destination IP": e.get("destination_ip") or "N/A",
                "Description": e["description"],
                "Status": "Suspicious Activity" if e.get("is_suspicious") else "Routine Event",
                "Incident": e.get("group_id") or "—",
                "Notes": "<br>".join(e.get("correlation_notes", [])) if e.get("correlation_notes") else "None",
            })
        tl_df = pd.DataFrame(tl_rows)

        # Plotly Interactive Cyber Scatter Timeline
        fig = px.scatter(
            tl_df,
            x="Timestamp",
            y="Category",
            color="Status",
            symbol="Status",
            hover_data=["Source IP", "Destination IP", "Description"],
            color_discrete_map={
                "Suspicious Activity": "#f43f5e",
                "Routine Event": "#38bdf8"
            },
            title="Multi-Source Attack Progression (Chronological)"
        )
        fig.update_traces(
            marker=dict(size=14, line=dict(width=2, color="rgba(255,255,255,0.7)")),
            selector=dict(mode='markers')
        )
        fig.update_layout(
            paper_bgcolor="rgba(15, 23, 42, 0.75)",
            plot_bgcolor="rgba(10, 14, 23, 0.9)",
            font_color="#cbd5e1",
            font_family="Plus Jakarta Sans",
            xaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.08)",
                zerolinecolor="rgba(255, 255, 255, 0.08)",
                title_font=dict(size=12, color="#94a3b8")
            ),
            yaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.08)",
                title_font=dict(size=12, color="#94a3b8")
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(0,0,0,0)"
            ),
            height=360,
            margin=dict(l=30, r=30, t=50, b=30)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<h4 style='margin-top:24px; margin-bottom:14px; font-size:1.15rem;'>Investigation Event Stream</h4>", unsafe_allow_html=True)
        
        # Chronological Feed
        for e in events:
            is_susp = e.get("is_suspicious")
            etype = e["event_type"].lower()
            cat_badge_class = f"cat-{etype}"
            card_class = "timeline-node-card timeline-node-suspicious" if is_susp else "timeline-node-card"
            
            corr_html = ""
            if e.get("correlation_notes"):
                corr_items = "".join([f"<div>⚡ <strong>Rule Trigger:</strong> {n}</div>" for n in e["correlation_notes"]])
                corr_html = f"<div class='correlation-box'>{corr_items}</div>"
            
            st.markdown(f"""
            <div class="{card_class}">
                <div class="node-header">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="node-category {cat_badge_class}">{e['event_type']}</span>
                        <span class="node-time">[{e['timestamp']}]</span>
                    </div>
                    <div>
                        {f'<span class="alert-pill">🚨 SUSPICIOUS DETECTED</span>' if is_susp else '<span style="font-size:0.75rem; color:#64748b;">ROUTINE</span>'}
                    </div>
                </div>
                <div class="node-desc">{e['description']}</div>
                <div class="node-chips">
                    <span class="ip-chip">SRC: <strong>{e['source_ip']}</strong></span>
                    {f'<span class="ip-chip">DST: <strong>{e.get("destination_ip")}</strong></span>' if e.get("destination_ip") else ''}
                    <span class="ip-chip" style="color: #a855f7;">CLUSTER: {e.get('group_id', 'DEFAULT')}</span>
                </div>
                {corr_html}
            </div>
            """, unsafe_allow_html=True)

# =============================================================
# 3. LOG VIEWER & INGESTION (FR-02, FR-07)
# =============================================================
elif nav == "📂 Telemetry Logs":
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="margin: 0; font-size: 1.5rem;">Normalized Telemetry Logs</h2>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.9rem;">
            Inspect raw and normalized event structures, upload custom CSV telemetry, and apply granular filters.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("⬆️ Ingest Custom CSV Telemetry Logs", expanded=False):
        st.markdown("<p style='font-size:0.85rem; color:#94a3b8;'>Select CSV files matching PRD schemas for Firewall, DNS, or Login events.</p>", unsafe_allow_html=True)
        u1, u2, u3 = st.columns(3)
        fw_file    = u1.file_uploader("Firewall CSV (timestamp, source_ip, destination_ip, action, destination_port)", type=["csv"], key="up_fw")
        dns_file   = u2.file_uploader("DNS CSV (timestamp, source_ip, queried_domain, resolved_ip)", type=["csv"], key="up_dns")
        login_file = u3.file_uploader("Login CSV (timestamp, source_ip, username, login_status)", type=["csv"], key="up_login")

        if st.button("Process & Correlate Uploaded Logs", type="primary", use_container_width=True):
            new_events, new_warnings = [], []
            for f, ltype in [(fw_file, "firewall"), (dns_file, "dns"), (login_file, "login")]:
                if f is not None:
                    try:
                        df = pd.read_csv(f)
                        evs, warns = parse_and_validate_csv(df, ltype)
                        new_events.extend(evs)
                        new_warnings.extend(warns)
                    except Exception as err:
                        new_warnings.append(f"Error parsing {ltype} CSV: {err}")

            if new_events:
                corr = correlate_events(new_events, window_minutes=time_window)
                save_events(corr)
                st.session_state.events = corr
                st.session_state.warnings = new_warnings
                st.session_state.scenario = "custom"
                st.success(f"Successfully processed and normalized {len(new_events)} records!")
                st.rerun()
            else:
                st.warning("No valid records found. Verify headers and timestamps.")

    if st.session_state.warnings:
        with st.expander(f"⚠️ Ingestion Validation Warnings ({len(st.session_state.warnings)})", expanded=True):
            for w in st.session_state.warnings:
                st.warning(w)

    if not events:
        st.info("No records loaded in memory. Load a scenario from the sidebar.")
    else:
        st.markdown("<div class='glass-panel' style='padding:16px 20px; margin-bottom:16px;'>", unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)
        cat_filter = f1.multiselect("Filter Category", ["firewall", "dns", "login"], default=["firewall", "dns", "login"])
        all_ips = sorted(set(
            [e["source_ip"] for e in events] +
            [e["destination_ip"] for e in events if e.get("destination_ip")]
        ))
        ip_filter = f2.multiselect("Filter IP Address", all_ips)
        susp_only = f3.checkbox("Show Suspicious Only", value=False)
        st.markdown("</div>", unsafe_allow_html=True)

        filtered = events
        if cat_filter:
            filtered = [e for e in filtered if e["event_type"] in cat_filter]
        if ip_filter:
            filtered = [e for e in filtered if e["source_ip"] in ip_filter or e.get("destination_ip") in ip_filter]
        if susp_only:
            filtered = [e for e in filtered if e.get("is_suspicious")]

        st.caption(f"Displaying {len(filtered)} of {len(events)} normalized records")

        rows = [{
            "Timestamp": str(e["timestamp"]),
            "Category": e["event_type"].upper(),
            "Source IP": e["source_ip"],
            "Destination IP": e.get("destination_ip") or "—",
            "Description": e["description"],
            "Anomaly Verdict": "🚨 SUSPICIOUS" if e.get("is_suspicious") else "ROUTINE",
            "Cluster ID": e.get("group_id") or "—",
            "Correlation Notes": " | ".join(e.get("correlation_notes", [])) or "None",
        } for e in filtered]
        
        st.dataframe(pd.DataFrame(rows), use_container_width=True, height=450)

# =============================================================
# 4. INVESTIGATION REPORT (FR-05, FR-06)
# =============================================================
elif nav == "📋 Threat Dossier":
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="margin: 0; font-size: 1.5rem;">Threat Intelligence Dossier & Evidence Summary</h2>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.9rem;">
            Cryptographically sound evidence summary generated dynamically from corroborated telemetry.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not events:
        st.info("No investigation telemetry available. Select a scenario from the sidebar.")
    else:
        group_ids = ["All"] + sorted(set(e.get("group_id", "") for e in events if e.get("group_id")))
        
        c_sel1, c_sel2 = st.columns([2, 1])
        with c_sel1:
            selected_target = st.selectbox("Target Investigation Cluster", group_ids)
        with c_sel2:
            st.caption("Selecting a cluster isolates timeline & evidence for that specific incident group.")

        summary = generate_evidence_summary(events, group_id=selected_target)

        dossier_col, action_col = st.columns([1.7, 1])

        with dossier_col:
            st.markdown(f"""
            <div class="glass-panel">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:12px;">
                    <div>
                        <span style="font-size:0.75rem; color:#64748b; font-family:'JetBrains Mono', monospace;">INVESTIGATION DOSSIER</span>
                        <h3 style="margin:2px 0 0 0; font-size:1.35rem; color:#38bdf8;">{summary['investigation_id']}</h3>
                    </div>
                    <div>
                        <span class="alert-pill">{'CRITICAL' if summary['suspicious_patterns'] else 'BENIGN BASELINE'}</span>
                    </div>
                </div>

                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-bottom:16px;">
                    <div style="background:rgba(15,23,42,0.6); padding:10px 12px; border-radius:8px; border:1px solid rgba(255,255,255,0.05);">
                        <div style="font-size:0.72rem; color:#94a3b8; text-transform:uppercase;">Time Range Window</div>
                        <div style="font-family:'JetBrains Mono', monospace; font-size:0.85rem; color:#f1f5f9; margin-top:3px;">{summary['time_range']}</div>
                    </div>
                    <div style="background:rgba(15,23,42,0.6); padding:10px 12px; border-radius:8px; border:1px solid rgba(255,255,255,0.05);">
                        <div style="font-size:0.72rem; color:#94a3b8; text-transform:uppercase;">Involved Host Entities</div>
                        <div style="font-family:'JetBrains Mono', monospace; font-size:0.85rem; color:#38bdf8; margin-top:3px;">{", ".join(summary['involved_ips']) if summary['involved_ips'] else 'None'}</div>
                    </div>
                </div>

                <h4 style="font-size:0.95rem; margin-top:16px; margin-bottom:10px; color:#cbd5e1;">Observed Threat Patterns</h4>
            """, unsafe_allow_html=True)

            if summary["suspicious_patterns"]:
                for pat in summary["suspicious_patterns"]:
                    st.markdown(f"""
                    <div style="background:rgba(244,63,94,0.1); border-left:3px solid #f43f5e; padding:10px 14px; border-radius:0 8px 8px 0; margin-bottom:8px; font-size:0.85rem; color:#fecdd3;">
                        <strong>[!] ANOMALY:</strong> {pat}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background:rgba(16,185,129,0.1); border-left:3px solid #10b981; padding:10px 14px; border-radius:0 8px 8px 0; margin-bottom:8px; font-size:0.85rem; color:#a7f3d0;">
                    ✓ No malicious or anomalous threat sequences detected under the current correlation parameters.
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<h4 style='font-size:0.95rem; margin-top:16px; margin-bottom:10px; color:#cbd5e1;'>Correlation Explanations</h4>", unsafe_allow_html=True)
            if summary["correlation_reasons"]:
                for r in summary["correlation_reasons"]:
                    st.markdown(f"""
                    <div style="background:rgba(56,189,248,0.08); border-left:3px solid #38bdf8; padding:8px 12px; border-radius:0 8px 8px 0; margin-bottom:6px; font-size:0.82rem; color:#bae6fd;">
                        🔗 <strong>Correlated Link:</strong> {r}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("No multi-stage correlations detected.")

            st.markdown(f"""
                <h4 style="font-size:0.95rem; margin-top:18px; margin-bottom:8px; color:#cbd5e1;">Forensic Limitations &amp; Uncertainty</h4>
                <p style="font-size:0.8rem; color:#94a3b8; line-height:1.4; background:rgba(15,23,42,0.4); padding:10px 12px; border-radius:8px; border:1px solid rgba(255,255,255,0.05); margin:0;">
                    {summary['limitations']}
                </p>
            </div>
            """, unsafe_allow_html=True)

        with action_col:
            st.markdown("""
            <div class="glass-panel">
                <h4 style="margin: 0 0 14px 0; font-size: 1.05rem;">Telemetry Metrics</h4>
            """, unsafe_allow_html=True)

            for cat, cnt in summary["event_counts"].items():
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.05);">
                    <span style="font-size:0.85rem; color:#94a3b8;">{cat.upper()}</span>
                    <strong style="font-family:'JetBrains Mono', monospace; font-size:1.1rem; color:#ffffff;">{cnt}</strong>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("<h4 style='margin: 12px 0 10px 0; font-size: 1.05rem;'>Export Dossier</h4>", unsafe_allow_html=True)

            # TXT Format
            txt_report = (
                "=" * 76 + "\n"
                "TRACEBACK // CYBER INCIDENT INVESTIGATION REPORT\n"
                + "=" * 76 + "\n"
                f"Investigation ID : {summary['investigation_id']}\n"
                f"Generated At     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                f"Time Range       : {summary['time_range']}\n"
                f"Involved Hosts   : {', '.join(summary['involved_ips'])}\n\n"
                "EVENT BREAKDOWN:\n"
                + "\n".join(f"  - {k.upper()}: {v}" for k, v in summary["event_counts"].items())
                + "\n\nIDENTIFIED THREAT PATTERNS:\n"
                + ("\n".join(f"  [!] {p}" for p in summary["suspicious_patterns"]) if summary["suspicious_patterns"] else "  None detected")
                + "\n\nCORRELATION EXPLANATIONS:\n"
                + ("\n".join(f"  [*] {r}" for r in summary["correlation_reasons"]) if summary["correlation_reasons"] else "  None")
                + "\n\nCHRONOLOGICAL EVIDENCE SEQUENCE:\n"
                + "\n".join(summary["event_sequence"])
                + "\n\nINVESTIGATION LIMITATIONS:\n"
                + summary["limitations"]
                + "\n" + "=" * 76 + "\n"
            )

            # CSV Format
            subset_for_csv = (
                events if selected_target == "All"
                else [e for e in events if e.get("group_id") == selected_target]
            )
            csv_data = pd.DataFrame([{
                "timestamp": str(e["timestamp"]),
                "category": e["event_type"],
                "source_ip": e["source_ip"],
                "destination_ip": e.get("destination_ip", ""),
                "description": e["description"],
                "is_suspicious": e.get("is_suspicious", False),
                "group_id": e.get("group_id", ""),
                "correlation_notes": "; ".join(e.get("correlation_notes", [])),
            } for e in subset_for_csv])

            safe_slug = summary["investigation_id"].replace("/", "-")
            st.download_button(
                "📥 Download Forensic Report (TXT)",
                txt_report,
                file_name=f"traceback_report_{safe_slug}.txt",
                mime="text/plain",
                use_container_width=True
            )
            st.download_button(
                "📥 Export Telemetry Evidence (CSV)",
                csv_data.to_csv(index=False),
                file_name=f"traceback_evidence_{safe_slug}.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.markdown("</div>", unsafe_allow_html=True)
