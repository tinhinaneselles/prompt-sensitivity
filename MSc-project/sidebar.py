import json
import streamlit as st

from db import list_specs, load_spec, list_base_prompts, load_base_prompt


def render_sidebar():
    with st.sidebar:
        st.subheader("Saved TaskSpecs")
        specs = list_specs()

        if not specs:
            st.caption("No TaskSpecs saved yet.")
            return

        chosen_spec = st.selectbox(
            "Open a saved TaskSpec",
            options=[r[0] for r in specs],
            format_func=lambda x: f"{x[:8]}…  •  {next(r for r in specs if r[0]==x)[1]}",
        )

        if st.button("Open TaskSpec"):
            st.session_state.active_spec_id = chosen_spec
            st.session_state.step = 2

        if not st.session_state.get("active_spec_id"):
            return

        st.caption(f"Active spec: {st.session_state.active_spec_id[:8]}…")
        raw = load_spec(st.session_state.active_spec_id)
        if raw:
            st.code(json.dumps(json.loads(raw), indent=2, ensure_ascii=False), language="json")

        st.divider()
        st.subheader("Base Prompts (PQB)")
        prompts = list_base_prompts(st.session_state.active_spec_id)

        if not prompts:
            st.caption("No base prompts saved for this spec yet.")
            return

        chosen_prompt = st.selectbox(
            "Open a saved base prompt",
            options=[p[0] for p in prompts],
            format_func=lambda x: f"{x[:8]}…  •  {next(p for p in prompts if p[0]==x)[1]}",
        )
        if st.button("Open Base Prompt"):
            text = load_base_prompt(chosen_prompt)
            if text:
                st.session_state.pqb_text = text
