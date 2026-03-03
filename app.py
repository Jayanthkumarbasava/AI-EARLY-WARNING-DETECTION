# =====================================================
# IMPORTS
# =====================================================
import streamlit as st
import pandas as pd
import numpy as np
import psutil
import subprocess
import base64
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime
import os

from database import create_table, insert_data, load_data
from email_alert import send_email_alert

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="AI Early Warning System",
    layout="wide",
    page_icon="🚨"
)

# =====================================================
# CREATE TABLE
# =====================================================
create_table()

# =====================================================
# 🔔 FIXED ALERT SOUND FUNCTION (WORKING 100%)
# =====================================================
def play_alert_sound():
    try:

        if not os.path.exists("alert.mp3"):
            st.error("alert.mp3 file not found")
            return

        with open("alert.mp3", "rb") as f:
            audio_bytes = f.read()

        b64 = base64.b64encode(audio_bytes).decode()

        audio_html = f"""
        <audio autoplay loop>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """

        st.markdown(audio_html, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Audio error: {e}")

# =====================================================
# PREMIUM CSS
# =====================================================
st.markdown("""
<style>

.main {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    color:white;
}

h1, h2, h3 {
    color:white;
}

.stButton>button {
    background: linear-gradient(90deg,#00c6ff,#0072ff);
    color:white;
    border-radius:10px;
    height:3em;
    font-weight:bold;
    border:none;
}

footer {
    visibility:hidden;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# LOGIN SYSTEM
# =====================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def login():

    st.markdown("<h1 style='text-align:center;'>🔐 Secure Login</h1>", unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username == "admin" and password == "1234":

            st.session_state.logged_in = True
            st.success("Login Successful")
            st.rerun()

        else:
            st.error("Invalid Credentials")


def logout():
    st.session_state.logged_in = False
    st.rerun()


if not st.session_state.logged_in:
    login()
    st.stop()

col1, col2 = st.columns([10, 1])

with col2:
    if st.button("🚪 Logout"):
        logout()

# =====================================================
# HEADER
# =====================================================
st.markdown("""
<h1 style='text-align:center;'>🚨 AI Early Warning System</h1>
<h4 style='text-align:center; color:#ccc;'>Real-Time Intelligent Monitoring Dashboard</h4>
""", unsafe_allow_html=True)

# =====================================================
# SYSTEM DATA COLLECTION
# =====================================================
def get_system_data():

    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    errors = np.random.randint(0, 5)

    try:

        output = subprocess.check_output("ping google.com -n 1", shell=True).decode()

        if "time=" in output:
            latency = int(output.split("time=")[1].split("ms")[0])
        else:
            latency = 50

    except:
        latency = 50

    return {
        "CPU": cpu,
        "Memory": memory,
        "Disk": disk,
        "Latency": latency,
        "Errors": errors
    }

# =====================================================
# REFRESH BUTTON
# =====================================================
if st.button("🔄 Refresh Data"):
    st.rerun()

# =====================================================
# GET NEW DATA
# =====================================================
new_data = get_system_data()

# =====================================================
# LOAD OLD DATA
# =====================================================
rows = load_data()

df = pd.DataFrame(rows)

if not df.empty:

    df.columns = [
        "ID",
        "Timestamp",
        "CPU",
        "Memory",
        "Disk",
        "Latency",
        "Errors",
        "Prediction",
        "Probability"
    ]

# =====================================================
# CREATE FAILURE LABEL
# =====================================================
if not df.empty:

    df["Failure"] = (
        (df["CPU"] > 75) |
        (df["Memory"] > 90) |
        (df["Disk"] > 90)
    ).astype(int)

# =====================================================
# TRAIN AI MODEL
# =====================================================
prediction = 0
probability = 0.0

if not df.empty and df["Failure"].nunique() >= 2:

    X = df[["CPU", "Memory", "Disk", "Latency", "Errors"]]
    y = df["Failure"]

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42
    )

    model.fit(X, y)

    latest_input = pd.DataFrame([new_data])

    prediction = model.predict(latest_input)[0]

    probability = model.predict_proba(latest_input)[0][1]

# =====================================================
# INSERT NEW DATA INTO DATABASE
# =====================================================
insert_data(new_data, prediction, probability)

# reload updated data
rows = load_data()
df = pd.DataFrame(rows)

if df.empty:

    st.warning("Collecting data...")
    st.stop()

df.columns = [
    "ID",
    "Timestamp",
    "CPU",
    "Memory",
    "Disk",
    "Latency",
    "Errors",
    "Prediction",
    "Probability"
]

latest = df.iloc[0]

# =====================================================
# LIVE METRICS
# =====================================================
st.markdown("## 📊 Live System Metrics")

c1, c2, c3, c4 = st.columns(4)

c1.metric("CPU", f"{latest['CPU']} %")
c2.metric("Memory", f"{latest['Memory']} %")
c3.metric("Disk", f"{latest['Disk']} %")
c4.metric("Latency", f"{latest['Latency']} ms")

# =====================================================
# RISK ENGINE (FIXED)
# =====================================================
st.markdown("## 🔎 AI Risk Analysis")

cpu = latest["CPU"]
memory = latest["Memory"]
disk = latest["Disk"]

risk_score = latest["Probability"] * 100

# threshold logic
if cpu > 90 or memory > 95 or disk > 95:
    risk_level = "CRITICAL"

elif cpu > 80 or memory > 85 or disk > 85:
    risk_level = "HIGH"

elif cpu > 65 or memory > 70:
    risk_level = "MEDIUM"

else:
    risk_level = "LOW"

# AI override
if risk_score > 80:
    risk_level = "CRITICAL"

elif risk_score > 60 and risk_level != "CRITICAL":
    risk_level = "HIGH"

# =====================================================
# ALERT DISPLAY
# =====================================================
if risk_level in ["HIGH", "CRITICAL"]:

    st.error(f"🚨 {risk_level} RISK DETECTED")

    play_alert_sound()

    send_email_alert(cpu, memory, disk)

elif risk_level == "MEDIUM":

    st.warning("⚠️ MEDIUM RISK")

else:

    st.success("🟢 SYSTEM STABLE")

st.write(f"Risk Probability: {risk_score:.2f} %")
st.write(f"Risk Level: {risk_level}")

# =====================================================
# CHART
# =====================================================
st.markdown("## 📈 Usage History")

st.line_chart(df[["CPU", "Memory", "Disk"]])

# =====================================================
# DATABASE TABLE
# =====================================================
st.markdown("## 🗄️ Database Records")

st.dataframe(df, use_container_width=True)

# =====================================================
# FOOTER
# =====================================================
st.markdown("""
<hr>
<p style='text-align:center;color:gray'>
AI Monitoring System © 2026 | Designed by Jayanth Kumar
</p>
""", unsafe_allow_html=True)