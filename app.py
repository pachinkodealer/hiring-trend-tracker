import pandas as pd
import plotly.express as px
import streamlit as st
from collections import Counter

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Job Market Intelligence",
    page_icon="📊",
    layout="wide",
)

# ── Load data ─────────────────────────────────────────────────────────────────
STATE_ABBREV = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
    'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
    'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY', 'District of Columbia': 'DC',
}

COUNTY_STATE = {
    'Clark County': 'NV', 'Chester County': 'PA', 'Richland County': 'SC',
    'Hudson County': 'NJ', 'Mecklenburg County': 'NC', 'Cumberland County': 'PA',
    'Kosciusko County': 'IN', 'Oakland County': 'MI', 'Davidson County': 'TN',
    'Minnehaha County': 'SD', 'Saint Louis County': 'MO', 'Maricopa County': 'AZ',
    'Madison County': 'AL', 'Lamoille County': 'VT', 'Cobb County': 'GA',
    'Los Angeles County': 'CA', 'Cook County': 'IL', 'Harris County': 'TX',
    'Middlesex County': 'NJ', 'Nassau County': 'NY', 'Suffolk County': 'NY',
    'Fairfax County': 'VA', 'Wake County': 'NC', 'King County': 'WA',
    'Orange County': 'CA', 'San Diego County': 'CA', 'Alameda County': 'CA',
    'Santa Clara County': 'CA', 'Bergen County': 'NJ', 'Essex County': 'NJ',
    'Morris County': 'NJ', 'Hennepin County': 'MN', 'Montgomery County': 'MD',
    'Fulton County': 'GA', 'Denver County': 'CO', 'Multnomah County': 'OR',
    'Travis County': 'TX', 'Dallas County': 'TX', 'Tarrant County': 'TX',
    'Wayne County': 'MI', 'Allegheny County': 'PA', 'Franklin County': 'OH',
    'Hamilton County': 'OH', 'Broward County': 'FL', 'Miami-Dade County': 'FL',
    'Palm Beach County': 'FL', 'Hillsborough County': 'FL', 'Pinellas County': 'FL',
}

def extract_state(location):
    if pd.isna(location):
        return None
    # Format: "StateName, US"
    import re
    match = re.match(r'^(.+),\s*US$', str(location))
    if match:
        state_name = match.group(1).strip()
        return STATE_ABBREV.get(state_name)
    # Format: "City, County Name County"
    parts = str(location).split(',')
    if len(parts) >= 2:
        county = parts[-1].strip()
        if county in COUNTY_STATE:
            return COUNTY_STATE[county]
    return None

@st.cache_data
def load_jobs():
    df = pd.read_csv("data/jobs_data.csv", parse_dates=["created"])
    df["salary_avg"] = (df["salary_min"] + df["salary_max"]) / 2
    df["month"] = df["created"].dt.to_period("M").astype(str)
    df["state"] = df["location"].apply(extract_state)
    return df

@st.cache_data
def load_layoffs():
    df = pd.read_csv("data/layoffs.csv", parse_dates=["date"])
    df["total_laid_off"] = pd.to_numeric(df["total_laid_off"], errors="coerce")
    df["percentage_laid_off"] = pd.to_numeric(df["percentage_laid_off"], errors="coerce")
    df["funds_raised"] = pd.to_numeric(df["funds_raised"], errors="coerce")
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df

jobs_df   = load_jobs()
layoff_df = load_layoffs()

# ── Skills extraction ─────────────────────────────────────────────────────────
SKILLS = [
    "python", "sql", "tableau", "excel", "power bi", "r",
    "machine learning", "spark", "aws", "azure", "snowflake",
    "dbt", "airflow", "pandas", "scikit-learn", "tensorflow",
]

