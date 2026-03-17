import os
from collections import defaultdict

import streamlit as st

try:
    import pandas as pd
except Exception:
    pd = None

try:
    import plotly.express as px
    import plotly.graph_objects as go
except Exception:
    px = None

st.set_page_config(
    page_title="Kellermann | Social Media Intelligence",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)

if px is None or pd is None:
    st.error("Run: pip install plotly pandas")
    st.stop()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap');
:root {
  --bg: #0a0a0b; --surface: #111113;
  --border: rgba(255,255,255,0.07); --border-hover: rgba(255,255,255,0.14);
  --text: #f0f0f0; --muted: #888;
  --accent: #f59e0b; --accent2: #e11d48; --accent3: #0ea5e9; --green: #22c55e;
  --mono: 'DM Mono', monospace; --display: 'Syne', sans-serif;
}
html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important; color: var(--text) !important; font-family: var(--display);
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border) !important; }
[data-testid="stSidebar"] * { font-family: var(--display) !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
.kpi { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 18px 20px; position: relative; overflow: hidden; transition: border-color 0.2s; margin-bottom: 8px; }
.kpi::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: var(--accent); }
.kpi:hover { border-color: var(--border-hover); }
.kpi .k-label { font-size: 0.70rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted); font-family: var(--mono); margin-bottom: 8px; }
.kpi .k-value { font-size: 1.80rem; font-weight: 800; letter-spacing: -0.02em; color: var(--text); line-height: 1; }
.kpi .k-hint { font-size: 0.72rem; color: var(--muted); margin-top: 6px; font-family: var(--mono); }
.kpi .k-accent { color: var(--accent); }
.dash-header { border-bottom: 1px solid var(--border); padding-bottom: 20px; margin-bottom: 24px; }
.dash-eyebrow { font-family: var(--mono); font-size: 0.72rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--accent); margin-bottom: 6px; }
.dash-title { font-size: 1.90rem; font-weight: 800; letter-spacing: -0.03em; color: var(--text); }
.dash-title span { color: var(--accent); }
.dash-sub { font-size: 0.85rem; color: var(--muted); margin-top: 4px; font-family: var(--mono); }
.insight { background: rgba(245,158,11,0.06); border: 1px solid rgba(245,158,11,0.20); border-left: 3px solid var(--accent); border-radius: 8px; padding: 14px 18px; font-size: 0.88rem; margin: 16px 0; line-height: 1.55; }
.insight b { color: var(--accent); font-weight: 700; }
.insight-label { font-family: var(--mono); font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.12em; color: var(--accent); margin-bottom: 6px; }
.insight-blue { background: rgba(14,165,233,0.06); border-color: rgba(14,165,233,0.20); border-left-color: var(--accent3); }
.insight-blue b, .insight-blue .insight-label { color: var(--accent3); }
.section-label { font-family: var(--mono); font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.14em; color: var(--muted); margin-bottom: 12px; margin-top: 28px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
div[data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--border) !important; }
button[data-baseweb="tab"] { font-family: var(--mono) !important; font-size: 0.78rem !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; border-radius: 6px 6px 0 0 !important; padding: 10px 18px !important; color: var(--muted) !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: var(--accent) !important; background: rgba(245,158,11,0.06) !important; }
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: 8px; }
span[data-baseweb="tag"] { background: rgba(245,158,11,0.15) !important; }
</style>
""", unsafe_allow_html=True)


def normalize_yes_no(v):
    s = str(v).strip().lower()
    if s in {"yes", "y", "true", "1"}: return "Yes"
    if s in {"no", "n", "false", "0"}: return "No"
    return "Unknown"

@st.cache_data(show_spinner=False)
def load_df(path):
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for c in ["Platform","Product_Featured","Post_Type","AI_Generated_Caption","Campaign"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    for c in ["Views","Likes","Comments","Shares","Saves"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
        else:
            df[c] = 0
    df["AI_Generated_Caption"] = df["AI_Generated_Caption"].apply(normalize_yes_no)
    df["Interactions"] = df["Likes"] + df["Comments"]
    df["Total_Engagements"] = df["Interactions"] + df["Shares"] + df["Saves"]
    df["Engagement_Rate"] = (df["Total_Engagements"] / df["Views"].replace(0, float("nan")) * 100).round(2)
    return df

def unique_sorted(df, col):
    if col not in df.columns: return []
    return sorted(df[col].dropna().astype(str).str.strip().unique().tolist(), key=str.lower)

def top_val(s):
    if s is None or s.empty: return "—"
    s = s.dropna()
    return str(s.idxmax()) if not s.empty else "—"

def fmt_num(n):
    n = float(n)
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000: return f"{n/1_000:.1f}K"
    return str(int(n))

def kpi(label, value, hint=None, accent=False):
    hint_html = f'<div class="k-hint">{hint}</div>' if hint else ""
    val_class = "k-value k-accent" if accent else "k-value"
    st.markdown(f'<div class="kpi"><div class="k-label">{label}</div><div class="{val_class}">{value}</div>{hint_html}</div>', unsafe_allow_html=True)

def insight_box(text, kind="amber"):
    cls = {"amber": "", "blue": " insight-blue"}.get(kind, "")
    label = {"amber": "📊 Insight", "blue": "💡 Recommendation"}.get(kind, "Insight")
    st.markdown(f'<div class="insight{cls}"><div class="insight-label">{label}</div>{text}</div>', unsafe_allow_html=True)

DARK_LAYOUT = dict(
    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=44, b=10),
    font=dict(family="DM Mono, monospace", size=11, color="#888"),
    title_font=dict(family="Syne, sans-serif", size=14, color="#f0f0f0"),
    hoverlabel=dict(bgcolor="#111113", bordercolor="#f59e0b", font=dict(color="#f0f0f0", size=12, family="DM Mono, monospace")),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#222", borderwidth=1, font=dict(size=11)),
)
PLATFORM_COLORS = {"Instagram": "#fb7185", "YouTube": "#fbbf24", "TikTok": "#38bdf8"}
AMBER = "#f59e0b"; RED = "#e11d48"; BLUE = "#0ea5e9"; GREEN = "#22c55e"


csv_path = os.path.join(os.path.dirname(__file__), "kellermann_data.csv")
if not os.path.exists(csv_path):
    st.error("kellermann_data.csv not found in same folder as app.py"); st.stop()

df = load_df(csv_path)
df = df[df["Date"].notna()].copy()
if df.empty:
    st.error("No valid data found."); st.stop()


with st.sidebar:
    st.markdown('<div style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:800;margin-bottom:4px;">💡 Kellermann</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.70rem;color:#666;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:20px;">Dashboard Controls</div>', unsafe_allow_html=True)
    platforms = unique_sorted(df, "Platform")
    products  = unique_sorted(df, "Product_Featured")
    campaigns = unique_sorted(df, "Campaign")
    sel_platforms = st.multiselect("Platform",      platforms, default=platforms, key="k_plat")
    sel_products  = st.multiselect("Product",       products,  default=products,  key="k_prod")
    sel_campaigns = st.multiselect("Campaign Type", campaigns, default=campaigns, key="k_camp")
    min_d, max_d = df["Date"].min().date(), df["Date"].max().date()
    sel_range = st.date_input("Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d, key="k_date")
    start_d = sel_range[0] if isinstance(sel_range, (tuple, list)) and len(sel_range) >= 1 else min_d
    end_d   = sel_range[1] if isinstance(sel_range, (tuple, list)) and len(sel_range) >= 2 else max_d
    st.divider()
    st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.65rem;color:#444;text-transform:uppercase;letter-spacing:0.1em;">Note: Simulated data for demo purposes</div>', unsafe_allow_html=True)

fdf = df.copy()
if sel_platforms: fdf = fdf[fdf["Platform"].isin(sel_platforms)]
if sel_products:  fdf = fdf[fdf["Product_Featured"].isin(sel_products)]
if sel_campaigns and "Campaign" in fdf.columns: fdf = fdf[fdf["Campaign"].isin(sel_campaigns)]
fdf = fdf[(fdf["Date"].dt.date >= start_d) & (fdf["Date"].dt.date <= end_d)]

st.markdown("""
<div class="dash-header">
  <div class="dash-eyebrow">Social Media Intelligence · Simulated Data</div>
  <div class="dash-title">Kellermann <span>Command Center</span></div>
  <div class="dash-sub">Campaign performance · Content analysis · AI caption impact · Platform breakdown</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["01 · Performance", "02 · Content & AI", "03 · Products", "04 · Raw Data"])


