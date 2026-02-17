import os
import streamlit as st

from db import load_prompt_variant, save_run, list_runs, load_run
from dataset import dataset_block_for_prompt
from llm import call_llm_openai, try_parse_json


def render_step4(saved_variant_rows, base_prompt_id, base_prompt_text):
    st.header("Step 4 — Run LLM Executions (k repeats)")

    if not os.getenv("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY is not set in your environment. Set it and restart Streamlit.")
        st.stop()

    chosen_variant_id = st.selectbox(
        "Choose a variant to run",
        options=[r[0] for r in saved_variant_rows],
        format_func=lambda x: f"{x[:8]}…  •  {next(r for r in saved_variant_rows if r[0]==x)[2]}/{next(r for r in saved_variant_rows if r[0]==x)[3]}",
        key="chosen_variant_step4",
    )

    vrec = load_prompt_variant(chosen_variant_id)
    variant_prompt_text = vrec["variant_prompt_text"] if vrec else base_prompt_text

    st.markdown("### Model settings (fixed for k runs)")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        model_name = st.text_input("Model", value="gpt-4.1-mini")
    with c2:
        temperature = st.number_input("temperature", min_value=0.0, max_value=2.0, value=0.2, step=0.1)
    with c3:
        top_p = st.number_input("top_p", min_value=0.0, max_value=1.0, value=1.0, step=0.05)
    with c4:
        max_tokens = st.number_input("max_tokens", min_value=64, max_value=4096, value=512, step=64)

    k = st.number_input("k repeats", min_value=1, max_value=20, value=3, step=1)

    if st.button("▶ Run k executions", type="primary"):
        full_prompt = variant_prompt_text.strip() + dataset_block_for_prompt()

        for i in range(1, int(k) + 1):
            try:
                resp_text, latency_ms = call_llm_openai(
                    prompt_text=full_prompt,
                    model_name=model_name,
                    temperature=float(temperature),
                    top_p=float(top_p),
                    max_tokens=int(max_tokens),
                )
                parsed, ok = try_parse_json(resp_text)

                run_id = save_run(
                    spec_id=st.session_state.active_spec_id,
                    base_prompt_id=base_prompt_id,
                    variant_id=chosen_variant_id,
                    model_name=model_name,
                    temperature=float(temperature),
                    top_p=float(top_p),
                    max_tokens=int(max_tokens),
                    k_index=i,
                    full_prompt_text=full_prompt,
                    response_text=resp_text,
                    latency_ms=latency_ms,
                    parsed_json=parsed,
                    parse_ok=ok,
                )

                st.success(f"Run {i}/{k} saved: {run_id[:8]}… • latency={latency_ms}ms • parse_ok={ok}")
                st.code(resp_text, language="text")
            except Exception as e:
                st.error(f"Run {i} failed: {e}")

    st.divider()
    st.subheader("Recent runs for this variant")
    run_rows = list_runs(chosen_variant_id, limit=10)
    if not run_rows:
        st.caption("No runs saved yet.")
        return

    chosen_run = st.selectbox(
        "Open a run",
        options=[r[0] for r in run_rows],
        format_func=lambda x: f"{x[:8]}…  •  k={next(r for r in run_rows if r[0]==x)[3]}  • parse_ok={bool(next(r for r in run_rows if r[0]==x)[5])}",
    )
    if st.button("Open Run"):
        rr = load_run(chosen_run)
        if rr:
            st.markdown("**Full prompt**")
            st.code(rr["full_prompt_text"], language="text")
            st.markdown("**Response**")
            st.code(rr["response_text"], language="text")
            st.markdown(f"**JSON parse ok:** {rr['parse_ok']}")
            if rr["parse_ok"]:
                st.json(rr["parsed_json"])
