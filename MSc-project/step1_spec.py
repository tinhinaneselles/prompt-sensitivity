import json
import pandas as pd
import streamlit as st

from db import save_spec
from prompting import generate_pqb_from_spec


def render_step1():
    st.header("Capture TaskSpec and store as JSON")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        task_type = st.selectbox("Task type", ["Deterministic", "Judgmental"])
        decision_format = st.selectbox("Decision format", ["Binary", "Graded", "Pairwise"])
        domain_context = st.text_input("Domain context (optional)", value="")
        task_description = st.text_area("Task description", height=120, placeholder="Describe what the agent must do…")
        output_format = st.text_area("Output format requirements", height=80, placeholder="e.g., Return ONLY YES/NO")

    with col2:
        st.markdown("### Extra fields (optional)")
        compliance_rules = st.text_area("Compliance / constraint rules (optional)", height=120)
        evaluation_policy = st.text_area("Evaluation policy notes (optional)", height=120)
        perturbation_types = st.text_input(
            "Perturbation types (comma-separated)",
            value="",
            placeholder="persona, format, task_framing",
        )
        uploaded_csv = st.file_uploader("Upload CSV (optional)", type=["csv"], key="csv_optional")

        if uploaded_csv is not None:
            st.session_state["uploaded_df"] = pd.read_csv(uploaded_csv)
            st.success(
                f"CSV loaded: {st.session_state['uploaded_df'].shape[0]} rows × "
                f"{st.session_state['uploaded_df'].shape[1]} cols"
            )

    if st.button("save TaskSpec JSON", type="primary"):
        spec = {
            "task_type": task_type,
            "decision_format": decision_format,
            "domain_context": domain_context,
            "task_description": task_description,
            "output_format": output_format,
            "evaluation_policy_notes": evaluation_policy,
            "compliance_rules_notes": compliance_rules,
            "perturbation_types": [t.strip() for t in perturbation_types.split(",") if t.strip()],
        }
        spec_id = save_spec(spec)
        st.session_state.active_spec_id = spec_id
        st.session_state.step = 2
        st.session_state.pqb_text = generate_pqb_from_spec(spec)
        st.success(f"Saved TaskSpec! id = {spec_id}")
        st.code(json.dumps(spec, indent=2, ensure_ascii=False), language="json")