def extract_skills(descriptions):
    counts = Counter()
    for desc in descriptions.dropna():
        desc_lower = desc.lower()
        for skill in SKILLS:
            if skill in desc_lower:
                counts[skill] += 1
    return counts

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Hiring Filters section - blue tags */
[data-testid="stSidebar"] .stMultiSelect:nth-of-type(1) span[data-baseweb="tag"],
[data-testid="stSidebar"] .stMultiSelect:nth-of-type(2) span[data-baseweb="tag"] {
    background-color: #1D4ED8 !important;
    color: white !important;
}
/* Refresh button styling */
[data-testid="stSidebar"] { border-right: 1px solid #e5e7eb; }
</style>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📈 Hiring Trends", "📉 Layoff Tracker", "🔍 Market Overview"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — HIRING TRENDS
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.title("📈 Global Data & Analytics Hiring Trends")
    st.caption("Tracking Data Analyst, Data Scientist, BI & ML roles across Finance and Tech in 6 countries")
    last_collected = pd.to_datetime(jobs_df["collected_at"]).max()
    info_col, btn_col = st.columns([5, 1])
    with info_col:
        st.info(f"📡 **Data Source:** [Adzuna Jobs API](https://www.adzuna.com) · Live job postings aggregated across Finance and IT categories in 6 countries (US, UK, Canada, Australia, India, Singapore) · **Last refreshed: {last_collected.strftime('%B %d, %Y at %I:%M %p')}**", icon=None)
    with btn_col:
        if st.button("🔄 Refresh Data", use_container_width=True):
            import subprocess, sys
            with st.spinner("Fetching latest job postings..."):
                result = subprocess.run(
                    [sys.executable, "data_collector.py"],
                    capture_output=True, text=True
                )
            if result.returncode == 0:
                st.cache_data.clear()
                st.success("Data refreshed!")
                st.rerun()
            else:
                st.error("Refresh failed. Check API credentials.")

    # Sidebar filters
    st.sidebar.title("Hiring Filters")
    all_countries = sorted(jobs_df["country"].dropna().unique()) if "country" in jobs_df.columns else []
    selected_countries = st.sidebar.multiselect(
        "Country", options=all_countries, default=all_countries
    )
    all_categories = sorted(jobs_df["category"].dropna().unique())
    selected_categories = st.sidebar.multiselect(
        "Industry Category", options=all_categories, default=all_categories
    )
    all_titles = sorted(jobs_df["search_term"].dropna().unique())
    selected_titles = st.sidebar.multiselect(
        "Role Type", options=all_titles, default=all_titles
    )

    filtered = jobs_df[
        jobs_df["category"].isin(selected_categories) &
        jobs_df["search_term"].isin(selected_titles)
    ]
    if selected_countries and "country" in jobs_df.columns:
        filtered = filtered[filtered["country"].isin(selected_countries)]

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Postings", f"{len(filtered):,}")
    k2.metric("Unique Companies", f"{filtered['company'].nunique():,}")
    k3.metric("Avg Salary", f"${filtered['salary_avg'].mean():,.0f}" if filtered["salary_avg"].notna().any() else "N/A")
    k4.metric("Roles Tracked", filtered["search_term"].nunique())
    st.divider()

    # Row 1
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Postings by Role Type")
        role_counts = filtered["search_term"].value_counts().reset_index()
        role_counts.columns = ["Role", "Postings"]
        fig = px.bar(role_counts, x="Postings", y="Role", orientation="h",
                     color="Postings", color_continuous_scale="Blues")
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True, key="fig_roles_bar")

    with c2:
        st.subheader("Postings by Industry")
        cat_counts = filtered["category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Postings"]
        fig2 = px.pie(cat_counts, names="Category", values="Postings",
                      color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig2, use_container_width=True, key="fig_industry_pie")

    # Row 2
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Most In-Demand Skills")
        skill_counts = extract_skills(filtered["description"])
        skill_df = pd.DataFrame(skill_counts.most_common(12), columns=["Skill", "Mentions"])
        fig3 = px.bar(skill_df, x="Mentions", y="Skill", orientation="h",
                      color="Mentions", color_continuous_scale="Teal")
        fig3.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True, key="fig_skills")

    with c4:
        st.subheader("Salary Distribution")
        salary_df = filtered[filtered["salary_avg"].notna() & (filtered["salary_avg"] > 20000)]
        if not salary_df.empty:
            fig4 = px.histogram(salary_df, x="salary_avg", nbins=30,
                                color_discrete_sequence=["#1D4ED8"],
                                labels={"salary_avg": "Avg Salary ($)"})
            fig4.update_layout(bargap=0.1)
            st.plotly_chart(fig4, use_container_width=True, key="fig_salary")
        else:
            st.info("Not enough salary data for selected filters.")

    # Row 3
    st.subheader("Top Hiring Companies")
    top_companies = filtered["company"].value_counts().head(15).reset_index()
    top_companies.columns = ["Company", "Postings"]
    fig5 = px.bar(top_companies, x="Company", y="Postings",
                  color="Postings", color_continuous_scale="Blues")
    fig5.update_layout(coloraxis_showscale=False, xaxis_tickangle=-30)
    st.plotly_chart(fig5, use_container_width=True, key="fig_companies")

    # Row 4 — Global hiring map
    st.subheader("Hiring by Country")
    if "country" in filtered.columns:
        country_hire_df = filtered["country"].value_counts().reset_index()
        country_hire_df.columns = ["Country", "Postings"]
        fig6 = px.choropleth(
            country_hire_df, locations="Country", locationmode="country names",
            color="Postings", color_continuous_scale="Blues",
            labels={"Postings": "Job Postings"},
        )
        fig6.update_layout(geo=dict(showframe=False, showcoastlines=True))
        st.plotly_chart(fig6, use_container_width=True, key="fig_state_map")
    else:
        st.info("Run the collector to get global data.")

    st.divider()
    st.caption("Built by Ian Lee · Data sourced from Adzuna Jobs API (adzuna.com) · Covers Finance & IT categories across US, UK, Canada, Australia, India & Singapore · Updated on demand")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — LAYOFF TRACKER
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.title("📉 Tech Layoff Tracker")
    st.caption("Tracking global tech & finance layoffs from 2022 to present")
    layoff_start = layoff_df["date"].min().strftime("%B %Y")
    layoff_end = layoff_df["date"].max().strftime("%B %Y")
    st.info(f"📡 **Data Source:** [layoffs.fyi](https://layoffs.fyi) by Roger Lee · Crowd-sourced layoff data covering 4,400+ events across industries and countries · **Data range: {layoff_start} – {layoff_end}**", icon=None)

    # Sidebar filters
    st.sidebar.title("Layoff Filters")
    all_industries = sorted(layoff_df["industry"].dropna().unique())
    selected_industries = st.sidebar.multiselect(
        "Industry", options=all_industries, default=all_industries
    )
    all_years = sorted(layoff_df["year"].dropna().unique().astype(int), reverse=True)
    selected_years = st.sidebar.multiselect(
        "Year", options=all_years, default=all_years
    )

    lay_filtered = layoff_df[
        layoff_df["industry"].isin(selected_industries) &
        layoff_df["year"].isin(selected_years)
    ]

    # KPIs
    l1, l2, l3, l4 = st.columns(4)
    l1.metric("Total Laid Off", f"{lay_filtered['total_laid_off'].sum():,.0f}")
    l2.metric("Companies Affected", f"{lay_filtered['company'].nunique():,}")
    l3.metric("Industries Hit", f"{lay_filtered['industry'].nunique():,}")
    l4.metric("Countries", f"{lay_filtered['country'].nunique():,}")
    st.divider()

    # Row 1 — Layoffs over time + by industry
    r1, r2 = st.columns(2)
    with r1:
        st.subheader("Layoffs Over Time")
        time_df = (
            lay_filtered.groupby("month")["total_laid_off"]
            .sum()
            .reset_index()
            .sort_values("month")
        )
        fig_time = px.line(time_df, x="month", y="total_laid_off",
                           markers=True, color_discrete_sequence=["#DC2626"],
                           labels={"month": "Month", "total_laid_off": "Total Laid Off"})
        fig_time.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_time, use_container_width=True, key="fig_layoff_time")

    with r2:
        st.subheader("Layoffs by Industry")
        ind_df = (
            lay_filtered.groupby("industry")["total_laid_off"]
            .sum()
            .reset_index()
            .sort_values("total_laid_off", ascending=False)
            .head(12)
        )
        fig_ind = px.bar(ind_df, x="total_laid_off", y="industry", orientation="h",
                         color="total_laid_off", color_continuous_scale="Reds")
        fig_ind.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_ind, use_container_width=True, key="fig_layoff_ind")

    # Row 2 — Top companies + Layoffs by stage
    r3, r4 = st.columns(2)
    with r3:
        st.subheader("Top Companies by Layoffs")
        co_df = (
            lay_filtered.groupby("company")["total_laid_off"]
            .sum()
            .reset_index()
            .sort_values("total_laid_off", ascending=False)
            .head(15)
        )
        fig_co = px.bar(co_df, x="company", y="total_laid_off",
                        color="total_laid_off", color_continuous_scale="Reds",
                        labels={"company": "Company", "total_laid_off": "Laid Off"})
        fig_co.update_layout(coloraxis_showscale=False, xaxis_tickangle=-30)
        st.plotly_chart(fig_co, use_container_width=True, key="fig_layoff_co")

    with r4:
        st.subheader("Layoffs by Company Stage")
        stage_df = (
            lay_filtered.groupby("stage")["total_laid_off"]
            .sum()
            .reset_index()
            .sort_values("total_laid_off", ascending=False)
            .dropna()
        )
        fig_stage = px.pie(stage_df, names="stage", values="total_laid_off",
                           color_discrete_sequence=px.colors.sequential.Reds_r)
        st.plotly_chart(fig_stage, use_container_width=True, key="fig_layoff_stage")

    # Row 3 — Country map
    st.subheader("Layoffs by Country")
    country_df = (
        lay_filtered.groupby("country")["total_laid_off"]
        .sum()
        .reset_index()
        .sort_values("total_laid_off", ascending=False)
    )
    fig_map = px.choropleth(
        country_df, locations="country", locationmode="country names",
        color="total_laid_off", color_continuous_scale="Reds",
        labels={"total_laid_off": "Total Laid Off"},
    )
    st.plotly_chart(fig_map, use_container_width=True, key="fig_layoff_map")

    st.divider()
    st.caption("Built by Ian Lee · Data sourced from layoffs.fyi by Roger Lee · Dataset covers 4,400+ layoff events globally · Updated periodically")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — MARKET OVERVIEW (Overlay)
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.title("🔍 Market Overview")
    st.caption("Layoff activity vs. active job postings — the full picture of the data & analytics job market")
    st.info("📡 **Combined view** of layoffs.fyi historical data and live Adzuna job postings · Use this tab to understand where the market is headed, not just where it's been.", icon=None)

    st.divider()

    # ── Insight box ───────────────────────────────────────────────────────────
    total_postings  = len(jobs_df)
    total_layoffs   = int(layoff_df["total_laid_off"].sum())
    top_hiring_role = jobs_df["search_term"].value_counts().idxmax()
    top_hit_industry = layoff_df.groupby("industry")["total_laid_off"].sum().idxmax()

    st.subheader("📌 What the Data is Saying Right Now")
    i1, i2, i3, i4 = st.columns(4)
    countries_tracked = jobs_df["country"].nunique() if "country" in jobs_df.columns else 1
    i1.metric("Active Job Postings", f"{total_postings:,}", help="From Adzuna API")
    i2.metric("Total Layoffs (All Time)", f"{total_layoffs:,}", help="From layoffs.fyi")
    i3.metric("Most In-Demand Role", top_hiring_role.title())
    i4.metric("Countries Tracked", f"{countries_tracked}")

    # Plain English insight
    recent_layoffs = layoff_df[layoff_df["date"] >= layoff_df["date"].max() - pd.DateOffset(months=6)]
    recent_total = int(recent_layoffs["total_laid_off"].sum())
    st.success(
        f"📣 **Market Snapshot:** There are currently **{total_postings:,} open roles** in data & analytics "
        f"across finance and tech. Over the past 6 months, **{recent_total:,} workers** were laid off globally — "
        f"but hiring for **{top_hiring_role.title()}** roles remains active. "
        f"The **{top_hit_industry}** industry has seen the most cuts overall."
    )

    st.divider()

    # ── Overlay chart: Layoffs over time + hiring snapshot ────────────────────
    st.subheader("📊 Layoffs Over Time vs. Current Hiring Activity")

    # Layoffs timeline
    layoff_time = (
        layoff_df.groupby("month")["total_laid_off"]
        .sum()
        .reset_index()
        .sort_values("month")
        .rename(columns={"total_laid_off": "Value", "month": "Month"})
    )
    layoff_time["Metric"] = "Layoffs"

    # Job postings by created date
    jobs_time = (
        jobs_df[jobs_df["created"].notna()]
        .groupby(jobs_df["created"].dt.to_period("M").astype(str))
        .size()
        .reset_index()
        .rename(columns={"created": "Month", 0: "Value"})
    )
    jobs_time["Metric"] = "Job Postings"

    combined = pd.concat([layoff_time, jobs_time], ignore_index=True)

    fig_overlay = px.line(
        combined, x="Month", y="Value", color="Metric",
        markers=True,
        color_discrete_map={"Layoffs": "#DC2626", "Job Postings": "#1D4ED8"},
        labels={"Value": "Count", "Month": "Month"},
    )
    fig_overlay.update_layout(
        xaxis_tickangle=-45,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    st.plotly_chart(fig_overlay, use_container_width=True, key="fig_overlay")

    st.divider()

    # ── Side by side: top hiring roles vs top layoff industries ──────────────
    o1, o2 = st.columns(2)

    with o1:
        st.subheader("🟦 Most Hired Roles Right Now")
        role_df = jobs_df["search_term"].value_counts().reset_index()
        role_df.columns = ["Role", "Postings"]
        fig_roles = px.bar(role_df, x="Postings", y="Role", orientation="h",
                           color="Postings", color_continuous_scale="Blues")
        fig_roles.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_roles, use_container_width=True, key="fig_overview_roles")

    with o2:
        st.subheader("🟥 Most Impacted Industries by Layoffs")
        ind_overview = (
            layoff_df.groupby("industry")["total_laid_off"]
            .sum()
            .reset_index()
            .sort_values("total_laid_off", ascending=False)
            .head(10)
        )
        fig_ind_ov = px.bar(ind_overview, x="total_laid_off", y="industry", orientation="h",
                            color="total_laid_off", color_continuous_scale="Reds")
        fig_ind_ov.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_ind_ov, use_container_width=True, key="fig_overview_ind")

    st.divider()
    st.caption("Built by Ian Lee · Adzuna Jobs API + layoffs.fyi · Combined market intelligence dashboard")
