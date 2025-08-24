import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Demo Personal Finance Tracker", layout="wide")

st.title("Demo Personal Finance Tracker (Web Preview)")

# Simulasi login
st.subheader("Login")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
login_btn = st.button("Login")

if login_btn:
    if username == "demo" and password == "demo":
        st.success("Login successful!")
    else:
        st.error("Incorrect username or password")

# Contoh data transaksi
data = pd.DataFrame({
    "Bulan": ["Jan", "Feb", "Mar"],
    "Pendapatan": [1000, 1200, 1100],
    "Pengeluaran": [800, 950, 900]
})

st.subheader("Laporan Bulanan")
st.dataframe(data)

# Grafik interaktif
fig = px.bar(data, x="Bulan", y=["Pendapatan", "Pengeluaran"], barmode="group")
st.plotly_chart(fig)

# Simulasi fitur premium
st.subheader("Fitur Premium")
st.write("- Upgrade to Premium (simulasi)")
st.write("- Export PDF / Excel (contoh data)")

# Link download APK
st.markdown("[Download APK Demo](https://link-apk-demo.com/PersonalFinanceTracker.apk)")
