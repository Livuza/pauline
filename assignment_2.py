import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import warnings

warnings.filterwarnings("ignore")

# ----------------------------------------------------------------------------
# Page configuration
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Bank Churn Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Shared colour palette so every chart looks consistent
CHURN_COLORS = {0: "#2E86AB", 1: "#E63946"}
SEQ_COLOR = px.colors.sequential.Blues
PLOT_TEMPLATE = "plotly_white"

# ----------------------------------------------------------------------------
# Light styling touch-ups
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        .block-container {padding-top: 2rem; padding-bottom: 2rem;}
        [data-testid="stMetricValue"] {font-size: 1.8rem;}
        h1, h2, h3 {color: #1d3557;}
        .stTabs [data-baseweb="tab-list"] {gap: 8px;}
        .stTabs [data-baseweb="tab"] {
            padding: 8px 18px;
            background-color: #f1f5f9;
            border-radius: 8px 8px 0 0;
        }
        .stTabs [aria-selected="true"] {background-color: #dbeafe;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------------
@st.cache_data
def load_data():
    url = (
        "https://raw.githubusercontent.com/Livuza/ADS-April-2021/"
        "main/Assignments/Assignment%202/banking_churn.csv"
    )
    return pd.read_csv(url)


df_raw = load_data()
df = df_raw.copy()

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.title("🏦 Bank Churn Analysis Dashboard")
st.caption(
    "An interactive overview of customer churn — explore the drivers behind "
    "why customers stay or leave."
)
st.divider()

# ----------------------------------------------------------------------------
# Sidebar filters
# ----------------------------------------------------------------------------
st.sidebar.header("⚙️ Filters")
st.sidebar.caption("Refine the dataset and every chart updates instantly.")

if "Geography" in df.columns:
    geography = st.sidebar.multiselect(
        "Geography",
        options=sorted(df["Geography"].unique()),
        default=sorted(df["Geography"].unique()),
    )
    df = df[df["Geography"].isin(geography)]

if "Gender" in df.columns:
    gender = st.sidebar.multiselect(
        "Gender",
        options=sorted(df["Gender"].unique()),
        default=sorted(df["Gender"].unique()),
    )
    df = df[df["Gender"].isin(gender)]

if "Age" in df.columns:
    age_min, age_max = int(df_raw["Age"].min()), int(df_raw["Age"].max())
    age_range = st.sidebar.slider(
        "Age range",
        min_value=age_min,
        max_value=age_max,
        value=(age_min, age_max),
    )
    df = df[df["Age"].between(*age_range)]

st.sidebar.divider()
st.sidebar.metric("Rows after filtering", f"{len(df):,}")

# Guard against an empty selection
if df.empty:
    st.warning("No records match the current filters. Try widening your selection.")
    st.stop()

# ----------------------------------------------------------------------------
# Key metrics
# ----------------------------------------------------------------------------
st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Customers", f"{len(df):,}")

if "Exited" in df.columns:
    churned = int(df["Exited"].sum())
    churn_rate = df["Exited"].mean() * 100
    retention_rate = 100 - churn_rate
    col2.metric("Churned Customers", f"{churned:,}")
    col3.metric("Churn Rate", f"{churn_rate:.1f}%")
    col4.metric("Retention Rate", f"{retention_rate:.1f}%")
elif "Balance" in df.columns:
    col2.metric("Average Balance", f"${df['Balance'].mean():,.0f}")

st.divider()

# ----------------------------------------------------------------------------
# Tabbed content
# ----------------------------------------------------------------------------
tab_overview, tab_demographics, tab_financials, tab_data = st.tabs(
    ["🔎 Overview", "👥 Demographics", "💰 Financials", "📁 Data"]
)

# --- Overview tab -----------------------------------------------------------
with tab_overview:
    if "Exited" in df.columns:
        left, right = st.columns(2)

        with left:
            st.markdown("##### Customer Churn Distribution")
            churn_counts = df["Exited"].value_counts().reset_index()
            churn_counts.columns = ["Exited", "Count"]
            churn_counts["Status"] = churn_counts["Exited"].map(
                {0: "Retained", 1: "Churned"}
            )
            fig = px.pie(
                churn_counts,
                values="Count",
                names="Status",
                hole=0.45,
                color="Status",
                color_discrete_map={"Retained": "#2E86AB", "Churned": "#E63946"},
                template=PLOT_TEMPLATE,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)

        with right:
            if "Geography" in df.columns:
                st.markdown("##### Churn Rate by Geography")
                geo = df.groupby("Geography")["Exited"].mean().reset_index()
                geo["Exited"] *= 100
                fig = px.bar(
                    geo.sort_values("Exited"),
                    x="Exited",
                    y="Geography",
                    orientation="h",
                    text=geo.sort_values("Exited")["Exited"].round(1),
                    color="Exited",
                    color_continuous_scale=SEQ_COLOR,
                    template=PLOT_TEMPLATE,
                    labels={"Exited": "Churn Rate (%)"},
                )
                fig.update_traces(texttemplate="%{text}%", textposition="outside")
                fig.update_layout(coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No 'Exited' column found — churn overview unavailable.")

# --- Demographics tab -------------------------------------------------------
with tab_demographics:
    cols = st.columns(2)

    if "Gender" in df.columns and "Exited" in df.columns:
        with cols[0]:
            st.markdown("##### Churn Rate by Gender")
            gender_df = df.groupby("Gender")["Exited"].mean().reset_index()
            gender_df["Exited"] *= 100
            fig = px.bar(
                gender_df,
                x="Gender",
                y="Exited",
                text=gender_df["Exited"].round(1),
                color="Gender",
                template=PLOT_TEMPLATE,
                labels={"Exited": "Churn Rate (%)"},
            )
            fig.update_traces(texttemplate="%{text}%", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

    if "Age" in df.columns:
        with cols[1]:
            st.markdown("##### Age Distribution")
            color_arg = {"color": "Exited"} if "Exited" in df.columns else {}
            fig = px.histogram(
                df,
                x="Age",
                nbins=20,
                template=PLOT_TEMPLATE,
                color_discrete_sequence=["#2E86AB"],
                **color_arg,
            )
            st.plotly_chart(fig, use_container_width=True)

# --- Financials tab ---------------------------------------------------------
with tab_financials:
    cols = st.columns(2)

    if "Balance" in df.columns:
        with cols[0]:
            st.markdown("##### Balance Distribution")
            fig = px.histogram(
                df,
                x="Balance",
                nbins=30,
                template=PLOT_TEMPLATE,
                color_discrete_sequence=["#457B9D"],
            )
            st.plotly_chart(fig, use_container_width=True)

    if "CreditScore" in df.columns and "Exited" in df.columns:
        with cols[1]:
            st.markdown("##### Credit Score by Churn Status")
            box_df = df.copy()
            box_df["Status"] = box_df["Exited"].map({0: "Retained", 1: "Churned"})
            fig = px.box(
                box_df,
                x="Status",
                y="CreditScore",
                color="Status",
                color_discrete_map={"Retained": "#2E86AB", "Churned": "#E63946"},
                template=PLOT_TEMPLATE,
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### Correlation Heatmap")
    numeric_df = df.select_dtypes(include=np.number)
    corr = numeric_df.corr()
    fig = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        template=PLOT_TEMPLATE,
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Data tab ---------------------------------------------------------------
with tab_data:
    # Quick shape summary
    info1, info2, info3 = st.columns(3)
    info1.metric("Rows", f"{df.shape[0]:,}")
    info2.metric("Columns", f"{df.shape[1]:,}")
    missing = int(df.isna().sum().sum())
    info3.metric("Missing values", f"{missing:,}")

    st.divider()

    # Build per-column number formatting so currency/score columns read cleanly
    money_cols = [c for c in ("Balance", "EstimatedSalary") if c in df.columns]
    column_config = {
        c: st.column_config.NumberColumn(c, format="$%,.0f") for c in money_cols
    }
    if "Exited" in df.columns:
        column_config["Exited"] = st.column_config.NumberColumn("Exited", format="%d")

    st.markdown("##### Dataset Preview")
    search = st.text_input(
        "Search", placeholder="Filter rows by any text value…", label_visibility="collapsed"
    )
    preview = df
    if search:
        mask = df.astype(str).apply(
            lambda row: row.str.contains(search, case=False, na=False)
        ).any(axis=1)
        preview = df[mask]
        st.caption(f"{len(preview):,} matching row(s)")

    st.dataframe(
        preview,
        use_container_width=True,
        hide_index=True,
        height=420,
        column_config=column_config,
    )

    with st.expander("📋 Column overview"):
        col_info = pd.DataFrame(
            {
                "Column": df.columns,
                "Type": df.dtypes.astype(str).values,
                "Non-null": df.notna().sum().values,
                "Unique": [df[c].nunique() for c in df.columns],
            }
        )
        st.dataframe(col_info, use_container_width=True, hide_index=True)

    with st.expander("📈 Summary statistics"):
        st.dataframe(
            df.describe().T.style.format("{:,.2f}"),
            use_container_width=True,
        )

    st.divider()
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Data",
        data=csv,
        file_name="bank_churn_filtered.csv",
        mime="text/csv",
    )

st.divider()
st.caption("Built with Streamlit & Plotly · Bank Churn Analysis")