# ── TAB 1 ─────────────────────────────────────────────────────────
with tab1:
    if fdf.empty:
        st.warning("No data for selected filters.")
    else:
        total_views  = int(fdf["Views"].sum())
        total_eng    = int(fdf["Total_Engagements"].sum())
        avg_er       = float(fdf["Engagement_Rate"].mean())
        total_posts  = len(fdf)
        top_platform = top_val(fdf.groupby("Platform")["Views"].sum())
        best_er_plat = top_val(fdf.groupby("Platform")["Engagement_Rate"].mean())

        c1,c2,c3,c4 = st.columns(4, gap="small")
        with c1: kpi("Total Views",        fmt_num(total_views))
        with c2: kpi("Total Engagements",  fmt_num(total_eng), hint="Likes + Comments + Shares + Saves")
        with c3: kpi("Avg Engagement Rate", f"{avg_er:.1f}%", accent=True)
        with c4: kpi("Posts Analyzed",     str(total_posts))

        insight_box(
            f"<b>{top_platform}</b> is the highest-reach platform with "
            f"<b>{fmt_num(int(fdf[fdf['Platform']==top_platform]['Views'].sum()))}</b> total views. "
            f"However, <b>{best_er_plat}</b> drives the highest engagement rate. "
            f"Recommendation: <b>scale volume on {top_platform}</b> and "
            f"<b>optimise content quality on {best_er_plat}</b>."
        )

        # ── Line chart
        st.markdown('<div class="section-label">Views Over Time — by Platform</div>', unsafe_allow_html=True)
        ts = fdf.assign(Week=fdf["Date"].dt.to_period("W").apply(lambda r: r.start_time))
        ts = ts.groupby(["Week","Platform"], as_index=False)["Views"].sum()
        fig_ts = px.line(ts, x="Week", y="Views", color="Platform",
                         color_discrete_map=PLATFORM_COLORS, markers=True)
        fig_ts.update_traces(line=dict(width=2.5), marker=dict(size=5))
        # Clean hover per trace
        for trace in fig_ts.data:
            trace.hovertemplate = f"<b>{trace.name}</b><br>Week: %{{x|%b %d, %Y}}<br>Views: %{{y:,.0f}}<extra></extra>"
        fig_ts.update_layout(
            title="Weekly Views by Platform",
            xaxis_title="", yaxis_title="Total Views",
            **DARK_LAYOUT
        )
        fig_ts.update_xaxes(showgrid=False, zeroline=False, color="#555")
        fig_ts.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.04)", zeroline=False, color="#555")
        st.plotly_chart(fig_ts, use_container_width=True, key="ts_line")

        col_a, col_b = st.columns(2, gap="large")
        with col_a:
            st.markdown('<div class="section-label">Platform — Views vs Engagement Rate</div>', unsafe_allow_html=True)
            plat_sum = fdf.groupby("Platform", as_index=False).agg(
                Views=("Views","sum"), ER=("Engagement_Rate","mean"), Posts=("Platform","count"))
            fig_bub = px.scatter(plat_sum, x="Views", y="ER", size="Posts",
                                 color="Platform", color_discrete_map=PLATFORM_COLORS,
                                 text="Platform", size_max=55)
            fig_bub.update_traces(
                textposition="top center", textfont=dict(size=11, color="#f0f0f0"),
                hovertemplate="<b>%{text}</b><br>Total Views: %{x:,.0f}<br>Avg ER: %{y:.1f}%<br>Posts: %{marker.size}<extra></extra>"
            )
            fig_bub.update_layout(
                title="Views vs Engagement Rate by Platform",
                xaxis_title="Total Views", yaxis_title="Avg Engagement Rate (%)",
                showlegend=False, **DARK_LAYOUT
            )
            fig_bub.update_xaxes(showgrid=False, zeroline=False, color="#555")
            fig_bub.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.04)", zeroline=False, color="#555")
            st.plotly_chart(fig_bub, use_container_width=True, key="plat_bubble")

        with col_b:
            st.markdown('<div class="section-label">Engagement Breakdown — Likes / Comments / Shares / Saves</div>', unsafe_allow_html=True)
            eng_totals = {"Likes": int(fdf["Likes"].sum()), "Comments": int(fdf["Comments"].sum()),
                          "Shares": int(fdf["Shares"].sum()), "Saves": int(fdf["Saves"].sum())}
            fig_donut = go.Figure(go.Pie(
                labels=list(eng_totals.keys()), values=list(eng_totals.values()), hole=0.55,
                marker=dict(colors=[AMBER, RED, BLUE, GREEN], line=dict(color="#0a0a0b", width=2)),
                textinfo="percent+label", textfont=dict(size=11),
                hovertemplate="<b>%{label}</b><br>Total: %{value:,}<br>Share: %{percent}<extra></extra>",
            ))
            fig_donut.update_layout(title="Engagement Type Split", showlegend=False, **DARK_LAYOUT)
            st.plotly_chart(fig_donut, use_container_width=True, key="eng_donut")

        # ── Campaign bar
        st.markdown('<div class="section-label">Campaign Type — Views & Engagement Rate</div>', unsafe_allow_html=True)
        if "Campaign" in fdf.columns and fdf["Campaign"].nunique() > 0:
            camp = fdf.groupby("Campaign", as_index=False).agg(
                Views=("Views","sum"), ER=("Engagement_Rate","mean"), Posts=("Campaign","count")
            ).sort_values("Views", ascending=True)
            fig_camp = px.bar(camp, y="Campaign", x="Views", orientation="h", text="Views",
                              color="ER", color_continuous_scale=[[0,"#1a1a1a"],[0.5,AMBER],[1.0,RED]])
            fig_camp.update_traces(
                texttemplate="%{text:,.0f}", textposition="outside", cliponaxis=False,
                hovertemplate="<b>%{y}</b><br>Total Views: %{x:,.0f}<extra></extra>"
            )
            fig_camp.update_layout(
                title="Campaign Performance — Total Views (color = Avg ER %)",
                xaxis_title="Total Views", yaxis_title="",
                coloraxis_colorbar=dict(title="Avg ER %", title_font=dict(size=10,color="#888"),
                                        tickfont=dict(size=10,color="#888"), thickness=10),
                **DARK_LAYOUT
            )
            fig_camp.update_xaxes(showgrid=False, zeroline=False, color="#555")
            fig_camp.update_yaxes(showgrid=False, zeroline=False, color="#aaa")
            st.plotly_chart(fig_camp, use_container_width=True, key="camp_bar")


