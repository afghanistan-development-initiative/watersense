import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="WaterSense — ADI", page_icon="💧", layout="wide")

st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px; padding: 1.2rem; text-align: center;
}
.metric-value { font-size: 2rem; font-weight: 700; }
.metric-label { font-size: 0.8rem; color: #9999bb; text-transform: uppercase; letter-spacing: 0.1em; }
.crisis-box {
    background: linear-gradient(135deg, #1a0a0a, #2d1a1a);
    border: 1px solid rgba(255,80,80,0.3);
    border-radius: 12px; padding: 1.2rem; margin: 0.5rem 0;
}
.info-box {
    background: linear-gradient(135deg, #0a1a2a, #0d2137);
    border: 1px solid rgba(79,195,247,0.3);
    border-radius: 12px; padding: 1.2rem; margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

ALL_COUNTRIES = {
    "Afghanistan": "AF", "Albania": "AL", "Algeria": "DZ", "Angola": "AO",
    "Argentina": "AR", "Armenia": "AM", "Australia": "AU", "Austria": "AT",
    "Azerbaijan": "AZ", "Bangladesh": "BD", "Belarus": "BY", "Belgium": "BE",
    "Bolivia": "BO", "Brazil": "BR", "Bulgaria": "BG", "Cambodia": "KH",
    "Cameroon": "CM", "Canada": "CA", "Chile": "CL", "China": "CN",
    "Colombia": "CO", "Congo, Dem. Rep.": "CD", "Croatia": "HR",
    "Czech Republic": "CZ", "Denmark": "DK", "Ecuador": "EC", "Egypt": "EG",
    "Ethiopia": "ET", "Finland": "FI", "France": "FR", "Georgia": "GE",
    "Germany": "DE", "Ghana": "GH", "Greece": "GR", "Guatemala": "GT",
    "Honduras": "HN", "Hungary": "HU", "India": "IN", "Indonesia": "ID",
    "Iran": "IR", "Iraq": "IQ", "Ireland": "IE", "Israel": "IL",
    "Italy": "IT", "Japan": "JP", "Jordan": "JO", "Kazakhstan": "KZ",
    "Kenya": "KE", "Kuwait": "KW", "Kyrgyzstan": "KG", "Laos": "LA",
    "Lebanon": "LB", "Libya": "LY", "Malaysia": "MY", "Mali": "ML",
    "Mexico": "MX", "Moldova": "MD", "Mongolia": "MN", "Morocco": "MA",
    "Mozambique": "MZ", "Myanmar": "MM", "Nepal": "NP", "Netherlands": "NL",
    "New Zealand": "NZ", "Nicaragua": "NI", "Niger": "NE", "Nigeria": "NG",
    "Norway": "NO", "Oman": "OM", "Pakistan": "PK", "Panama": "PA",
    "Paraguay": "PY", "Peru": "PE", "Philippines": "PH", "Poland": "PL",
    "Portugal": "PT", "Qatar": "QA", "Romania": "RO", "Russia": "RU",
    "Rwanda": "RW", "Saudi Arabia": "SA", "Senegal": "SN", "Serbia": "RS",
    "Sierra Leone": "SL", "Somalia": "SO", "South Africa": "ZA",
    "South Korea": "KR", "Spain": "ES", "Sri Lanka": "LK", "Sudan": "SD",
    "Sweden": "SE", "Switzerland": "CH", "Syria": "SY", "Tajikistan": "TJ",
    "Tanzania": "TZ", "Thailand": "TH", "Tunisia": "TN", "Turkey": "TR",
    "Turkmenistan": "TM", "Uganda": "UG", "Ukraine": "UA",
    "United Arab Emirates": "AE", "United Kingdom": "GB", "United States": "US",
    "Uruguay": "UY", "Uzbekistan": "UZ", "Venezuela": "VE", "Vietnam": "VN",
    "Yemen": "YE", "Zambia": "ZM", "Zimbabwe": "ZW"
}

REGIONS = {
    "South Asia": {"AF": "Afghanistan", "PK": "Pakistan", "IN": "India", "BD": "Bangladesh", "NP": "Nepal", "LK": "Sri Lanka"},
    "Central Asia": {"AF": "Afghanistan", "TJ": "Tajikistan", "UZ": "Uzbekistan", "KZ": "Kazakhstan", "KG": "Kyrgyzstan", "TM": "Turkmenistan"},
    "Middle East": {"IR": "Iran", "IQ": "Iraq", "SY": "Syria", "JO": "Jordan", "YE": "Yemen", "SA": "Saudi Arabia"},
    "Sub-Saharan Africa": {"ET": "Ethiopia", "KE": "Kenya", "TZ": "Tanzania", "NG": "Nigeria", "GH": "Ghana", "MZ": "Mozambique"},
    "Europe": {"NL": "Netherlands", "DE": "Germany", "FR": "France", "GB": "United Kingdom", "PL": "Poland", "ES": "Spain"},
}

@st.cache_data(ttl=86400)
def get_wb_data(indicator, country="AF", years=25):
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json&mrv={years}&per_page=100"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if len(data) > 1 and data[1]:
            df = pd.DataFrame(data[1])
            df = df[["date", "value"]].dropna()
            df["date"] = pd.to_numeric(df["date"])
            return df.sort_values("date")
    except:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=86400)
def get_latest(indicator, country="AF"):
    df = get_wb_data(indicator, country, years=5)
    if not df.empty:
        val = df.dropna()
        if not val.empty:
            return val.iloc[-1]["value"]
    return None

# HEADER
st.markdown("""
<div style='text-align:center; padding:1rem 0 0.5rem;'>
    <p style='color:#4fc3f7; font-size:0.75rem; font-weight:600; letter-spacing:0.2em; text-transform:uppercase;'>Afghanistan Development Initiative — ADI</p>
    <h1 style='font-size:2.8rem; color:#ffffff; margin:0.3rem 0;'>💧 WaterSense</h1>
    <p style='color:#9999bb; font-size:1.05rem;'>Global Water Security Dashboard — Live data from World Bank API</p>
    <p style='color:#4fc3f7; font-size:0.85rem;'>🌍 Any country worldwide · 🇦🇫 Afghanistan deep dive · 📊 Compare countries</p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["🇦🇫 Afghanistan Deep Dive", "🌍 Global — Any Country", "📊 Compare Countries"])

# ── TAB 1: AFGHANISTAN ──
with tab1:
    st.markdown("### Afghanistan Water Security — Deep Dive")
    with st.spinner("Loading live data..."):
        wa = get_latest("SH.H2O.BASW.ZS", "AF")
        ru = get_latest("SH.H2O.BASW.RU.ZS", "AF")
        ur = get_latest("SH.H2O.BASW.UR.ZS", "AF")
        sa = get_latest("SH.STA.BASS.ZS", "AF")
        ga = get_latest("SH.H2O.BASW.ZS", "1W")

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, val, fb, color, label in [
        (c1, wa, "~36%", "#ff5252", "National access"),
        (c2, ru, "~25%", "#ff8a65", "Rural access"),
        (c3, ur, "~67%", "#81c784", "Urban access"),
        (c4, sa, "~28%", "#ce93d8", "Sanitation"),
        (c5, ga, "~74%", "#4fc3f7", "Global average"),
    ]:
        d = f"{val:.1f}%" if val else fb
        col.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{color}">{d}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🚨 Kabul Groundwater Crisis")
        st.markdown("""<div class="crisis-box">
            <p style="color:#e0e0e0">📉 <strong>Depletion:</strong> Up to 3 metres/year</p>
            <p style="color:#e0e0e0">🚰 <strong>Dependency:</strong> 75–80% from over-extracted wells</p>
            <p style="color:#e0e0e0">💧 <strong>Deficit by 2030:</strong> 44 million m³/year</p>
            <p style="color:#e0e0e0">👥 <strong>At risk:</strong> ~6 million people in Kabul</p>
            <p style="color:#ff8a65; font-size:0.8rem;">Source: FAO AQUASTAT, World Bank</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        yrs = list(range(2015, 2031))
        dep = [0,-0.3,-0.6,-1.0,-1.5,-2.0,-2.6,-3.2,-3.9,-4.7,-5.6,-6.6,-7.7,-9.0,-10.4,-12.0]
        fig = go.Figure(go.Scatter(x=yrs, y=dep, mode='lines+markers',
            line=dict(color='#ff5252', width=3), fill='tozeroy', fillcolor='rgba(255,82,82,0.1)'))
        fig.add_vline(x=2025, line_dash="dash", line_color="#4fc3f7", annotation_text="Today")
        fig.update_layout(title="Kabul Groundwater Depletion Projection",
            xaxis_title="Year", yaxis_title="Level change (m)",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0'), height=300)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📈 Afghanistan Water Access Trend")
    with st.spinner("Loading..."):
        n_df = get_wb_data("SH.H2O.BASW.ZS", "AF")
        r_df = get_wb_data("SH.H2O.BASW.RU.ZS", "AF")
        u_df = get_wb_data("SH.H2O.BASW.UR.ZS", "AF")
    fig2 = go.Figure()
    for df_t, name, color in [(n_df,"National","#4fc3f7"),(r_df,"Rural","#ff8a65"),(u_df,"Urban","#81c784")]:
        if not df_t.empty:
            fig2.add_trace(go.Scatter(x=df_t["date"], y=df_t["value"], mode='lines+markers', name=name, line=dict(color=color, width=3 if name=="National" else 2)))
    fig2.update_layout(title="Access to Safe Drinking Water (%)", xaxis_title="Year", yaxis_title="%",
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e0e0e0'), height=400, legend=dict(bgcolor='rgba(0,0,0,0)'))
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 💡 Solutions & Implementation Pathways")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""**Immediate (0–2 years)**
- ✅ Rainwater harvesting systems
- ✅ Community water filtration
- ✅ Repair kareez/qanat systems
- ✅ Water conservation campaigns

**Medium term (2–5 years)**
- 🔧 Urban aquifer recharge zones
- 🔧 Drip irrigation rollout
- 🔧 Water-smart urban planning""")
    with c2:
        st.markdown("""**Long term (5–10 years)**
- 🌊 National river basin management
- 🌊 Transboundary water agreements
- 🌊 Groundwater monitoring network
- 🌊 Climate-resilient infrastructure

**Data needs**
- 📡 Provincial monitoring stations
- 📡 Real-time river sensors
- 📡 Open national water portal""")

# ── TAB 2: GLOBAL ──
with tab2:
    st.markdown("### 🌍 Global Water Security — Any Country")
    st.markdown("*Select any country to see live water security data from World Bank*")

    col1, col2 = st.columns([3, 1])
    with col1:
        sel_country = st.selectbox("Select a country", sorted(ALL_COUNTRIES.keys()),
                                    index=sorted(ALL_COUNTRIES.keys()).index("Afghanistan"))
    sel_code = ALL_COUNTRIES[sel_country]

    with st.spinner(f"Loading data for {sel_country}..."):
        cw = get_latest("SH.H2O.BASW.ZS", sel_code)
        cr = get_latest("SH.H2O.BASW.RU.ZS", sel_code)
        cu = get_latest("SH.H2O.BASW.UR.ZS", sel_code)
        cs = get_latest("SH.STA.BASS.ZS", sel_code)
        gv = get_latest("SH.H2O.BASW.ZS", "1W")

    st.markdown(f"#### {sel_country} — Water Indicators")
    c1,c2,c3,c4 = st.columns(4)
    for col, val, label, color in [(c1,cw,"Water access","#4fc3f7"),(c2,cr,"Rural access","#ff8a65"),(c3,cu,"Urban access","#81c784"),(c4,cs,"Sanitation","#ce93d8")]:
        d = f"{val:.1f}%" if val else "No data"
        col.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{color}">{d}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    if cw and gv:
        diff = cw - gv
        color = "#81c784" if diff >= 0 else "#ff5252"
        arrow = "▲" if diff >= 0 else "▼"
        st.markdown(f'<div class="info-box"><p style="color:#e0e0e0"><strong>{sel_country}:</strong> <strong style="color:#4fc3f7">{cw:.1f}%</strong> &nbsp;|&nbsp; <strong>Global avg:</strong> <strong style="color:#4fc3f7">{gv:.1f}%</strong> &nbsp;|&nbsp; <strong style="color:{color}">{arrow} {abs(diff):.1f}% vs global</strong></p></div>', unsafe_allow_html=True)

    st.markdown(f"#### {sel_country} — 25 Year Trend")
    with st.spinner("Loading trend..."):
        sn = get_wb_data("SH.H2O.BASW.ZS", sel_code)
        sr = get_wb_data("SH.H2O.BASW.RU.ZS", sel_code)
        su = get_wb_data("SH.H2O.BASW.UR.ZS", sel_code)
    fig3 = go.Figure()
    for df_t, name, color in [(sn,"National","#4fc3f7"),(sr,"Rural","#ff8a65"),(su,"Urban","#81c784")]:
        if not df_t.empty:
            fig3.add_trace(go.Scatter(x=df_t["date"], y=df_t["value"], mode='lines+markers', name=name, line=dict(color=color, width=3 if name=="National" else 2)))
    if gv:
        fig3.add_hline(y=gv, line_dash="dash", line_color="#ffffff", annotation_text=f"Global avg: {gv:.1f}%")
    fig3.update_layout(title=f"{sel_country} — Water Access (%)", xaxis_title="Year", yaxis_title="%",
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e0e0e0'), height=420, legend=dict(bgcolor='rgba(0,0,0,0)'))
    st.plotly_chart(fig3, use_container_width=True)

# ── TAB 3: COMPARE ──
with tab3:
    st.markdown("### 📊 Compare Countries")
    mode = st.radio("Compare by:", ["Select a region", "Choose countries manually"], horizontal=True)

    if mode == "Select a region":
        region = st.selectbox("Region", list(REGIONS.keys()))
        comp_c = REGIONS[region]
    else:
        names = st.multiselect("Select countries (max 10)", sorted(ALL_COUNTRIES.keys()),
            default=["Afghanistan","Pakistan","Iran","Tajikistan","India"], max_selections=10)
        comp_c = {ALL_COUNTRIES[n]: n for n in names}

    ind_choice = st.selectbox("Indicator", ["Water access (national)","Rural water access","Urban water access","Basic sanitation"])
    ind_map = {"Water access (national)":"SH.H2O.BASW.ZS","Rural water access":"SH.H2O.BASW.RU.ZS","Urban water access":"SH.H2O.BASW.UR.ZS","Basic sanitation":"SH.STA.BASS.ZS"}
    ind_code = ind_map[ind_choice]

    with st.spinner("Loading..."):
        comp_vals = {name: get_latest(ind_code, code) for code, name in comp_c.items()}
        comp_vals = {k: v for k, v in comp_vals.items() if v}

    if comp_vals:
        df_cv = pd.DataFrame(list(comp_vals.items()), columns=["Country", ind_choice]).sort_values(ind_choice)
        colors = ["#ff5252" if c == "Afghanistan" else "#4fc3f7" for c in df_cv["Country"]]
        fig4 = go.Figure(go.Bar(x=df_cv[ind_choice], y=df_cv["Country"], orientation='h',
            marker_color=colors, text=df_cv[ind_choice].round(1).astype(str)+"%", textposition='outside'))
        gv2 = get_latest(ind_code, "1W")
        if gv2:
            fig4.add_vline(x=gv2, line_dash="dash", line_color="#ffffff", annotation_text=f"Global: {gv2:.1f}%")
        fig4.update_layout(title=f"{ind_choice} — Comparison (%)",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0'), height=max(400, len(comp_vals)*50), legend=dict(bgcolor='rgba(0,0,0,0)'))
        st.plotly_chart(fig4, use_container_width=True)

        st.markdown("#### Trend Comparison")
        with st.spinner("Loading trends..."):
            fig5 = go.Figure()
            for code, name in comp_c.items():
                df_t = get_wb_data(ind_code, code)
                if not df_t.empty:
                    fig5.add_trace(go.Scatter(x=df_t["date"], y=df_t["value"], mode='lines', name=name,
                        line=dict(color="#ff5252" if name=="Afghanistan" else None, width=4 if name=="Afghanistan" else 2)))
        fig5.update_layout(title=f"{ind_choice} — 25 Year Trend", xaxis_title="Year", yaxis_title="%",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e0e0e0'),
            height=450, legend=dict(bgcolor='rgba(0,0,0,0)'))
        st.plotly_chart(fig5, use_container_width=True)
        st.dataframe(df_cv.sort_values(ind_choice, ascending=False).reset_index(drop=True), use_container_width=True)

# FOOTER
st.markdown("---")
st.markdown("""<div style='text-align:center; color:#9999bb; font-size:0.8rem; padding:1rem;'>
WaterSense is part of the <a href='https://afghanistan-development-initiative.github.io' style='color:#4fc3f7;'>Afghanistan Development Initiative (ADI)</a><br>
Built by <a href='https://www.linkedin.com/in/maiwand-alamzoi-33b9351a9' style='color:#4fc3f7;'>Maiwand Jan Alamzoi</a> | 
Data: World Bank API | <a href='https://github.com/afghanistan-development-initiative/watersense' style='color:#4fc3f7;'>GitHub</a>
</div>""", unsafe_allow_html=True)
