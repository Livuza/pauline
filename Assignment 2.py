#%matplotlib inline
import pandas as pd
#from matplotlib import plotly as plt
import numpy as np
import streamlit as st
import warnings
warnings.filterwarnings("ignore")
url = "https://raw.githubusercontent.com/Livuza/ADS-April-2021/main/Assignments/Assignment%202/banking_churn.csv"
banking_churn = pd.read_csv(url)
st.write(banking_churn.head())
st.title("Bank Churn")
