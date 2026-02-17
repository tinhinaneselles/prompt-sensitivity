import streamlit as st
import json

from db import list_base_prompts, load_base_prompt, list_prompt_variants, save_prompt_variant, load_spec
from perturbations import PERSONAS, OUTPUT_FORMATS, generate_variants


def render_step3():
    st.header("Step 3 — Generate Prompt Variants")

    raw = load_spec(st.session_state.active_spec_id)
    spec = json.loads(raw) if raw else {}

    saved_prompts = list_base_prompts(st.session_state.active_spec_id)
    if not saved_prompts:
        st.info("Save at least one Base Prompt first (Step 2) to generate variants.")
        return

    base_prompt_id = st.selectbox(
        "Choose a saved Base Prompt ID",
        options=[p[0] for p in saved_prompts],
        format_func=lambda x: f"{x[:8]}…  •  {next(p for p in saved_prompts if p[0]==x)[1]}",
        key="base_prompt_id_step3",
    )
    st.session_state.base_prompt_id = base_prompt_id

    base_prompt_text = load_base_prompt(base_prompt_id) or st.session_state.get("pqb_text", "")

    persona_ids = [p["id"] for p in PERSONAS]
    fmt_ids = [f["id"] for f in OUTPUT_FORMATS]
    cA, cB, cC = st.columns(3)

    with cA:
        selected_personas = st.multiselect(
            "Personas",
            options=persona_ids,
            default=["persona_default", "persona_strict_compliance"],
            format_func=lambda pid: next(p["label"] for p in PERSONAS if p["id"] == pid),
        )
    with cB:
        selected_formats = st.multiselect(
            "Output formats",
            options=fmt_ids,
            default=["fmt_binary_only", "fmt_json_strict"],
            format_func=lambda fid: next(f["label"] for f in OUTPUT_FORMATS if f["id"] == fid),
        )
    with cC:
        flip_task_type = st.checkbox("Flip task type (Deterministic ↔ Judgmental)", value=False)

    if st.button("Generate variants", type="primary"):
        generated = generate_variants(
            base_prompt=base_prompt_text,
            spec=spec,
            selected_persona_ids=selected_personas,
            selected_format_ids=selected_formats,
            flip_task_type=flip_task_type,
        )
        st.session_state.generated_variants = generated
        st.success(f"Generated {len(generated)} variants. Review below and save.")

    if "generated_variants" in st.session_state and st.session_state.generated_variants:
        st.subheader("Generated variants (preview)")
        for i, v in enumerate(st.session_state.generated_variants, start=1):
            with st.expander(f"Variant {i}: {v['perturbation_type']} • {v['perturbation_id']}"):
                st.code(v["prompt_text"], language="text")
                st.caption(json.dumps(v["metadata"], indent=2, ensure_ascii=False))
                if st.button(f"💾 Save this variant #{i}", key=f"save_variant_{i}"):
                    vid = save_prompt_variant(
                        spec_id=st.session_state.active_spec_id,
                        base_prompt_id=base_prompt_id,
                        perturbation_type=v["perturbation_type"],
                        perturbation_id=v["perturbation_id"],
                        strength=v["strength"],
                        variant_prompt_text=v["prompt_text"],
                        metadata=v["metadata"],
                    )
                    st.success(f"Saved variant! id = {vid}")

    st.divider()
    st.subheader("Saved variants for this base prompt")
    rows = list_prompt_variants(st.session_state.active_spec_id, base_prompt_id)
    if not rows:
        st.caption("No variants saved yet for this base prompt.")
    else:
        st.session_state.saved_variants_rows = rows
