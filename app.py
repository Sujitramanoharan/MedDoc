import streamlit as st
import pandas as pd

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="Medical Report Analyzer", layout="wide")

st.title("🩺 Medical Report Analyzer")
st.write("Explain medical lab reports in simple language")

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data():
    labs = pd.read_csv("LABEVENTS.csv")
    lab_items = pd.read_csv("D_LABITEMS.csv")
    return labs, lab_items

labs, lab_items = load_data()

# -------------------------------
# Merge datasets
# -------------------------------
data = labs.merge(
    lab_items[['ITEMID', 'LABEL']],
    on='ITEMID',
    how='left'
)

# Keep only numeric lab results
data = data[data['VALUENUM'].notnull()]

# -------------------------------
# Normal ranges (manual for hackathon)
# -------------------------------
normal_ranges = {
    "Hemoglobin": (12, 16, "g/dL"),
    "Glucose": (70, 110, "mg/dL"),
    "White Blood Cells": (4, 11, "x10³/µL"),
    "Platelet Count": (150, 450, "x10³/µL"),
    "Creatinine": (0.6, 1.3, "mg/dL")
}

# -------------------------------
# Sidebar – Patient Selection
# -------------------------------
st.sidebar.header("Patient Selection")

patient_ids = data['SUBJECT_ID'].unique()
patient_id = st.sidebar.selectbox("Select Patient ID", patient_ids)

patient_data = data[data['SUBJECT_ID'] == patient_id]

st.subheader(f"Patient ID: {patient_id}")

# -------------------------------
# Analyze Lab Results
# -------------------------------
results = []

for test, (low, high, unit) in normal_ranges.items():
    test_data = patient_data[patient_data['LABEL'].str.contains(test, case=False, na=False)]
    
    if not test_data.empty:
        value = test_data.iloc[0]['VALUENUM']
        
        if value < low:
            status = "Low"
        elif value > high:
            status = "High"
        else:
            status = "Normal"
        
        results.append([test, value, unit, status])

results_df = pd.DataFrame(
    results,
    columns=["Test Name", "Value", "Unit", "Status"]
)

# -------------------------------
# Display Table
# -------------------------------
st.subheader("📊 Lab Results")

def highlight_status(val):
    if val == "Low" or val == "High":
        return "background-color: #ffcccc"
    return "background-color: #ccffcc"

if not results_df.empty:
    st.dataframe(
        results_df.style.applymap(highlight_status, subset=["Status"])
    )
else:
    st.warning("No common lab results found for this patient.")

# -------------------------------
# Simple Language Explanation
# -------------------------------
st.subheader("🧠 Patient-Friendly Explanation")

for _, row in results_df.iterrows():
    if row["Status"] != "Normal":
        st.markdown(f"**{row['Test Name']}** ({row['Status']})")
        
        if row["Status"] == "Low":
            st.write(
                f"Your {row['Test Name'].lower()} level is lower than normal. "
                "This may indicate a deficiency or underlying health issue. "
                "You may experience symptoms like tiredness or weakness."
            )
        else:
            st.write(
                f"Your {row['Test Name'].lower()} level is higher than normal. "
                "This could be due to infection, stress, or organ-related conditions. "
                "Medical follow-up is recommended."
            )

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("⚠️ This tool provides simplified explanations and is not a medical diagnosis.")
