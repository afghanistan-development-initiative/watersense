import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="WaterSense — ADI",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ──
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #4fc3f7; }
    .metric-label { font-size: 0.8rem; color: #9999bb; text-transform: uppercase; letter-spacing: 0.1em; }
    .crisis-box {
        background: linear-gradient(135deg, #1a0a0a, #2d1a1a);
        border: 1px solid rgba(255,80,80,0.3);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.5rem 0;
    }
    .header-tag {
        background: rgba(79,195,247,0.15);
        border: 1px solid rgba(79,195,247,0.3);
        color: #4fc3f7;
        padding: 0.3rem 1rem;
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# ── WORLD BANK API ──
@st.cache_data(ttl=86400)
def get_wb_data(indicator, country="AF", years=20):
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json&mrv={years}&per_page=100"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if len(data) > 1 and data[1]:
            df = pd.DataFrame(data[1])
            df = df[["date", "value"]].dropna()
            df["date"] = pd.to_numeric(df["date"])
            df = df.sort_values("date")
            return df
    except:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=86400)
def get_wb_latest(indicator, country="AF"):
    df = get_wb_data(indicator, country, years=5)
    if not df.empty:
        return df.iloc[-1]["value"]
    return None

@st.cache_data(ttl=86400)
def get_regional_comparison(indicator, countries):
    results = {}
    for code, name in countries.items():
        val = get_wb_latest(indicator, code)
        if val:
            results[name] = val
    return results

# ── HEADER ──
st.markdown('<div style="text-align:center; padding: 1rem 0 0.5rem;">', unsafe_allow_html=True)
st.markdown('<span class="header-tag">Afghanistan Development Initiative — ADI</span>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center; padding: 0.5rem 0 2rem;'>
    <h1 style='font-size:2.5rem; color:#ffffff; margin-bottom:0.5rem;'>
        💧 WaterSense
    </h1>
    <p style='color:#9999bb; font-size:1.1rem;'>
        Afghanistan Water Security Dashboard — Live data from World Bank & FAO
    </p>
</div>
""", unsafe_allow_html=True)

# ── TABS ──
tab1, tab2, tab3 = st.tabs([
    "🇦🇫 Afghanistan Focus",
    "🌍 Regional Comparison",
    "📊 Trends & Analysis"
])

# ════════════════════════════════════════
# TAB 1 — AFGHANISTAN FOCUS
# ════════════════════════════════════════
with tab1:
    st.markdown("### Afghanistan Water Security Overview")
    st.markdown("*Live data pulled from World Bank API — updates daily*")

    # Pull live data
    with st.spinner("Loading live data from World Bank..."):
        water_access = get_wb_latest("SH.H2O.BASW.ZS", "AF")
        rural_water = get_wb_latest("SH.H2O.BASW.RU.ZS", "AF")
        urban_water = get_wb_latest("SH.H2O.BASW.UR.ZS", "AF")
        sanitation = get_wb_latest("SH.STA.BASS.ZS", "AF")
        population = get_wb_latest("SP.POP.TOTL", "AF")
        rural_pop = get_wb_latest("SP.RUR.TOTL.ZS", "AF")

    # KEY METRICS
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        val = f"{water_access:.1f}%" if water_access else "~36%"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:#4fc3f7">{val}</div>
            <div class="metric-label">Safe water access</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        val = f"{rural_water:.1f}%" if rural_water else "~25%"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:#ff8a65">{val}</div>
            <div class="metric-label">Rural water access</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        val = f"{urban_water:.1f}%" if urban_water else "~67%"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:#81c784">{val}</div>
            <div class="metric-label">Urban water access</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        val = f"{sanitation:.1f}%" if sanitation else "~28%"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:#ce93d8">{val}</div>
            <div class="metric-label">Basic sanitation</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # KABUL CRISIS SECTION
    st.markdown("### 🚨 Kabul Groundwater Crisis")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
        <div class="crisis-box">
            <h4 style="color:#ff5252; margin-bottom:1rem;">Critical Indicators</h4>
            <p style="color:#e0e0e0; margin-bottom:0.5rem;">📉 <strong>Groundwater depletion:</strong> Up to 3 metres/year in parts of Kabul</p>
            <p style="color:#e0e0e0; margin-bottom:0.5rem;">🚰 <strong>Dependency:</strong> 75–80% of Kabul drinking water from over-extracted wells</p>
            <p style="color:#e0e0e0; margin-bottom:0.5rem;">💧 <strong>Annual deficit:</strong> 44 million m³ gap between use and recharge by 2030</p>
            <p style="color:#e0e0e0; margin-bottom:0.5rem;">👥 <strong>Population at risk:</strong> ~6 million people in greater Kabul</p>
            <p style="color:#ff8a65; margin-top:1rem; font-size:0.85rem;">Source: FAO AQUASTAT, World Bank WASH data</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Groundwater depletion projection chart
        years = list(range(2015, 2031))
        depletion = [0, -0.3, -0.6, -1.0, -1.5, -2.0, -2.6, -3.2, -3.9, -4.7,
                     -5.6, -6.6, -7.7, -9.0, -10.4, -12.0]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years, y=depletion,
            mode='lines+markers',
            line=dict(color='#ff5252', width=3),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(255,82,82,0.1)',
            name='Groundwater level change (m)'
        ))
        fig.add_vline(x=2025, line_dash="dash", line_color="#4fc3f7",
                      annotation_text="Today", annotation_position="top right")
        fig.update_layout(
            title="Kabul Groundwater Depletion Projection",
            xaxis_title="Year",
            yaxis_title="Change in groundwater level (m)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0'),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # WATER ACCESS TREND
    st.markdown("### 📈 Water Access Trend (Live from World Bank)")

    with st.spinner("Loading trend data..."):
        trend_df = get_wb_data("SH.H2O.BASW.ZS", "AF", years=25)
        rural_df = get_wb_data("SH.H2O.BASW.RU.ZS", "AF", years=25)
        urban_df = get_wb_data("SH.H2O.BASW.UR.ZS", "AF", years=25)

    if not trend_df.empty:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=trend_df["date"], y=trend_df["value"],
            mode='lines+markers', name='National', line=dict(color='#4fc3f7', width=3)))
        if not rural_df.empty:
            fig2.add_trace(go.Scatter(x=rural_df["date"], y=rural_df["value"],
                mode='lines+markers', name='Rural', line=dict(color='#ff8a65', width=2)))
        if not urban_df.empty:
            fig2.add_trace(go.Scatter(x=urban_df["date"], y=urban_df["value"],
                mode='lines+markers', name='Urban', line=dict(color='#81c784', width=2)))
        fig2.update_layout(
            title="Afghanistan — Access to Basic Drinking Water (%)",
            xaxis_title="Year", yaxis_title="Population with access (%)",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0'), height=400,
            legend=dict(bgcolor='rgba(0,0,0,0)')
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Loading live data from World Bank API...")

    # RIVER BASINS
    st.markdown("---")
    st.markdown("### 🏔️ Afghanistan Major River Basins")

    basins = {
        "Basin": ["Amu Darya", "Helmand", "Kabul", "Harirud-Murghab", "Northern"],
        "Area (km²)": [258000, 334000, 90000, 112000, 58000],
        "Annual Flow (km³)": [20.6, 11.8, 16.4, 4.2, 1.9],
        "Countries shared": ["AFG, TJK, UZB, TKM", "AFG, IRN, PAK", "AFG, PAK", "AFG, IRN, TKM", "AFG, TKM"]
    }
    df_basins = pd.DataFrame(basins)

    fig3 = px.bar(df_basins, x="Basin", y="Annual Flow (km³)",
                  color="Annual Flow (km³)", color_continuous_scale="Blues",
                  title="Afghanistan River Basins — Annual Flow")
    fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                       font=dict(color='#e0e0e0'), height=350)
    st.plotly_chart(fig3, use_container_width=True)
    st.dataframe(df_basins, use_container_width=True)

# ════════════════════════════════════════
# TAB 2 — REGIONAL COMPARISON
# ════════════════════════════════════════
with tab2:
    st.markdown("### Afghanistan vs Regional Countries")
    st.markdown("*Live comparison data from World Bank*")

    countries = {
        "AF": "Afghanistan", "PK": "Pakistan", "IR": "Iran",
        "TJ": "Tajikistan", "UZ": "Uzbekistan", "IN": "India",
        "BD": "Bangladesh", "MM": "Myanmar"
    }

    with st.spinner("Loading regional data from World Bank..."):
        comparison = get_regional_comparison("SH.H2O.BASW.ZS", countries)

    if comparison:
        df_comp = pd.DataFrame(list(comparison.items()), columns=["Country", "Water Access (%)"])
        df_comp = df_comp.sort_values("Water Access (%)")
        colors = ["#ff5252" if c == "Afghanistan" else "#4fc3f7" for c in df_comp["Country"]]

        fig4 = go.Figure(go.Bar(
            x=df_comp["Water Access (%)"],
            y=df_comp["Country"],
            orientation='h',
            marker_color=colors,
            text=df_comp["Water Access (%)"].round(1).astype(str) + "%",
            textposition='outside'
        ))
        fig4.update_layout(
            title="Access to Safe Drinking Water — Regional Comparison (%)",
            xaxis_title="Population with access (%)",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0'), height=450
        )
        st.plotly_chart(fig4, use_container_width=True)

        # Global average
        global_avg = get_wb_latest("SH.H2O.BASW.ZS", "1W")
        af_val = comparison.get("Afghanistan", 36)
        if global_avg:
            col1, col2, col3 = st.columns(3)
            col1.metric("Afghanistan", f"{af_val:.1f}%")
            col2.metric("Global Average", f"{global_avg:.1f}%")
            col3.metric("Gap", f"{global_avg - af_val:.1f}%", delta=f"{global_avg - af_val:.1f}% below global average", delta_color="inverse")
    else:
        st.info("Loading regional comparison data...")

    # SANITATION COMPARISON
    st.markdown("---")
    st.markdown("### Sanitation Access — Regional Comparison")

    with st.spinner("Loading sanitation data..."):
        sanitation_comp = get_regional_comparison("SH.STA.BASS.ZS", countries)

    if sanitation_comp:
        df_san = pd.DataFrame(list(sanitation_comp.items()), columns=["Country", "Sanitation Access (%)"])
        df_san = df_san.sort_values("Sanitation Access (%)")
        colors2 = ["#ff5252" if c == "Afghanistan" else "#81c784" for c in df_san["Country"]]

        fig5 = go.Figure(go.Bar(
            x=df_san["Sanitation Access (%)"],
            y=df_san["Country"],
            orientation='h',
            marker_color=colors2,
            text=df_san["Sanitation Access (%)"].round(1).astype(str) + "%",
            textposition='outside'
        ))
        fig5.update_layout(
            title="Access to Basic Sanitation — Regional Comparison (%)",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0'), height=450
        )
        st.plotly_chart(fig5, use_container_width=True)

# ════════════════════════════════════════
# TAB 3 — TRENDS & ANALYSIS
# ════════════════════════════════════════
with tab3:
    st.markdown("### Water Security Trends & Analysis")

    # MULTI COUNTRY TREND
    st.markdown("#### Water Access Progress — Afghanistan vs Neighbours")

    trend_countries = {"AF": "Afghanistan", "PK": "Pakistan", "IR": "Iran", "TJ": "Tajikistan"}

    with st.spinner("Loading trend data..."):
        fig6 = go.Figure()
        for code, name in trend_countries.items():
            df_t = get_wb_data("SH.H2O.BASW.ZS", code, years=25)
            if not df_t.empty:
                color = "#ff5252" if code == "AF" else None
                width = 4 if code == "AF" else 2
                fig6.add_trace(go.Scatter(
                    x=df_t["date"], y=df_t["value"],
                    mode='lines', name=name,
                    line=dict(color=color, width=width)
                ))

    fig6.update_layout(
        title="Water Access Progress (% population) — 25 Year Trend",
        xaxis_title="Year", yaxis_title="Access (%)",
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e0e0'), height=450,
        legend=dict(bgcolor='rgba(0,0,0,0)')
    )
    st.plotly_chart(fig6, use_container_width=True)

    st.markdown("---")

    # SOLUTIONS SECTION
    st.markdown("### 💡 Solutions & Implementation Pathways")
    st.markdown("*Based on FAO guidelines and field experience in Afghanistan*")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Immediate actions (0–2 years)**
        - ✅ Rainwater harvesting systems for homes and public buildings
        - ✅ Community-scale water filtration units
        - ✅ Awareness campaigns on water conservation
        - ✅ Repair and maintenance of existing kareez systems

        **Medium term (2–5 years)**
        - 🔧 Urban aquifer recharge zones
        - 🔧 Small-scale desalination for saline groundwater areas
        - 🔧 Drip irrigation rollout in Kabul river basin
        - 🔧 Water-smart urban infrastructure planning
        """)

    with col2:
        st.markdown("""
        **Long term (5–10 years)**
        - 🌊 River basin management framework
        - 🌊 Transboundary water agreements (Amu Darya, Helmand)
        - 🌊 National groundwater monitoring network
        - 🌊 Climate-resilient water infrastructure

        **Data & monitoring needs**
        - 📡 Provincial groundwater monitoring stations
        - 📡 Real-time river flow sensors
        - 📡 Satellite-based soil moisture tracking
        - 📡 Open national water data portal
        """)

    st.markdown("---")

    # DATA SOURCES
    st.markdown("### 📚 Data Sources")
    st.markdown("""
    | Source | Data | Update frequency |
    |--------|------|-----------------|
    | World Bank API | Water access, sanitation, population | Annual |
    | FAO AQUASTAT | River basins, water resources | Annual |
    | GRACE-FO Satellite | Groundwater storage anomalies | Monthly |
    | CHIRPS | Rainfall and precipitation | Monthly |
    | ADI field research | Kabul groundwater crisis indicators | As available |
    """)

# ── FOOTER ──
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#9999bb; font-size:0.8rem; padding:1rem;'>
    WaterSense is part of the <a href='https://afghanistan-development-initiative.github.io' style='color:#4fc3f7;'>Afghanistan Development Initiative (ADI)</a> — 
    open data, research and tools for Afghanistan's development.<br>
    Built by <a href='https://www.linkedin.com/in/maiwand-alamzoi-33b9351a9' style='color:#4fc3f7;'>Maiwand Jan Alamzoi</a> | 
    Data: World Bank API, FAO AQUASTAT | 
    <a href='https://github.com/afghanistan-development-initiative/watersense' style='color:#4fc3f7;'>GitHub</a>
</div>
""", unsafe_allow_html=True)
