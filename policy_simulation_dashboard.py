
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load simulation data
df = pd.read_csv("LMIC_Intervention_Simulation_Results.csv")

st.title("LMIC Policy Simulation Dashboard")

# Sidebar controls
st.sidebar.header("Simulated Intervention Levers")
audit_effect = st.sidebar.checkbox("Increase Audit Score", value=True)
ast_effect = st.sidebar.checkbox("Use Rapid AST", value=True)
therapy_adjustment = st.sidebar.checkbox("Apply Targeted Therapy", value=True)

# Apply logic to simulate MDR change
df_sim = df.copy()
if not therapy_adjustment:
    df_sim['Delta_MDR'] = 0
elif not (audit_effect or ast_effect):
    df_sim['Delta_MDR'] = df_sim['MDR_Pred_Targeted'] - df_sim['MDR_Pred_Targeted']
else:
    df_sim['Delta_MDR'] = df_sim['MDR_Pred_Targeted'] - df_sim['MDR_Pred_Intervention']

# Summary metrics
st.metric("Total Cases", len(df_sim))
st.metric("Predicted MDR (Baseline)", int(df_sim['MDR_Pred_Intervention'].sum()))
st.metric("Predicted MDR (After Intervention)", int(df_sim['MDR_Pred_Targeted'].sum()))
st.metric("Net MDR Change", int(df_sim['Delta_MDR'].sum()))

# Delta by Region
region_summary = df_sim.groupby("Region")["Delta_MDR"].sum().reset_index()
fig, ax = plt.subplots()
ax.bar(region_summary['Region'], region_summary['Delta_MDR'])
ax.set_title("Change in MDR by Region")
ax.axhline(0, color='gray', linestyle='--')
plt.xticks(rotation=45)
st.pyplot(fig)

# Feature explanation
st.subheader("Top Drivers of Policy Impact")
st.markdown("""
- **Audit_Score**: Higher score correlates with lower MDR
- **AST_Ordered**: Early AST use linked to targeted therapy
- **Therapy_Modified_After_AST**: Reduces inappropriate antibiotic use
- **ICU_Admission**, **APACHE_II_Score**: Higher severity = greater MDR risk
""")

# Visualize risk levels from prediction
st.subheader("MDR Risk Stratification")
if 'MDR_Probability' in df.columns:
    def risk_level(prob):
        if prob > 0.8:
            return 'Red'
        elif prob > 0.5:
            return 'Yellow'
        else:
            return 'Green'

    df['Risk_Level'] = df['MDR_Probability'].apply(risk_level)
    risk_counts = df['Risk_Level'].value_counts().reindex(['Green', 'Yellow', 'Red']).fillna(0)

    fig2, ax2 = plt.subplots()
    ax2.bar(risk_counts.index, risk_counts.values, color=['green', 'orange', 'red'])
    ax2.set_title("Risk Levels Among Patients")
    st.pyplot(fig2)
