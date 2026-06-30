# #%matplotlib inline
# import pandas as pd
# #from matplotlib import plotly as plt
# import numpy as np
# import streamlit as st
# import warnings
# warnings.filterwarnings("ignore")
# url = "https://raw.githubusercontent.com/Livuza/ADS-April-2021/main/Assignments/Assignment%202/banking_churn.csv"
# banking_churn = pd.read_csv(url)
# st.write(banking_churn.head())
# st.title("Bank Churn")


import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import warnings

warnings.filterwarnings("ignore")

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(
    page_title="Bank Churn Dashboard",
    page_icon="🏦",
    layout="wide"
)

# ---------------------------
# Load Data
# ---------------------------
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Livuza/ADS-April-2021/main/Assignments/Assignment%202/banking_churn.csv"
    return pd.read_csv(url)

df = load_data()

# ---------------------------
# Title
# ---------------------------
st.title("🏦 Bank Churn Analysis Dashboard")
st.markdown("Interactive dashboard for analyzing customer churn.")

# ---------------------------
# Sidebar Filters
# ---------------------------
st.sidebar.header("Filters")

if "Geography" in df.columns:
    geography = st.sidebar.multiselect(
        "Select Geography",
        options=df["Geography"].unique(),
        default=df["Geography"].unique()
    )
    df = df[df["Geography"].isin(geography)]

if "Gender" in df.columns:
    gender = st.sidebar.multiselect(
        "Select Gender",
        options=df["Gender"].unique(),
        default=df["Gender"].unique()
    )
    df = df[df["Gender"].isin(gender)]

# ---------------------------
# Metrics
# ---------------------------
st.subheader("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Customers", len(df))

with col2:
    if "Exited" in df.columns:
        churned = df["Exited"].sum()
        st.metric("Churned Customers", churned)

with col3:
    if "Exited" in df.columns:
        churn_rate = (df["Exited"].mean()) * 100
        st.metric("Churn Rate (%)", f"{churn_rate:.2f}")

with col4:
    if "Balance" in df.columns:
        st.metric("Average Balance", f"{df['Balance'].mean():,.2f}")

# ---------------------------
# Dataset Preview
# ---------------------------
st.subheader("Dataset Preview")
st.dataframe(df.head())

# ---------------------------
# Churn Distribution
# ---------------------------
if "Exited" in df.columns:
    st.subheader("Customer Churn Distribution")

    churn_counts = df["Exited"].value_counts().reset_index()
    churn_counts.columns = ["Exited", "Count"]

    fig = px.pie(
        churn_counts,
        values="Count",
        names="Exited",
        title="Churn vs Non-Churn"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Geography Analysis
# ---------------------------
if "Geography" in df.columns and "Exited" in df.columns:
    st.subheader("Churn by Geography")

    geo = (
        df.groupby("Geography")["Exited"]
        .mean()
        .reset_index()
    )

    geo["Exited"] *= 100

    fig = px.bar(
        geo,
        x="Geography",
        y="Exited",
        title="Churn Rate by Geography (%)"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Gender Analysis
# ---------------------------
if "Gender" in df.columns and "Exited" in df.columns:
    st.subheader("Churn by Gender")

    gender_df = (
        df.groupby("Gender")["Exited"]
        .mean()
        .reset_index()
    )

    gender_df["Exited"] *= 100

    fig = px.bar(
        gender_df,
        x="Gender",
        y="Exited",
        title="Churn Rate by Gender (%)"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Age Distribution
# ---------------------------
if "Age" in df.columns:
    st.subheader("Customer Age Distribution")

    fig = px.histogram(
        df,
        x="Age",
        nbins=20,
        title="Age Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Balance Distribution
# ---------------------------
if "Balance" in df.columns:
    st.subheader("Balance Distribution")

    fig = px.histogram(
        df,
        x="Balance",
        nbins=30,
        title="Customer Balance Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Correlation Matrix
# ---------------------------
st.subheader("Correlation Matrix")

numeric_df = df.select_dtypes(include=np.number)

corr = numeric_df.corr()

fig = px.imshow(
    corr,
    text_auto=True,
    aspect="auto",
    title="Correlation Heatmap"
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Summary Statistics
# ---------------------------
st.subheader("Summary Statistics")
st.dataframe(df.describe())

# ---------------------------
# Download Data
# ---------------------------
csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data",
    data=csv,
    file_name="bank_churn_filtered.csv",
    mime="text/csv"
)