# ── TAB 2 ─────────────────────────────────────────────────────────
with tab2:
    if fdf.empty:
        st.warning("No data for selected filters.")
    else:
        ai_df = fdf[fdf["AI_Generated_Caption"].isin(["Yes","No"])]
        ai_stats = ai_df.groupby("AI_Generated_Caption", as_index=False).agg(
            Avg_ER=("Engagement_Rate","mean"), Posts=("AI_Generated_Caption","count"))
        yes_er = float(ai_stats.loc[ai_stats["AI_Generated_Caption"]=="Yes","Avg_ER"].values[0]) \
                 if "Yes" in ai_stats["AI_Generated_Caption"].values else 0.0
        no_er  = float(ai_stats.loc[ai_stats["AI_Generated_Caption"]=="No","Avg_ER"].values[0]) \
                 if "No"  in ai_stats["AI_Generated_Caption"].values else 0.0
        diff = yes_er - no_er
        direction = "outperforming" if diff > 0 else "underperforming vs."
        insight_box(
            f"AI-generated captions are <b>{direction} human-written captions</b> by "
            f"<b>{abs(diff):.1f}%</b> in engagement rate. "
            + ("Scale up AI prompting." if diff > 0 else "Refine AI prompts — try product-specific language.")
        )

        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown('<div class="section-label">AI-Generated vs Human Captions — Avg Engagement Rate</div>', unsafe_allow_html=True)
            ai_colors = [AMBER if x=="Yes" else "#444" for x in ai_stats["AI_Generated_Caption"]]
            fig_ai = go.Figure()
            for _, row in ai_stats.iterrows():
                color = AMBER if row["AI_Generated_Caption"] == "Yes" else "#444"
                label = "AI Caption" if row["AI_Generated_Caption"] == "Yes" else "Human Caption"
                fig_ai.add_trace(go.Bar(
                    x=[row["AI_Generated_Caption"]],
                    y=[row["Avg_ER"]],
                    name=label,
                    marker_color=color,
                    text=[f"{row['Avg_ER']:.1f}%"],
                    textposition="outside",
                    hovertemplate=f"<b>{label}</b><br>Avg Engagement Rate: {row['Avg_ER']:.1f}%<br>Posts analyzed: {int(row['Posts'])}<extra></extra>",
                ))
            fig_ai.update_layout(
                title="AI vs Human Captions — Avg Engagement Rate",
                xaxis_title="Caption Type", yaxis_title="Avg Engagement Rate (%)",
                showlegend=False, **DARK_LAYOUT
            )
            fig_ai.update_xaxes(showgrid=False, zeroline=False, color="#aaa",
                                 ticktext=["Human Caption", "AI Caption"],
                                 tickvals=["No", "Yes"])
            fig_ai.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.04)", zeroline=False, color="#555")
            st.plotly_chart(fig_ai, use_container_width=True, key="ai_bar")

        with col2:
            st.markdown('<div class="section-label">Post Format — Avg Engagement Rate</div>', unsafe_allow_html=True)
            pt = fdf.groupby("Post_Type", as_index=False).agg(
                ER=("Engagement_Rate","mean"), Posts=("Post_Type","count")
            ).sort_values("ER", ascending=False)
            top_pt = pt.iloc[0]["Post_Type"] if not pt.empty else "—"
            fig_pt = go.Figure()
            for _, row in pt.iterrows():
                color = AMBER if row["Post_Type"] == top_pt else "#333"
                fig_pt.add_trace(go.Bar(
                    x=[row["Post_Type"]], y=[row["ER"]],
                    marker_color=color,
                    text=[f"{row['ER']:.1f}%"],
                    textposition="outside",
                    hovertemplate=f"<b>{row['Post_Type']}</b><br>Avg ER: {row['ER']:.1f}%<br>Posts: {int(row['Posts'])}<extra></extra>",
                    showlegend=False,
                ))
            fig_pt.update_layout(
                title="Post Format — Avg Engagement Rate",
                xaxis_title="Post Format", yaxis_title="Avg Engagement Rate (%)",
                showlegend=False, **DARK_LAYOUT
            )
            fig_pt.update_xaxes(showgrid=False, zeroline=False, color="#aaa")
            fig_pt.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.04)", zeroline=False, color="#555")
            st.plotly_chart(fig_pt, use_container_width=True, key="pt_bar")

        st.markdown('<div class="section-label">AI Caption × Post Format — Engagement Rate Heatmap</div>', unsafe_allow_html=True)
        insight_box(f"<b>{top_pt}</b> format has the highest avg engagement rate. Combined with AI captions, this is the recommended format for the next campaign cycle.", kind="blue")
        heat = (fdf[fdf["AI_Generated_Caption"].isin(["Yes","No"])]
                .groupby(["Post_Type","AI_Generated_Caption"], as_index=False)["Engagement_Rate"]
                .mean().round(2))
        heat_pivot = heat.pivot(index="Post_Type", columns="AI_Generated_Caption",
                                values="Engagement_Rate").fillna(0)
        fig_heat = px.imshow(heat_pivot,
                             color_continuous_scale=[[0,"#111113"],[0.5,"#7c2d12"],[1.0,AMBER]],
                             text_auto=".1f",
                             labels=dict(x="AI Caption Used", y="Post Format", color="Avg ER %"),
                             aspect="auto")
        fig_heat.update_traces(
            textfont=dict(size=13, color="#fff"),
            hovertemplate="<b>%{y}</b> · AI Caption: <b>%{x}</b><br>Avg Engagement Rate: <b>%{z:.1f}%</b><extra></extra>"
        )
        fig_heat.update_layout(
            title="Engagement Rate by Format × AI Caption",
            **DARK_LAYOUT
        )
        fig_heat.update_coloraxes(colorbar=dict(thickness=10, tickfont=dict(size=10,color="#888"),
                                                title=dict(text="Avg ER %", font=dict(size=10,color="#888"))))
        st.plotly_chart(fig_heat, use_container_width=True, key="heat_map")


