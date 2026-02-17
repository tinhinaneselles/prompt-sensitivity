import streamlit as st
import json

from db import load_spec, save_base_prompt
from prompting import generate_pqb_from_spec


def render_step2():
    st.header("Build Base Prompt (PQB)")

    raw = load_spec(st.session_state.active_spec_id)
    if not raw:
        st.error("Could not load the active spec from DB.")
        st.stop()

    spec = json.loads(raw)

    if "pqb_text" not in st.session_state:
        st.session_state.pqb_text = generate_pqb_from_spec(spec)

    c1, c2 = st.columns([2, 1], gap="large")
    with c1:
        pqb_text = st.text_area("Base Prompt (edit if needed)", value=st.session_state.pqb_text, height=320)
        st.session_state.pqb_text = pqb_text

        btns = st.columns(3)
        with btns[0]:
            if st.button("🔁 Regenerate from TaskSpec"):
                st.session_state.pqb_text = generate_pqb_from_spec(spec)
                st.rerun()
        with btns[1]:
            if st.button("Save Base Prompt", type="primary"):
                prompt_id = save_base_prompt(st.session_state.active_spec_id, st.session_state.pqb_text)
                st.success(f"Saved base prompt! id = {prompt_id}")
        with btns[2]:
            if st.button("🧹 Clear"):
                st.session_state.pqb_text = ""
                st.rerun()

    with c2:
        st.markdown("### What happens next")
        st.write("Step 3: generate prompt variants")
        st.write("Step 4: run LLM executions")
