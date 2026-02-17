from prompting import replace_section

PERSONAS = [
    {"id": "persona_default", "label": "Default (precise & reliable)", "role_text": "You are a precise and reliable assistant."},
    {"id": "persona_strict_compliance", "label": "Strict compliance officer", "role_text": "You are a strict compliance officer. Prioritise policy adherence and risk minimisation over helpfulness."},
    {"id": "persona_pragmatic_analyst", "label": "Pragmatic analyst (reduce false positives)", "role_text": "You are a pragmatic analyst. Avoid unnecessary escalation; prioritise reducing false positives while staying compliant."},
    {"id": "persona_risk_averse", "label": "Risk-averse analyst (reduce false negatives)", "role_text": "You are a risk-averse compliance analyst. Prioritise reducing false negatives; when unsure, choose the safer option."},
    {"id": "persona_audit_ready", "label": "Audit-ready (justify clearly)", "role_text": "You are an audit-ready compliance analyst. Provide concise, traceable reasoning suitable for review."},
]

OUTPUT_FORMATS = [
    {"id": "fmt_free_text", "label": "Free text", "text": "Provide your answer as plain text."},
    {"id": "fmt_binary_only", "label": "Binary only (YES/NO)", "text": "Return ONLY one token: YES or NO. No additional text."},
    {"id": "fmt_binary_reason", "label": "Binary + 1-sentence rationale", "text": "Return: YES or NO, followed by a hyphen and one sentence explaining why."},
    {
        "id": "fmt_json_strict",
        "label": "Strict JSON",
        "text": """Return STRICT JSON only 
""",
    },
]


def apply_persona(base_prompt: str, persona: dict) -> str:
    return replace_section(base_prompt, "ROLE", persona["role_text"] + "\n")


def apply_output_format(base_prompt: str, fmt: dict) -> str:
    return replace_section(base_prompt, "OUTPUT FORMAT", fmt["text"].strip() + "\n")


def apply_task_type_flip(spec: dict) -> dict:
    flipped = dict(spec)
    current = (spec.get("task_type") or "").strip().lower()
    if current == "deterministic":
        flipped["task_type"] = "Judgmental"
    elif current == "judgmental":
        flipped["task_type"] = "Deterministic"
    else:
        flipped["task_type"] = "Judgmental"
    return flipped


def generate_variants(
    base_prompt: str,
    spec: dict,
    selected_persona_ids: list[str],
    selected_format_ids: list[str],
    flip_task_type: bool,
):
    variants = []
    persona_map = {p["id"]: p for p in PERSONAS}
    fmt_map = {f["id"]: f for f in OUTPUT_FORMATS}

    for pid in selected_persona_ids:
        p = persona_map[pid]
        v_text = apply_persona(base_prompt, p)
        variants.append(
            {
                "perturbation_type": "persona",
                "perturbation_id": p["id"],
                "strength": "medium",
                "prompt_text": v_text,
                "metadata": {"persona_label": p["label"], "original_task_type": spec.get("task_type")},
            }
        )

    for fid in selected_format_ids:
        f = fmt_map[fid]
        v_text = apply_output_format(base_prompt, f)
        variants.append(
            {
                "perturbation_type": "format",
                "perturbation_id": f["id"],
                "strength": "medium",
                "prompt_text": v_text,
                "metadata": {"format_label": f["label"], "original_task_type": spec.get("task_type")},
            }
        )

    if flip_task_type:
        flipped_spec = apply_task_type_flip(spec)
        variants.append(
            {
                "perturbation_type": "task_framing",
                "perturbation_id": "flip_task_type",
                "strength": "low",
                "prompt_text": base_prompt,
                "metadata": {
                    "original_task_type": spec.get("task_type"),
                    "flipped_task_type": flipped_spec.get("task_type"),
                    "note": "Spec-level framing perturbation; prompt text unchanged.",
                },
            }
        )

    return variants
