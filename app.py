import streamlit as st
import plotly.graph_objects as go
import anthropic
import json

st.set_page_config(
    page_title="PUE Optimizer",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Styles ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
.stApp { background: #07090f; color: #e2e8f0; }
[data-testid="collapsedControl"] { display: none; }
.block-container { padding-top: 2.5rem !important; max-width: 860px; }

.page-header { text-align: center; margin-bottom: 2rem; }
.page-header h1 {
    font-size: 2rem; font-weight: 700; color: #f1f5f9;
    letter-spacing: -0.02em; margin: 0 0 4px 0;
}
.page-header p { color: #475569; font-size: 0.88rem; margin: 0; }

/* Table shell */
.tbl-shell {
    background: #0d1117;
    border: 1.5px solid #1e293b;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 1rem;
}
.tbl-head {
    display: grid; grid-template-columns: 1fr 160px 130px;
    background: #0f1923;
    border-bottom: 1.5px solid #1e293b;
    padding: 12px 18px;
}
.tbl-head span {
    font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.12em; color: #38bdf8;
}
.tbl-head span:not(:first-child) { text-align: right; }
.tbl-row { border-bottom: 1px solid #111827; }
.tbl-row:last-child { border-bottom: none; }

.row-label {
    display: flex; align-items: center; gap: 10px; padding: 4px 0;
}
.row-icon {
    width: 32px; height: 32px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.95rem; flex-shrink: 0;
}
.row-name { font-weight: 600; font-size: 0.88rem; color: #e2e8f0; }
.row-hint { font-size: 0.72rem; color: #3d5068; }
.unit-pill {
    font-size: 0.7rem; color: #38bdf8; font-family: 'IBM Plex Mono', monospace;
    font-weight: 600; padding: 3px 9px; background: #0c2240;
    border-radius: 5px; white-space: nowrap;
}

/* Override number input */
div[data-testid="stNumberInput"] { margin: 0 !important; }
div[data-testid="stNumberInput"] > label { display: none !important; }
div[data-testid="stNumberInput"] > div { margin: 0 !important; }
div[data-testid="stNumberInput"] input {
    background: #111827 !important;
    border: 1.5px solid #1e293b !important;
    border-radius: 7px !important;
    color: #f1f5f9 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.95rem !important; font-weight: 600 !important;
    padding: 8px 10px !important; text-align: right !important;
}
div[data-testid="stNumberInput"] input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.12) !important;
    outline: none !important;
}

/* Text input */
div[data-testid="stTextInput"] > label { display: none !important; }
div[data-testid="stTextInput"] input {
    background: #111827 !important; border: 1.5px solid #1e293b !important;
    border-radius: 8px !important; color: #64748b !important;
    font-family: 'IBM Plex Mono', monospace !important; font-size: 0.8rem !important;
    padding: 10px 14px !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.12) !important;
}

/* Generate button */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #0369a1 0%, #0ea5e9 100%);
    color: #fff; border: none; border-radius: 10px;
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 700; font-size: 1rem;
    letter-spacing: 0.06em; padding: 14px 0;
    text-transform: uppercase; transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%);
    transform: translateY(-2px); box-shadow: 0 8px 24px rgba(14,165,233,0.3);
}

/* Section divider */
.sdiv { border: none; border-top: 1px solid #111827; margin: 2rem 0 1.4rem; }
.stitle {
    font-size: 0.68rem; font-weight: 700; color: #38bdf8;
    text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 1rem;
}

/* KPI grid */
.kpi-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 1.2rem; }
.kpi-card {
    background: #0d1117; border: 1px solid #1e293b;
    border-radius: 10px; padding: 14px 14px; text-align: center;
}
.kpi-v {
    font-family: 'IBM Plex Mono', monospace; font-size: 1.55rem;
    font-weight: 600; line-height: 1; color: #38bdf8;
}
.kpi-l { font-size: 0.67rem; color: #3d5068; text-transform: uppercase;
          letter-spacing: 0.08em; margin-top: 5px; }
.kpi-s { font-size: 0.7rem; color: #475569; margin-top: 3px; }

/* Output table */
.otbl {
    width: 100%; border-collapse: collapse;
    border: 1.5px solid #1e293b; border-radius: 10px; overflow: hidden;
    background: #0d1117; margin-bottom: 1.2rem;
}
.otbl thead th {
    background: #0f1923; padding: 10px 16px;
    font-size: 0.67rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.1em; color: #38bdf8; border-bottom: 1.5px solid #1e293b;
}
.otbl tbody tr { border-bottom: 1px solid #111827; }
.otbl tbody tr:last-child { border-bottom: none; }
.otbl td { padding: 10px 16px; font-size: 0.86rem; color: #64748b; }
.otbl td:first-child { color: #cbd5e1; font-weight: 500; }
.otbl td.mn {
    font-family: 'IBM Plex Mono', monospace; font-weight: 600;
    color: #38bdf8; text-align: right;
}
.otbl tr.tot td { background: #0f1923; color: #f1f5f9; font-weight: 700; }
.otbl tr.tot td.mn { color: #22c55e; font-size: 1rem; }

/* Benchmark bars */
.bm { padding: 8px 0; border-bottom: 1px solid #0d1117; display: flex; align-items: center; gap: 12px; }
.bm:last-child { border-bottom: none; }
.bm-n { width: 180px; font-size: 0.82rem; color: #64748b; flex-shrink: 0; }
.bm-n.you { color: #f1f5f9; font-weight: 700; }
.bm-t { flex:1; background: #111827; border-radius: 4px; height: 7px; overflow: hidden; }
.bm-f { height: 100%; border-radius: 4px; }
.bm-v { width: 48px; text-align: right; font-family: 'IBM Plex Mono', monospace;
         font-size: 0.8rem; font-weight: 600; flex-shrink: 0; }

/* Live ranking table */
.rank-tbl { width:100%; border-collapse:collapse; margin-bottom:1.2rem; }
.rank-tbl thead th {
    background:#0f1923; padding:10px 14px;
    font-size:0.67rem; font-weight:700; text-transform:uppercase;
    letter-spacing:0.1em; color:#38bdf8;
    border-bottom:1.5px solid #1e293b;
}
.rank-tbl thead th:first-child { border-radius:10px 0 0 0; }
.rank-tbl thead th:last-child  { border-radius:0 10px 0 0; }
.rank-tbl tbody tr { border-bottom:1px solid #111827; transition: background 0.15s; }
.rank-tbl tbody tr:hover { background:#0f1923; }
.rank-tbl tbody tr:last-child { border-bottom:none; }
.rank-tbl td { padding:10px 14px; font-size:0.84rem; vertical-align:middle; }
.rank-tbl td.rank-num {
    font-family:'IBM Plex Mono',monospace; font-weight:700;
    font-size:1rem; text-align:center; width:48px;
}
.rank-tbl td.org-name { font-weight:600; color:#e2e8f0; }
.rank-tbl td.pue-val {
    font-family:'IBM Plex Mono',monospace; font-weight:700;
    font-size:0.95rem; text-align:right;
}
.rank-tbl td.pue-bar { width:160px; }
.rank-tbl td.src-tag { font-size:0.7rem; color:#3d5068; }
.rank-tbl tr.you-row td { background:#0a1e35 !important; }
.rank-tbl tr.you-row td.org-name { color:#38bdf8; }
.medal-1 { color:#fbbf24; }
.medal-2 { color:#94a3b8; }
.medal-3 { color:#b45309; }
.rank-badge {
    display:inline-block; padding:2px 8px; border-radius:5px;
    font-size:0.68rem; font-weight:700; text-transform:uppercase;
    letter-spacing:0.06em; margin-left:6px; vertical-align:middle;
}

/* ROI grid */
.roi-g { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; margin-bottom: 1.2rem; }
.roi-c {
    background: #0d1117; border: 1px solid #1e293b;
    border-radius: 9px; padding: 14px;
}
.roi-n { color: #38bdf8; font-size: 0.68rem; font-weight: 700;
          text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 10px; }
.roi-r { display: flex; justify-content: space-between; margin-bottom: 4px; }
.roi-k { color: #3d5068; font-size: 0.73rem; }
.roi-num { font-family: 'IBM Plex Mono', monospace; font-size: 0.76rem; font-weight: 600; }

/* AI report */
.ai-box {
    background: #0d1117; border: 1px solid #1e293b; border-radius: 10px;
    padding: 22px 24px; color: #cbd5e1; line-height: 1.8;
    font-size: 0.86rem; white-space: pre-wrap;
}

.disc {
    background: #0d1117; border: 1px solid #1e293b; border-radius: 8px;
    padding: 11px 15px; font-size: 0.74rem; color: #3d5068; margin-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)


# ─── Helpers ─────────────────────────────────────────────────────────────────
def compute(it, cool, loss, light):
    total = it + cool + loss + light
    return {"it": it, "cool": cool, "loss": loss, "light": light,
            "total": total, "pue": total / it}

def pue_col(p):
    if p <= 1.15: return "#22c55e"
    if p <= 1.30: return "#84cc16"
    if p <= 1.55: return "#eab308"
    if p <= 1.80: return "#f97316"
    return "#ef4444"

def pue_lbl(p):
    if p <= 1.15: return "World-class"
    if p <= 1.30: return "Efficient"
    if p <= 1.55: return "Average"
    if p <= 1.80: return "Inefficient"
    return "Critical"

# ─── Session defaults ─────────────────────────────────────────────────────────
for k, v in dict(it=500.0, cool=200.0, loss=60.0, light=10.0,
                 rate=0.08,
                 show=False, adone=False, arep="", alog=[]).items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─── Page header ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h1>⚡ PUE Optimizer</h1>
  <p>Data Center Power Usage Effectiveness — Calculator &amp; AI Advisor</p>
</div>""", unsafe_allow_html=True)


# ─── Preset buttons ───────────────────────────────────────────────────────────
pb1, pb2, pb3 = st.columns(3)
with pb1:
    if st.button("🔴  Inefficient  (≈2.0)", use_container_width=True):
        st.session_state.update(it=500.0, cool=400.0, loss=90.0, light=15.0, show=False, adone=False)
        st.rerun()
with pb2:
    if st.button("🟡  Standard  (≈1.5)", use_container_width=True):
        st.session_state.update(it=500.0, cool=200.0, loss=60.0, light=10.0, show=False, adone=False)
        st.rerun()
with pb3:
    if st.button("🟢  Hyperscale  (≈1.2)", use_container_width=True):
        st.session_state.update(it=500.0, cool=75.0, loss=25.0, light=2.5, show=False, adone=False)
        st.rerun()

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)


# ─── Input table ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="tbl-shell">
  <div class="tbl-head">
    <span>Energy Category</span>
    <span>Power (kW)</span>
    <span>Type</span>
  </div>
</div>""", unsafe_allow_html=True)

ROWS = [
    ("it",    "#1a2e45", "🖥️", "IT Equipment",    "Servers, storage, networking",         "Required"),
    ("cool",  "#162914", "❄️", "Cooling",           "CRAC, chillers, cooling towers",       "kW"),
    ("loss",  "#1e1535", "⚡", "Power Loss",        "UPS losses, PDUs, distribution",       "kW"),
    ("light", "#141a30", "💡", "Lighting & Misc",   "Lighting, security, other overhead",   "Optional"),
]

for key, bg, ico, name, hint, badge in ROWS:
    col_lbl, col_inp, col_badge = st.columns([11, 5, 4])
    with col_lbl:
        st.markdown(f"""
        <div class="row-label" style="padding:5px 0 5px 6px;">
          <div class="row-icon" style="background:{bg}">{ico}</div>
          <div>
            <div class="row-name">{name}</div>
            <div class="row-hint">{hint}</div>
          </div>
        </div>""", unsafe_allow_html=True)
    with col_inp:
        st.number_input("_", key=key, min_value=0.0, max_value=500_000.0,
                        step=10.0, label_visibility="collapsed")
    with col_badge:
        st.markdown(f"<div style='padding:10px 4px 10px 0;text-align:right;'>"
                    f"<span class='unit-pill'>{badge}</span></div>", unsafe_allow_html=True)
    st.markdown("<div style='border-top:1px solid #111827;margin:0 8px;'></div>",
                unsafe_allow_html=True)

# Rate + API key rows
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
r1, r2 = st.columns([3,1])
with r1:
    st.markdown("<div style='color:#3d5068;font-size:0.78rem;padding-top:10px;'>"
                "💲 Electricity rate ($/kWh) — for cost estimates</div>", unsafe_allow_html=True)
with r2:
    st.number_input("_r", key="rate", min_value=0.01, max_value=5.0,
                    step=0.01, format="%.3f", label_visibility="collapsed")

# ─── GENERATE button ──────────────────────────────────────────────────────────
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
if st.button("⚡  GENERATE THE REPORT", use_container_width=True, type="primary"):
    st.session_state.show  = True
    st.session_state.adone = False
    st.session_state.arep  = ""
    st.session_state.alog  = []


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.show:
    st.markdown("""
    <div style="text-align:center;padding:50px 0 20px;color:#1e293b;font-size:0.85rem;">
        Fill in the table above and click <b style="color:#38bdf8;">Generate the Report</b>
    </div>""", unsafe_allow_html=True)
    st.stop()

r = compute(st.session_state.it, st.session_state.cool,
            st.session_state.loss, st.session_state.light)
pue  = r["pue"]
pc   = pue_col(pue)
plbl = pue_lbl(pue)
rate = st.session_state.rate


# ── 1. KPI Bar ────────────────────────────────────────────────────────────────
st.markdown("<hr class='sdiv'>", unsafe_allow_html=True)
st.markdown("<div class='stitle'>📊 Results</div>", unsafe_allow_html=True)

ovh  = r["total"] - r["it"]
wgoo = max(0, (pue - 1.09) * r["it"])
aec  = wgoo * 8760 * rate

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card" style="border-color:{pc}50">
    <div class="kpi-v" style="color:{pc}">{pue:.3f}</div>
    <div class="kpi-l">PUE</div>
    <div class="kpi-s">{plbl}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-v">{r['total']:,.0f}</div>
    <div class="kpi-l">Total Facility kW</div>
    <div class="kpi-s">{r['total']*24/1000:,.1f} MWh/day</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-v" style="color:#f97316">{ovh:,.0f}</div>
    <div class="kpi-l">Overhead kW</div>
    <div class="kpi-s">{ovh/r['total']*100:.1f}% of total</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-v" style="color:#ef4444">${aec:,.0f}</div>
    <div class="kpi-l">Excess Cost/yr</div>
    <div class="kpi-s">vs Google 1.09</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── 2. Power Breakdown Table ──────────────────────────────────────────────────
ann = lambda kw: kw * 8760 * rate
rows_data = [
    ("🖥️ IT Equipment",  r["it"],    r["it"]/r["total"]*100,    "#38bdf8"),
    ("❄️ Cooling",        r["cool"],  r["cool"]/r["total"]*100,  "#0ea5e9"),
    ("⚡ Power Loss",     r["loss"],  r["loss"]/r["total"]*100,  "#7c3aed"),
    ("💡 Lighting/Misc",  r["light"], r["light"]/r["total"]*100, "#475569"),
]
body = ""
for nm, kw, pct, c in rows_data:
    body += f"<tr><td>{nm}</td><td class='mn' style='color:{c}'>{kw:,.0f}</td>" \
            f"<td class='mn' style='color:#3d5068;font-size:.76rem'>{pct:.1f}%</td>" \
            f"<td class='mn' style='color:#3d5068;font-size:.76rem'>${ann(kw):,.0f}</td></tr>"
body += f"<tr class='tot'><td>⚡ Total Facility</td>" \
        f"<td class='mn'>{r['total']:,.0f}</td>" \
        f"<td class='mn'>PUE {pue:.3f}</td>" \
        f"<td class='mn'>${ann(r['total']):,.0f}</td></tr>"

st.markdown(f"""
<table class="otbl">
  <thead><tr>
    <th>Category</th><th style="text-align:right">kW</th>
    <th style="text-align:right">% Total</th>
    <th style="text-align:right">Annual Cost</th>
  </tr></thead>
  <tbody>{body}</tbody>
</table>""", unsafe_allow_html=True)

# Donut chart
pie = go.Figure(go.Pie(
    labels=["IT Equipment","Cooling","Power Loss","Lighting/Misc"],
    values=[r["it"], r["cool"], r["loss"], r["light"]],
    hole=0.60,
    marker=dict(colors=["#38bdf8","#0ea5e9","#7c3aed","#475569"],
                line=dict(color="#07090f", width=2)),
    textfont=dict(family="IBM Plex Sans", color="#e2e8f0", size=12),
    hovertemplate="<b>%{label}</b><br>%{value:,.0f} kW (%{percent})<extra></extra>",
))
pie.add_annotation(text=f"PUE<br><b>{pue:.3f}</b>", x=0.5, y=0.5, showarrow=False,
                   font=dict(color=pc, family="IBM Plex Mono", size=17))
pie.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#64748b", family="IBM Plex Sans"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
    margin=dict(t=8,b=8,l=8,r=8), height=240,
)
st.plotly_chart(pie, use_container_width=True)


# ── 3. Benchmark ──────────────────────────────────────────────────────────────
st.markdown("<hr class='sdiv'>", unsafe_allow_html=True)
st.markdown("<div class='stitle'>🏆 Industry Benchmark</div>", unsafe_allow_html=True)

BMS = [
    ("Meta (2024)",        1.08, "#22c55e", False),
    ("Google (TTM)",       1.09, "#22c55e", False),
    ("Hyperscale target",  1.20, "#84cc16", False),
    (f"Your Facility ⭐",  pue,  pc,        True),
    ("Industry Average",   1.56, "#f97316", False),
    ("Inefficient tier",   2.00, "#ef4444", False),
]
bm_html = ""
for nm, val, c, is_you in sorted(BMS, key=lambda x: x[1]):
    w = min(100, (val - 1.0) / 1.1 * 100)
    yo = "you" if is_you else ""
    bm_html += f"""<div class="bm">
      <div class="bm-n {yo}">{nm}</div>
      <div class="bm-t"><div class="bm-f" style="width:{w:.0f}%;background:{c}"></div></div>
      <div class="bm-v" style="color:{c}">{val:.2f}</div>
    </div>"""

st.markdown(f"""<div style="background:#0d1117;border:1.5px solid #1e293b;
border-radius:10px;padding:14px 18px;">{bm_html}</div>""", unsafe_allow_html=True)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
gc1, gc2, gc3 = st.columns(3)
for col_, (ref, rv2) in zip([gc1,gc2,gc3],
    [("Hyperscale 1.20",1.20),("Google 1.09",1.09),("Meta 1.08",1.08)]):
    d = pue - rv2
    ck2 = "#22c55e" if d <= 0 else "#f97316"
    sv = abs(d) * r["it"]
    with col_:
        st.markdown(f"""
        <div style="background:#0d1117;border:1px solid #1e293b;border-radius:9px;
                    padding:12px 14px;text-align:center;">
          <div style="font-size:0.68rem;color:#3d5068;margin-bottom:5px;">{ref}</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:1.05rem;
                      color:{ck2};font-weight:700;">{'✅ Beat it!' if d<=0 else f'−{d:.3f} PUE'}</div>
          {'<div style="font-size:0.7rem;color:#475569;margin-top:3px;">save ' + f'{sv:,.0f} kW · ${sv*8760*rate:,.0f}/yr</div>' if d > 0 else ''}
        </div>""", unsafe_allow_html=True)


# ── 3.5 Live Global Ranking ───────────────────────────────────────────────────
st.markdown("<hr class='sdiv'>", unsafe_allow_html=True)
st.markdown("<div class='stitle'>🌍 Global Ranking — Your Facility vs Real Organizations</div>",
            unsafe_allow_html=True)

# ── Verified baseline from public reports ─────────────────────────────────────
# Sources:
#   Google: Google 2025 Environmental Report (2024 FY data) + datacenters.google/efficiency
#   Meta: Meta 2024 Sustainability Report
#   AWS: AWS 2024 Sustainability Report  
#   Microsoft: Microsoft 2024 Environmental Sustainability Report
#   Equinix: Equinix 2024 Impact Report
#   Others: Uptime Institute 2024 / 2025 surveys + individual sustainability reports
VERIFIED_BASELINE = [
    {"org": "Google",             "pue": 1.09, "year": "2024", "tier": "Hyperscale",
     "source": "Google 2025 Environmental Report (FY2024)"},
    {"org": "Meta",               "pue": 1.08, "year": "2024", "tier": "Hyperscale",
     "source": "Meta 2024 Sustainability Report"},
    {"org": "Amazon AWS",         "pue": 1.15, "year": "2024", "tier": "Hyperscale",
     "source": "AWS 2024 Sustainability Report"},
    {"org": "Microsoft Azure",    "pue": 1.16, "year": "2024", "tier": "Hyperscale",
     "source": "Microsoft 2024 Environmental Sustainability Report"},
    {"org": "Equinix",            "pue": 1.39, "year": "2024", "tier": "Colocation",
     "source": "Equinix 2024 Impact Report"},
    {"org": "Iron Mountain",      "pue": 1.41, "year": "2024", "tier": "Colocation",
     "source": "Iron Mountain Data Centers Sustainability Report 2024"},
    {"org": "CyrusOne",           "pue": 1.46, "year": "2024", "tier": "Colocation",
     "source": "CyrusOne 2025 Sustainability Report"},
    {"org": "DataBank",           "pue": 1.54, "year": "2024", "tier": "Enterprise",
     "source": "DataBank 2024 Corporate Responsibility Report"},
    {"org": "Digital Realty",     "pue": 1.58, "year": "2024", "tier": "Colocation",
     "source": "Digital Realty 2024 Impact Report"},
    {"org": "Industry Average",   "pue": 1.56, "year": "2024", "tier": "Benchmark",
     "source": "Uptime Institute 2024 Global Data Center Survey"},
]

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_live_pue_rankings(user_pue: float, api_key: str):
    """
    Uses Claude with web_search to find any newer PUE data published after our
    baseline, then merges with the verified baseline and adds the user's facility.
    """
    client = anthropic.Anthropic(api_key=api_key)

    baseline_json = json.dumps(VERIFIED_BASELINE, indent=2)

    prompt = f"""You have a verified baseline of data center PUE figures from official sustainability reports:

{baseline_json}

Use web search to check if any of these organizations have published MORE RECENT PUE data 
(2025 reports covering FY2024 or FY2025) that would update the baseline. Also search for 
any other major data center operators (Apple, Oracle, NTT, OVHcloud, Alibaba Cloud, etc.) 
with recently published verified PUE figures.

Return ONLY a JSON array of all organizations (updated baseline + any new ones you found).
Use this exact format, no markdown, no explanation:
[
  {{"org": "Google", "pue": 1.09, "year": "2024", "tier": "Hyperscale", "source": "Google 2025 Environmental Report (FY2024)"}},
  ...
]

Rules:
- Keep all baseline entries unless you found a more recent verified number
- Only add new orgs if you found a clearly sourced PUE figure from an official report
- Do NOT include the user's facility — that will be added separately
- Tiers: Hyperscale | Colocation | Enterprise | Benchmark
- Return ONLY the JSON array"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )

    full_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            full_text += block.text

    import re
    json_match = re.search(r'\[.*\]', full_text, re.DOTALL)
    if json_match:
        try:
            fetched = json.loads(json_match.group())
            # Merge: fetched entries override baseline by org name
            merged = {d["org"]: d for d in VERIFIED_BASELINE}
            for d in fetched:
                if d.get("org") and d.get("pue"):
                    merged[d["org"]] = d
            data = list(merged.values())
        except Exception:
            data = VERIFIED_BASELINE.copy()
    else:
        data = VERIFIED_BASELINE.copy()

    # Add user
    data.append({"org": "Your Facility", "pue": user_pue,
                 "year": "Now", "tier": "User", "source": "User Input"})

    return sorted(data, key=lambda x: float(x.get("pue", 9)))


def pue_tier_color(tier, org):
    if org == "Your Facility": return "#38bdf8"
    if tier == "Hyperscale":   return "#22c55e"
    if tier == "Colocation":   return "#84cc16"
    if tier == "Enterprise":   return "#eab308"
    if tier == "Benchmark":    return "#f97316"
    return "#64748b"

def rank_medal(i):
    if i == 0: return "🥇", "medal-1"
    if i == 1: return "🥈", "medal-2"
    if i == 2: return "🥉", "medal-3"
    return f"#{i+1}", ""


live_api = st.secrets.get("ANTHROPIC_API_KEY", "")

if not live_api:
    # Show static baseline table without web search
    st.markdown("""
    <div style="background:#0a1528;border:1px solid #1e293b;border-radius:8px;
                padding:8px 14px;margin-bottom:12px;font-size:0.75rem;color:#475569;">
        📊 Showing verified baseline from official sustainability reports.
        Add API key to Streamlit secrets to enable live web-search updates.
    </div>""", unsafe_allow_html=True)
    rankings = VERIFIED_BASELINE.copy()
    rankings.append({"org": "Your Facility", "pue": pue, "year": "Now",
                     "tier": "User", "source": "User Input"})
    rankings = sorted(rankings, key=lambda x: float(x.get("pue", 9)))
else:
    cache_pue = round(pue, 2)
    with st.spinner("🌐 Checking for latest PUE data via web search..."):
        try:
            rankings = fetch_live_pue_rankings(cache_pue, live_api)
        except Exception as e:
            st.warning(f"Web search unavailable, using verified baseline: {e}")
            rankings = VERIFIED_BASELINE.copy()
            rankings.append({"org": "Your Facility", "pue": pue, "year": "Now",
                             "tier": "User", "source": "User Input"})
            rankings = sorted(rankings, key=lambda x: float(x.get("pue", 9)))

if rankings:
    user_rank = next((i for i, d in enumerate(rankings)
                      if d.get("org") == "Your Facility"), None)
    total = len(rankings)

    # Rank banner
    if user_rank is not None:
        pct       = round((total - user_rank) / total * 100)
        banner_c  = "#22c55e" if pct >= 60 else "#eab308" if pct >= 30 else "#ef4444"
        medal_sym, _ = rank_medal(user_rank)
        google_pue = next((d["pue"] for d in rankings if d["org"] == "Google"), 1.09)
        gap_to_google = round(pue - google_pue, 3)

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0a1e35,#0d2640);
                    border:2px solid {banner_c};border-radius:12px;
                    padding:18px 24px;margin-bottom:1.2rem;">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
            <div>
              <div style="font-size:0.68rem;color:#3d5068;text-transform:uppercase;
                          letter-spacing:0.1em;margin-bottom:4px;">Your Global Rank</div>
              <div style="font-size:2rem;font-weight:700;color:{banner_c};
                          font-family:'IBM Plex Mono',monospace;">
                {medal_sym} #{user_rank+1}
                <span style="font-size:1rem;color:#475569;font-weight:400;">of {total} organizations</span>
              </div>
              <div style="font-size:0.78rem;color:#475569;margin-top:4px;">
                Better than <b style="color:{banner_c};">{pct}%</b> of benchmarked facilities
              </div>
            </div>
            <div style="display:flex;gap:20px;flex-wrap:wrap;">
              <div style="text-align:center;">
                <div style="font-size:0.68rem;color:#3d5068;margin-bottom:3px;">Your PUE</div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:1.8rem;
                            font-weight:700;color:{banner_c};">{pue:.3f}</div>
              </div>
              <div style="text-align:center;">
                <div style="font-size:0.68rem;color:#3d5068;margin-bottom:3px;">Gap to Google</div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:1.8rem;
                            font-weight:700;color:{'#22c55e' if gap_to_google<=0 else '#f97316'};">
                  {'✅' if gap_to_google<=0 else f'+{gap_to_google:.3f}'}
                </div>
              </div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    # Leaderboard
    max_pue_shown = max(float(d.get("pue", 2)) for d in rankings)
    tbl_rows = ""
    for i, d in enumerate(rankings):
        org    = d.get("org", "Unknown")
        dpue   = float(d.get("pue", 0))
        year   = d.get("year", "")
        source = d.get("source", "")
        tier   = d.get("tier", "")
        is_you = org == "Your Facility"
        is_bm  = tier == "Benchmark"

        color     = pue_tier_color(tier, org)
        bar_w     = min(100, (dpue - 1.0) / (max_pue_shown - 1.0 + 0.01) * 100)
        sym, mcls = rank_medal(i)
        you_cls   = "you-row" if is_you else ""

        tier_label = "⭐ You" if is_you else ("📊 Avg" if is_bm else tier)
        tier_badge = (f"<span class='rank-badge' style='background:{color}22;color:{color};'>"
                      f"{tier_label}</span>")

        src_display = source[:38] + "…" if len(source) > 38 else source

        tbl_rows += f"""
        <tr class="{you_cls}">
          <td class="rank-num {mcls}">{sym}</td>
          <td class="org-name">{org} {tier_badge}</td>
          <td class="pue-bar">
            <div style="background:#111827;border-radius:3px;height:6px;overflow:hidden;">
              <div style="width:{bar_w:.0f}%;height:100%;background:{color};border-radius:3px;"></div>
            </div>
          </td>
          <td class="pue-val" style="color:{color}">{dpue:.2f}</td>
          <td class="src-tag">{year}<br>
            <span title="{source}" style="cursor:help;color:#334155">{src_display}</span>
          </td>
        </tr>"""

    st.markdown(f"""
    <div style="background:#0d1117;border:1.5px solid #1e293b;border-radius:10px;overflow:hidden;">
      <table class="rank-tbl">
        <thead><tr>
          <th style="text-align:center;width:52px">Rank</th>
          <th>Organization</th>
          <th style="width:140px">Efficiency</th>
          <th style="text-align:right;width:60px">PUE</th>
          <th>Source</th>
        </tr></thead>
        <tbody>{tbl_rows}</tbody>
      </table>
    </div>""", unsafe_allow_html=True)

    # Legend + source note
    st.markdown("""
    <div style="display:flex;gap:16px;flex-wrap:wrap;margin-top:10px;margin-bottom:4px;">
      <span style="font-size:0.72rem;color:#3d5068;">
        <span style="color:#22c55e">■</span> Hyperscale &nbsp;
        <span style="color:#84cc16">■</span> Colocation &nbsp;
        <span style="color:#eab308">■</span> Enterprise &nbsp;
        <span style="color:#f97316">■</span> Industry Avg &nbsp;
        <span style="color:#38bdf8">■</span> Your Facility
      </span>
    </div>
    <div style="font-size:0.71rem;color:#334155;margin-bottom:0.5rem;">
      📄 Baseline sourced from official sustainability reports incl. 
      <b style="color:#475569;">Google 2025 Environmental Report (FY2024)</b>, 
      Meta 2024, AWS 2024, Microsoft 2024, Equinix 2024, Uptime Institute 2024 Survey.
      Live updates via web search refresh hourly.
    </div>""", unsafe_allow_html=True)


# ── 4. Scenarios ──────────────────────────────────────────────────────────────
st.markdown("<hr class='sdiv'>", unsafe_allow_html=True)
st.markdown("<div class='stitle'>🔀 Scenario Comparison</div>", unsafe_allow_html=True)

sc_data = {
    "Your Facility": (r["cool"], r["loss"], r["light"], "#38bdf8"),
    "Inefficient":   (r["it"]*.80, r["it"]*.18, r["it"]*.03, "#ef4444"),
    "Standard":      (r["it"]*.38, r["it"]*.12, r["it"]*.02, "#eab308"),
    "Hyperscale":    (r["it"]*.13, r["it"]*.04, r["it"]*.005,"#22c55e"),
}
sc_names, sc_pues, sc_colors = [], [], []
for sn, (ck2,lk,lgk,sc2) in sc_data.items():
    sp = compute(r["it"], ck2, lk, lgk)["pue"]
    sc_names.append(sn); sc_pues.append(sp); sc_colors.append(sc2)

bar = go.Figure(go.Bar(
    x=sc_names, y=sc_pues, marker_color=sc_colors,
    text=[f"{v:.2f}" for v in sc_pues], textposition="outside",
    textfont=dict(family="IBM Plex Mono", color="#e2e8f0", size=13),
    hovertemplate="<b>%{x}</b><br>PUE: %{y:.3f}<extra></extra>",
))
bar.add_hline(y=1.56, line_dash="dash", line_color="#f97316", annotation_text="Industry avg 1.56")
bar.add_hline(y=1.09, line_dash="dot",  line_color="#22c55e", annotation_text="Google 1.09")
bar.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#64748b", family="IBM Plex Sans"),
    yaxis=dict(gridcolor="#111827", title="PUE", range=[0.9, 2.4]),
    xaxis=dict(tickfont=dict(size=12)),
    height=290, margin=dict(t=28,b=8), showlegend=False,
)
st.plotly_chart(bar, use_container_width=True)


# ── 5. AI Agent ───────────────────────────────────────────────────────────────
st.markdown("<hr class='sdiv'>", unsafe_allow_html=True)
st.markdown("<div class='stitle'>🤖 AI Agent — Recommendations & Predictions</div>",
            unsafe_allow_html=True)

AGENT_TOOLS = [
    {
        "name": "analyze_cooling_efficiency",
        "description": "Analyzes cooling kW vs IT load, returns severity, gap vs hyperscale benchmark, saveable kW, and ranked interventions.",
        "input_schema": {"type":"object","properties":{
            "cooling_kw":{"type":"number"},"it_kw":{"type":"number"}},
            "required":["cooling_kw","it_kw"]},
    },
    {
        "name": "analyze_power_losses",
        "description": "Analyzes UPS/distribution losses vs IT load, returns severity and remediations with PUE deltas.",
        "input_schema": {"type":"object","properties":{
            "losses_kw":{"type":"number"},"it_kw":{"type":"number"}},
            "required":["losses_kw","it_kw"]},
    },
    {
        "name": "benchmark_against_hyperscalers",
        "description": "Compares current PUE to Google (1.09), Meta (1.08), hyperscale (1.20), industry avg (1.56). Returns gap analysis.",
        "input_schema": {"type":"object","properties":{
            "current_pue":{"type":"number"},"it_kw":{"type":"number"},"total_kw":{"type":"number"}},
            "required":["current_pue","it_kw","total_kw"]},
    },
    {
        "name": "estimate_improvement_roi",
        "description": "Estimates kW saved, annual $ savings, CO2 avoided for a proposed PUE improvement.",
        "input_schema": {"type":"object","properties":{
            "improvement_name":{"type":"string"},"current_pue":{"type":"number"},
            "projected_pue":{"type":"number"},"it_kw":{"type":"number"},
            "electricity_rate_usd":{"type":"number"}},
            "required":["improvement_name","current_pue","projected_pue","it_kw","electricity_rate_usd"]},
    },
    {
        "name": "generate_improvement_roadmap",
        "description": "Synthesises analysis into a prioritised roadmap with quick wins, medium-term projects, and long-term strategy.",
        "input_schema": {"type":"object","properties":{
            "current_pue":{"type":"number"},"cooling_severity":{"type":"string"},
            "power_severity":{"type":"string"},"top_roi_improvement":{"type":"string"},
            "it_kw":{"type":"number"}},
            "required":["current_pue","cooling_severity","power_severity","top_roi_improvement","it_kw"]},
    },
]

def exec_tool(name, inp):
    if name == "analyze_cooling_efficiency":
        ckw, ikw = inp["cooling_kw"], inp["it_kw"]
        cp = ckw / ikw * 100
        sev = "CRITICAL" if cp>50 else "HIGH" if cp>25 else "MEDIUM" if cp>12 else "LOW"
        gap = max(0, cp - 12)
        iv = []
        if cp>15: iv.append({"action":"Hot/Cold Aisle Containment","pue_delta":round(ikw*gap/100*.25/ikw,3),"effort":"Medium","timeline":"3-6 months"})
        if cp>20: iv.append({"action":"Raise supply air temp to 27°C (ASHRAE A2)","pue_delta":round(ckw*.06/ikw,3),"effort":"Low","timeline":"1-4 weeks"})
        if cp>35: iv.append({"action":"Air/water-side free cooling economizer","pue_delta":round(ckw*.30/ikw,3),"effort":"High","timeline":"12-24 months"})
        if cp>25: iv.append({"action":"Variable speed drives on CRAC/CRAH fans","pue_delta":round(ckw*.10/ikw,3),"effort":"Low-Medium","timeline":"1-3 months"})
        return {"severity":sev,"cooling_pct_of_it":round(cp,1),"hyperscale_benchmark_pct":12,
                "gap_pct":round(gap,1),"saveable_kw":round(ikw*gap/100,1),"interventions":iv}

    if name == "analyze_power_losses":
        lkw, ikw = inp["losses_kw"], inp["it_kw"]
        lp = lkw / ikw * 100
        sev = "CRITICAL" if lp>18 else "HIGH" if lp>10 else "MEDIUM" if lp>5 else "LOW"
        sv = ikw * max(0, lp-4) / 100
        iv = []
        if lp>8:  iv.append({"action":"High-efficiency UPS replacement (97-99%)","pue_delta":round(ikw*(lp-5)/100*.6/ikw,3),"effort":"High","timeline":"6-18 months"})
        if lp>6:  iv.append({"action":"Enable UPS ECO mode","pue_delta":round(lkw*.03/ikw,3),"effort":"Low","timeline":"Days"})
        if lp>10: iv.append({"action":"Upgrade to 480V power distribution","pue_delta":round(lkw*.08/ikw,3),"effort":"High","timeline":"12-24 months"})
        return {"severity":sev,"losses_pct_of_it":round(lp,1),"best_practice_pct":4,
                "saveable_kw":round(sv,1),"interventions":iv}

    if name == "benchmark_against_hyperscalers":
        cur, ikw, tkw = inp["current_pue"], inp["it_kw"], inp["total_kw"]
        refs = {"Meta (2024)":1.08,"Google (TTM)":1.09,"Hyperscale target":1.20,"Industry average":1.56}
        gaps = {k: round(cur-v,3) for k,v in refs.items()}
        wasted = round((cur-1.09)*ikw,1)
        pctile = "bottom 20%" if cur>1.8 else "bottom 40%" if cur>1.56 else "average" if cur>1.35 else "top 25%" if cur>1.20 else "top 10%" if cur>1.12 else "top 2%"
        return {"current_pue":cur,"percentile":pctile,"gaps_to_refs":gaps,
                "wasted_kw_vs_google":wasted,
                "wasted_gwh_per_year":round(max(0,wasted)*8760/1e6,2),
                "what_leaders_do":["Full containment + liquid/immersion cooling",
                                   "AI-driven cooling control (DeepMind: −40%)",
                                   "Custom 99%+ efficient power hardware",
                                   "On-site renewables / 24/7 carbon-free energy"]}

    if name == "estimate_improvement_roi":
        cur, proj = inp["current_pue"], inp["projected_pue"]
        ikw, rt = inp["it_kw"], inp["electricity_rate_usd"]
        sv = (cur-proj)*ikw
        return {"improvement":inp["improvement_name"],"pue_before":cur,"pue_after":proj,
                "pue_improvement":round(cur-proj,3),"power_saved_kw":round(sv,1),
                "annual_savings_usd":round(sv*8760*rt,0),
                "co2_tonnes_per_year":round(sv*8760*.386/1000,1)}

    if name == "generate_improvement_roadmap":
        cur, cs, ps, top, ikw = inp["current_pue"],inp["cooling_severity"],inp["power_severity"],inp["top_roi_improvement"],inp["it_kw"]
        qw = ["Enable UPS ECO mode (today, near-zero cost)",
              "Install blanking panels in empty rack units (<$500)",
              "Raise CRAC supply air temp setpoint +2°C (1 week)"]
        mt = []
        if cs in("HIGH","CRITICAL"): mt.append("Full hot/cold aisle containment (3-6 months, $50-150k)")
        if ps in("HIGH","CRITICAL"): mt.append("UPS replacement with high-efficiency units (6-12 months)")
        mt += ["Variable speed drives on all CRAC fans","Deploy DCIM for continuous PUE monitoring"]
        lt = ["Air/water-side economizer evaluation","Direct liquid cooling for GPU/AI workloads",
              "AI-driven cooling automation","On-site renewables or 24/7 CFE PPA"]
        return {"summary":f"Cooling {cs}, power losses {ps}. Top ROI action: {top}.",
                "quick_wins_48h":qw,"medium_term_projects":mt,"long_term_strategic":lt,
                "target_pue_18months":round(max(1.08,cur-0.45),2),"stretch_3yr":1.15}

    return {"error": f"Unknown tool: {name}"}


def run_agent(fac, api_key, rt):
    client = anthropic.Anthropic(api_key=api_key)
    system = """You are a world-class data center efficiency consultant AI agent.

MANDATORY SEQUENCE:
1. First turn: call analyze_cooling_efficiency AND analyze_power_losses.
2. Second turn: call benchmark_against_hyperscalers.
3. Third turn: call estimate_improvement_roi for TOP 2 improvements (use projected_pue = current_pue - estimated pue_delta from tool results).
4. Fourth turn: call generate_improvement_roadmap.
5. Final turn: write the expert report — NO more tool calls.

Final report format:
🔍 Executive Summary (3-4 sentences, data-driven)
📊 Key Findings (bullets with exact numbers from tools)
🏆 Top 3 Prioritized Actions (numbered, with PUE delta + $ savings)
⚡ Quick Wins — Start Today
🗺️ 18-Month Roadmap
📌 Peer Comparison vs Google & Meta (specific gap numbers)"""

    user_msg = f"""Analyze this data center and produce a full improvement plan:

IT Load: {fac['it']:,.0f} kW
Cooling: {fac['cool']:,.0f} kW ({fac['cool']/fac['it']*100:.1f}% of IT)
Power Losses: {fac['loss']:,.0f} kW ({fac['loss']/fac['it']*100:.1f}% of IT)
Lighting/Misc: {fac['light']:,.0f} kW
PUE: {fac['pue']:.3f}
Total: {fac['total']:,.0f} kW
Electricity rate: ${rt}/kWh"""

    messages = [{"role":"user","content":user_msg}]
    tool_log = []

    for _ in range(15):
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system, tools=AGENT_TOOLS, messages=messages,
        )
        text_out = ""
        tool_uses = []
        for blk in resp.content:
            if blk.type == "text": text_out += blk.text
            elif blk.type == "tool_use": tool_uses.append(blk)
        messages.append({"role":"assistant","content":resp.content})
        if resp.stop_reason == "end_turn" or not tool_uses:
            return text_out, tool_log
        results = []
        for tu in tool_uses:
            res = exec_tool(tu.name, tu.input)
            tool_log.append({"tool":tu.name,"input":tu.input,"result":res})
            results.append({"type":"tool_result","tool_use_id":tu.id,"content":json.dumps(res)})
        messages.append({"role":"user","content":results})

    return "Agent reached max iterations.", tool_log


# ── Run or display ────────────────────────────────────────────────────────────
api = st.secrets.get("ANTHROPIC_API_KEY", "")

if not api:
    st.markdown("""
    <div style="background:#0d1117;border:1px dashed #1e293b;border-radius:10px;
                padding:30px;text-align:center;">
      <div style="font-size:1.4rem;margin-bottom:8px;">⚙️</div>
      <div style="color:#475569;font-size:0.84rem;">
        AI recommendations are not configured yet.<br>
        <span style="color:#3d5068;font-size:0.78rem;">
          (App owner: add <b style="color:#38bdf8;">ANTHROPIC_API_KEY</b> in Streamlit Cloud → App Settings → Secrets)
        </span>
      </div>
    </div>""", unsafe_allow_html=True)
else:
    if not st.session_state.adone:
        fac = {"it":r["it"],"cool":r["cool"],"loss":r["loss"],
               "light":r["light"],"pue":pue,"total":r["total"]}
        status = st.empty()
        status.info("🤖 Agent running — calling analysis tools...")
        try:
            with st.spinner(""):
                rep, log = run_agent(fac, api, rate)
            st.session_state.arep  = rep
            st.session_state.alog  = log
            st.session_state.adone = True
            status.empty()
            st.rerun()
        except anthropic.AuthenticationError:
            status.empty()
            st.error("❌ Invalid API key — please check and try again.")
        except Exception as ex:
            status.empty()
            st.error(f"❌ Agent error: {ex}")

    if st.session_state.adone:
        log = st.session_state.alog
        rep = st.session_state.arep

        # Tool trace
        TICONS = {
            "analyze_cooling_efficiency":"🌡️","analyze_power_losses":"⚡",
            "benchmark_against_hyperscalers":"🏆","estimate_improvement_roi":"💰",
            "generate_improvement_roadmap":"🗺️",
        }
        if log:
            with st.expander(f"🔬 Agent Tool Call Trace ({len(log)} calls)", expanded=False):
                for i, call in enumerate(log, 1):
                    ico = TICONS.get(call["tool"],"🔧")
                    with st.expander(f"{ico} Call {i}: `{call['tool']}`"):
                        ci, co = st.columns(2)
                        with ci:
                            st.markdown("**Input**"); st.json(call["input"])
                        with co:
                            st.markdown("**Result**"); st.json(call["result"])

        # ROI cards
        roi_calls = [c for c in log if c["tool"] == "estimate_improvement_roi"]
        if roi_calls:
            st.markdown("<div class='stitle' style='margin-top:10px'>💰 ROI Summary</div>",
                        unsafe_allow_html=True)
            rhtml = "<div class='roi-g'>"
            for call in roi_calls[:3]:
                rv3 = call["result"]
                rhtml += f"""
                <div class="roi-c">
                  <div class="roi-n">{rv3.get('improvement','')}</div>
                  <div class="roi-r"><span class="roi-k">PUE gain</span>
                    <span class="roi-num" style="color:#22c55e">−{rv3.get('pue_improvement',0):.3f}</span></div>
                  <div class="roi-r"><span class="roi-k">Power saved</span>
                    <span class="roi-num" style="color:#38bdf8">{rv3.get('power_saved_kw',0):,.0f} kW</span></div>
                  <div class="roi-r"><span class="roi-k">Annual savings</span>
                    <span class="roi-num" style="color:#84cc16">${rv3.get('annual_savings_usd',0):,.0f}</span></div>
                  <div class="roi-r"><span class="roi-k">CO₂ avoided</span>
                    <span class="roi-num" style="color:#22d3ee">{rv3.get('co2_tonnes_per_year',0):,.0f} t/yr</span></div>
                </div>"""
            rhtml += "</div>"
            st.markdown(rhtml, unsafe_allow_html=True)

        # Full report
        st.markdown("<div class='stitle' style='margin-top:10px'>📋 Full Agent Report</div>",
                    unsafe_allow_html=True)
        st.markdown(f"<div class='ai-box'>{rep}</div>", unsafe_allow_html=True)

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="disc">
  ⚠️ <b>Disclaimer:</b> All recommendations are heuristic estimates based on industry benchmarks.
  Actual savings depend on facility design, climate zone, equipment age, and workload patterns.
  Always validate with qualified facility engineers before capital investment decisions.
</div>""", unsafe_allow_html=True)
