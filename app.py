import streamlit as st
import json
from groq import Groq

# --- 1. SETUP THE AI ---
# Your Groq API Key is connected here!
client = Groq(api_key="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")

# --- 2. LOAD OUR FAKE DATABASE ---
with open('patient_data.json', 'r') as f:
    patient = json.load(f)

with open('insurance_rules.json', 'r') as f:
    rules = json.load(f)

# --- 3. CREATE THE AI AGENTS ---

def clinical_agent(prescription, patient_data):
    """This agent acts as the strict medical safety checker."""
    prompt = f"""
    You are a Chief Medical Officer AI. Your job is to prevent medical errors.
    
    PATIENT MEDICAL RECORD: {patient_data}
    DOCTOR'S PRESCRIPTION: {prescription}
    
    INSTRUCTIONS:
    1. Extract all drugs and procedures from the prescription.
    2. Check if any drug triggers the patient's listed allergies.
    3. Check if any drug or procedure is dangerous for the patient's chronic conditions (e.g., Kidney Disease, Diabetes).
    
    If there is ANY danger or mismatch, respond EXACTLY like this:
    🚨 CLINICAL VIOLATION: [State exactly what is dangerous and why].
    
    If it is 100% safe, respond EXACTLY like this:
    ✅ CLINICAL APPROVED: No allergies or condition conflicts detected.
    """
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
        temperature=0.1 # This makes the AI strict and stops it from guessing
    )
    return response.choices[0].message.content

def insurance_agent(prescription, rules_data):
    """This agent acts as the strict financial auditor."""
    prompt = f"""
    You are a strict Healthcare Insurance Auditor AI. Your job is to prevent denied claims.
    
    ACTIVE INSURANCE RULES: {rules_data}
    DOCTOR'S PRESCRIPTION: {prescription}
    
    INSTRUCTIONS:
    1. Read the prescription carefully.
    2. Cross-check EVERY item against the Active Insurance Rules provided above.
    3. Do NOT invent rules. ONLY use the rules provided in the text above.
    
    If the prescription violates ANY rule, respond EXACTLY like this:
    🛑 INSURANCE REJECTED: [State exactly which rule was broken and what the doctor must do instead].
    
    If the prescription follows all rules, respond EXACTLY like this:
    ✅ INSURANCE APPROVED: Complies with all known policy rules.
    """
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
        temperature=0.1 # This makes the AI strict and stops it from guessing
    )
    return response.choices[0].message.content


# --- 4. BUILD THE USER INTERFACE (STREAMLIT) ---

st.title("🏥 PrescriptoGuard AI")
st.write("Autonomous Medical & Financial Safety Net")

# Display the patient file on the screen
st.sidebar.header("Patient File Open:")
st.sidebar.json(patient)

# A text box for the doctor to type
prescription = st.text_area("Doctor, enter your prescription/treatment plan here:")

# A button to trigger the AI
if st.button("Submit Prescription"):
    
    st.write("🔍 **Agents Analyzing...**")
    
    # Run Agent 1
    with st.expander("🩺 Clinical Safety Agent"):
        clinical_result = clinical_agent(prescription, patient)
        st.write(clinical_result)
        
    # Run Agent 2
    with st.expander("💼 Financial & Insurance Agent"):
        insurance_result = insurance_agent(prescription, rules["HDFC Ergo"])
        st.write(insurance_result)
        
    # Final Decision Logic
    if "VIOLATION" in clinical_result or "REJECTED" in insurance_result:
        st.error("❌ PRESCRIPTION BLOCKED: Please revise based on agent feedback above.")
    else:
        st.success("✅ PRESCRIPTION APPROVED & SAVED TO BLOCKCHAIN AUDIT LOG.")