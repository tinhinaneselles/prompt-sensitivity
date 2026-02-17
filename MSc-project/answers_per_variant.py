import streamlit as st

from db import list_prompt_variants, load_prompt_variant, list_runs_for_variant


def render_answers_per_variant(): # redering ui componeents 
    st.header("LLM Answers per Variant")

    base_prompt_id = st.session_state.get("base_prompt_id_step3") # reading the state of th prompt from ste 3 
    if not (st.session_state.get("active_spec_id") and base_prompt_id):
        st.caption("Select a Base Prompt in Step 3 to view per-variant answers.")
        return

    variants = list_prompt_variants(st.session_state.active_spec_id, base_prompt_id)
    if not variants:
        st.info("No variants available.")
        return

    for vid, created_at, ptype, pid, strength in variants:
        st.subheader(f"Variant {vid[:8]} • {ptype}/{pid}")

        vrec = load_prompt_variant(vid)
        st.markdown("**Variant prompt**")
        st.code(vrec["variant_prompt_text"], language="text")

        runs = list_runs_for_variant(vid)
        if not runs:
            st.warning("No LLM runs for this variant yet.")
            continue

        for k_index, response_text, parse_ok, latency_ms in runs:
            with st.expander(f"Run k={k_index} • latency={latency_ms}ms • parse_ok={bool(parse_ok)}"):
                st.code(response_text, language="text")
