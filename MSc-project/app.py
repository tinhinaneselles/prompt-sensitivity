import streamlit as st

from db import init_db
from sidebar import render_sidebar
from step1_spec import render_step1
from step2_pqb import render_step2
from step3_variants import render_step3
from step4_runs import render_step4
from answers_per_variant import render_answers_per_variant
from db import load_base_prompt
import os


st.set_page_config(page_title="TaskSpec → PQB Builder", layout="wide")
init_db()

def get_api_key() -> str | None:
    # Streamlit Cloud (Secrets UI) OR local .streamlit/secrets.toml
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        # Local fallback: environment variable
        return os.getenv("OPENAI_API_KEY")

api_key = get_api_key()

if not api_key:
    st.error("Missing OPENAI_API_KEY. Add it in Streamlit Cloud Secrets or set env var locally.")
    st.stop()


# session defaults
if "active_spec_id" not in st.session_state:
    st.session_state.active_spec_id = None
if "step" not in st.session_state:
    st.session_state.step = 1

st.title("Build Base Prompt (PQB) → Variants → Runs")

render_sidebar()

st.divider()

render_step1()
st.divider()

# step2+
if st.session_state.step >= 2 and st.session_state.active_spec_id:
    render_step2()
    st.divider()

    render_step3()
    st.divider()


    saved_rows = st.session_state.get("saved_variants_rows")
    base_prompt_id = st.session_state.get("base_prompt_id_step3")
    if saved_rows and base_prompt_id:
        base_prompt_text = load_base_prompt(base_prompt_id) or st.session_state.get("pqb_text", "")
        render_step4(saved_rows, base_prompt_id, base_prompt_text)

st.divider()
render_answers_per_variant()