# ── TAB 3 ─────────────────────────────────────────────────────────
with tab3:
    if fdf.empty:
        st.warning("No data for selected filters.")
    else:
        prod = fdf.groupby("Product_Featured", as_index=False).agg(
            Views=("Views","sum"), ER=("Engagement_Rate","mean"),
            Posts=("Product_Featured","count"), Engagements=("Total_Engagements","sum")
        ).sort_values("Views", ascending=False)

        top_prod    = prod.iloc[0]["Product_Featured"] if not prod.empty else "—"
        top_er_prod = top_val(fdf.groupby("Product_Featured")["Engagement_Rate"].mean())

        c1,c2 = st.columns(2)
        with c1: kpi("Top Product (Views)", top_prod,    hint="Highest total reach")
        with c2: kpi("Top Product (ER)",    top_er_prod, hint="Most engaging audience", accent=True)

        insight_box(
            f"<b>{top_prod}</b> dominates in raw reach — ideal for awareness campaigns. "
            f"<b>{top_er_prod}</b> generates the strongest community response, best for "
            f"<b>conversion-focused content</b> like testimonials and installation guides."
        )

        # ── Product bar — using go.Bar so colors apply correctly
        st.markdown('<div class="section-label">Total Views per Product</div>', unsafe_allow_html=True)
        prod_sorted = prod.sort_values("Views", ascending=True)
        fig_prod = go.Figure()
        for _, row in prod_sorted.iterrows():
            color = AMBER if row["Product_Featured"] == top_prod else "#2a2a2e"
            fig_prod.add_trace(go.Bar(
                y=[row["Product_Featured"]], x=[row["Views"]],
                orientation="h",
                marker_color=color,
                text=[f"{int(row['Views']):,}"],
                textposition="outside",
                hovertemplate=f"<b>{row['Product_Featured']}</b><br>Total Views: {int(row['Views']):,}<br>Avg ER: {row['ER']:.1f}%<br>Posts: {int(row['Posts'])}<extra></extra>",
                showlegend=False,
            ))
        fig_prod.update_layout(
            title="Total Views per Product (amber = top performer)",
            xaxis_title="Total Views", yaxis_title="",
            showlegend=False, **DARK_LAYOUT
        )
        fig_prod.update_xaxes(showgrid=False, zeroline=False, color="#555")
        fig_prod.update_yaxes(showgrid=False, zeroline=False, color="#aaa")
        st.plotly_chart(fig_prod, use_container_width=True, key="prod_bar")

        # ── Product bubble
        st.markdown('<div class="section-label">Product — Views vs Engagement Rate (bubble size = post count)</div>', unsafe_allow_html=True)
        fig_sc = go.Figure()
        for _, row in prod.iterrows():
            color = AMBER if row["Product_Featured"] == top_prod else BLUE
            fig_sc.add_trace(go.Scatter(
                x=[row["Views"]], y=[row["ER"]],
                mode="markers+text",
                marker=dict(size=max(row["Posts"] * 2, 12), color=color,
                            line=dict(color="#333", width=1), opacity=0.85),
                text=[row["Product_Featured"]],
                textposition="top center",
                textfont=dict(size=10, color="#ccc"),
                hovertemplate=f"<b>{row['Product_Featured']}</b><br>Total Views: {int(row['Views']):,}<br>Avg ER: {row['ER']:.1f}%<br>Posts: {int(row['Posts'])}<extra></extra>",
                showlegend=False,
            ))
        fig_sc.update_layout(
            title="Views vs Engagement Rate by Product (bubble size = post count)",
            xaxis_title="Total Views", yaxis_title="Avg Engagement Rate (%)",
            showlegend=False, **DARK_LAYOUT
        )
        fig_sc.update_xaxes(showgrid=False, zeroline=False, color="#555")
        fig_sc.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.04)", zeroline=False, color="#555")
        st.plotly_chart(fig_sc, use_container_width=True, key="prod_bubble")


# ── TAB 4 ─────────────────────────────────────────────────────────
with tab4:
    if fdf.empty:
        st.warning("No data for selected filters.")
    else:
        st.markdown('<div class="section-label">All Posts — Sorted by Total Engagements</div>', unsafe_allow_html=True)
        display_cols = ["Date","Platform","Product_Featured","Post_Type","Campaign",
                        "Views","Likes","Comments","Shares","Saves",
                        "Total_Engagements","Engagement_Rate","AI_Generated_Caption"]
        display_cols = [c for c in display_cols if c in fdf.columns]
        st.dataframe(fdf[display_cols].sort_values("Total_Engagements", ascending=False).reset_index(drop=True),
                     use_container_width=True, hide_index=True)
        csv_out = fdf[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Download filtered data as CSV", data=csv_out,
                           file_name="kellermann_filtered.csv", mime="text/csv", key="dl_csv")