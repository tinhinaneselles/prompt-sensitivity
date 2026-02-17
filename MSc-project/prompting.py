def generate_pqb_from_spec(spec: dict) -> str:
    domain = (spec.get("domain_context") or "").strip()
    task_desc = (spec.get("task_description") or "").strip()
    output_fmt = (spec.get("output_format") or "").strip()
    constraints = (spec.get("compliance_rules_notes") or "").strip()

    parts = []
    parts.append("ROLE\nYou are a precise and reliable assistant.\n")

    if domain:
        parts.append(f"CONTEXT\nDomain: {domain}\n")
    else:
        parts.append("CONTEXT\n(Provide relevant domain context if applicable.)\n")

    parts.append("TASK\n" + (task_desc if task_desc else "(Describe what the agent must do.)") + "\n")

    if constraints:
        parts.append("CONSTRAINTS\n" + constraints + "\n")

    parts.append("OUTPUT FORMAT\n" + (output_fmt if output_fmt else "(Specify strict output format requirements.)") + "\n")

    return "\n".join(parts).strip()


def replace_section(prompt: str, section_name: str, new_body: str) -> str:
    marker = f"{section_name}\n"
    if marker not in prompt:
        return (prompt.strip() + f"\n\n{section_name}\n{new_body.strip()}\n").strip()

    before, after = prompt.split(marker, 1)
    parts = after.split("\n\n", 1)
    if len(parts) == 1:
        return (before + marker + new_body.strip() + "\n").strip()
    remainder = parts[1]
    return (before + marker + new_body.strip() + "\n\n" + remainder).strip()
