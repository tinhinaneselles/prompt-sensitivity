import json
import sqlite3
import uuid
from datetime import datetime, timezone

DB_PATH = "spec_store.db"


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def init_db():
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS specs (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            spec_json TEXT NOT NULL
        );
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS base_prompts (
            id TEXT PRIMARY KEY,
            spec_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            prompt_text TEXT NOT NULL,
            FOREIGN KEY(spec_id) REFERENCES specs(id)
        );
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS prompt_variants (
            id TEXT PRIMARY KEY,
            spec_id TEXT NOT NULL,
            base_prompt_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            perturbation_type TEXT NOT NULL,
            perturbation_id TEXT NOT NULL,
            strength TEXT NOT NULL,
            variant_prompt_text TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            FOREIGN KEY(spec_id) REFERENCES specs(id),
            FOREIGN KEY(base_prompt_id) REFERENCES base_prompts(id)
        );
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            spec_id TEXT NOT NULL,
            base_prompt_id TEXT NOT NULL,
            variant_id TEXT NOT NULL,
            model_name TEXT NOT NULL,
            temperature REAL NOT NULL,
            top_p REAL NOT NULL,
            max_tokens INTEGER NOT NULL,
            k_index INTEGER NOT NULL,
            full_prompt_text TEXT NOT NULL,
            response_text TEXT NOT NULL,
            latency_ms INTEGER NOT NULL,
            parsed_json TEXT NOT NULL,
            parse_ok INTEGER NOT NULL,
            FOREIGN KEY(spec_id) REFERENCES specs(id),
            FOREIGN KEY(base_prompt_id) REFERENCES base_prompts(id),
            FOREIGN KEY(variant_id) REFERENCES prompt_variants(id)
        );
        """
    )
    conn.commit()
    conn.close()


# ---- Specs ----
def save_spec(spec: dict) -> str:
    spec_id = str(uuid.uuid4())
    conn = get_conn()
    conn.execute(
        "INSERT INTO specs (id, created_at, spec_json) VALUES (?, ?, ?)",
        (spec_id, _utc_now(), json.dumps(spec, ensure_ascii=False)),
    )
    conn.commit()
    conn.close()
    return spec_id


def list_specs(limit: int = 200):
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, created_at FROM specs ORDER BY created_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return rows


def load_spec(spec_id: str):
    conn = get_conn()
    row = conn.execute("SELECT spec_json FROM specs WHERE id = ?", (spec_id,)).fetchone()
    conn.close()
    return row[0] if row else None


# ---- Base prompts ----
def save_base_prompt(spec_id: str, prompt_text: str) -> str:
    prompt_id = str(uuid.uuid4())
    conn = get_conn()
    conn.execute(
        "INSERT INTO base_prompts (id, spec_id, created_at, prompt_text) VALUES (?, ?, ?, ?)",
        (prompt_id, spec_id, _utc_now(), prompt_text),
    )
    conn.commit()
    conn.close()
    return prompt_id


def list_base_prompts(spec_id: str, limit: int = 50):
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT id, created_at
        FROM base_prompts
        WHERE spec_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (spec_id, limit),
    ).fetchall()
    conn.close()
    return rows


def load_base_prompt(prompt_id: str):
    conn = get_conn()
    row = conn.execute("SELECT prompt_text FROM base_prompts WHERE id = ?", (prompt_id,)).fetchone()
    conn.close()
    return row[0] if row else None


# ---- Variants ----
def save_prompt_variant(
    spec_id: str,
    base_prompt_id: str,
    perturbation_type: str,
    perturbation_id: str,
    strength: str,
    variant_prompt_text: str,
    metadata: dict,
) -> str:
    variant_id = str(uuid.uuid4())
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO prompt_variants (
            id, spec_id, base_prompt_id, created_at,
            perturbation_type, perturbation_id, strength,
            variant_prompt_text, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            variant_id,
            spec_id,
            base_prompt_id,
            _utc_now(),
            perturbation_type,
            perturbation_id,
            strength,
            variant_prompt_text,
            json.dumps(metadata, ensure_ascii=False),
        ),
    )
    conn.commit()
    conn.close()
    return variant_id


def list_prompt_variants(spec_id: str, base_prompt_id: str, limit: int = 200):
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT id, created_at, perturbation_type, perturbation_id, strength
        FROM prompt_variants
        WHERE spec_id = ? AND base_prompt_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (spec_id, base_prompt_id, limit),
    ).fetchall()
    conn.close()
    return rows


def load_prompt_variant(variant_id: str):
    conn = get_conn()
    row = conn.execute(
        """
        SELECT variant_prompt_text, metadata_json
        FROM prompt_variants
        WHERE id = ?
        """,
        (variant_id,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {"variant_prompt_text": row[0], "metadata": json.loads(row[1])}


# ---- Runs ----
def save_run(
    spec_id: str,
    base_prompt_id: str,
    variant_id: str,
    model_name: str,
    temperature: float,
    top_p: float,
    max_tokens: int,
    k_index: int,
    full_prompt_text: str,
    response_text: str,
    latency_ms: int,
    parsed_json: dict | None,
    parse_ok: bool,
) -> str:
    run_id = str(uuid.uuid4())
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO runs (
            id, created_at, spec_id, base_prompt_id, variant_id,
            model_name, temperature, top_p, max_tokens, k_index,
            full_prompt_text, response_text,
            latency_ms, parsed_json, parse_ok
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            _utc_now(),
            spec_id,
            base_prompt_id,
            variant_id,
            model_name,
            float(temperature),
            float(top_p),
            int(max_tokens),
            int(k_index),
            full_prompt_text,
            response_text,
            int(latency_ms),
            json.dumps(parsed_json or {}, ensure_ascii=False),
            1 if parse_ok else 0,
        ),
    )
    conn.commit()
    conn.close()
    return run_id


def list_runs(variant_id: str, limit: int = 50):
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT id, created_at, model_name, k_index, latency_ms, parse_ok
        FROM runs
        WHERE variant_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (variant_id, limit),
    ).fetchall()
    conn.close()
    return rows


def list_runs_for_variant(variant_id: str):
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT k_index, response_text, parse_ok, latency_ms
        FROM runs
        WHERE variant_id = ?
        ORDER BY k_index ASC
        """,
        (variant_id,),
    ).fetchall()
    conn.close()
    return rows


def load_run(run_id: str):
    conn = get_conn()
    row = conn.execute(
        """
        SELECT full_prompt_text, response_text, parsed_json, parse_ok
        FROM runs
        WHERE id = ?
        """,
        (run_id,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "full_prompt_text": row[0],
        "response_text": row[1],
        "parsed_json": json.loads(row[2]) if row[2] else {},
        "parse_ok": bool(row[3]),
    }
