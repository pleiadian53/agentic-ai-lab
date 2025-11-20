"""Execution logic for single-agent "code-as-plan" workflows.

This module contains a small helper to extract the Python code block from
an LLM response and an executor that runs that code in a controlled
namespace.
"""

from __future__ import annotations

import io
import re
import sys
import traceback
from typing import Any, Dict, Optional

from tinydb import Query, where

from . import tinydb_data


def extract_execute_block(text: str) -> str:
    """Return the Python code inside <execute_python>...</execute_python>.

    If no tags are present, the input is returned as-is (stripped).
    """

    if not text:
        raise RuntimeError("Empty content passed to code executor.")
    m = re.search(r"<execute_python>(.*?)</execute_python>", text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else text.strip()


def execute_generated_code(
    code_or_content: str,
    *,
    db: Any,
    inventory_tbl: Any,
    transactions_tbl: Any,
    user_request: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute LLM-generated code in a constrained environment.

    This mirrors the notebook implementation but is free of any
    notebook-rendering concerns. It returns the executed code, stdout,
    any error traceback, and the answer extracted from the code's
    variables.
    """

    code = extract_execute_block(code_or_content)

    SAFE_GLOBALS = {
        "Query": Query,
        "where": where,
        "get_current_balance": tinydb_data.get_current_balance,
        "next_transaction_id": tinydb_data.next_transaction_id,
        "user_request": user_request or "",
    }
    SAFE_LOCALS = {
        "db": db,
        "inventory_tbl": inventory_tbl,
        "transactions_tbl": transactions_tbl,
    }

    # Capture stdout from the executed code
    _stdout_buf, _old_stdout = io.StringIO(), sys.stdout
    sys.stdout = _stdout_buf
    err_text = None
    try:
        exec(code, SAFE_GLOBALS, SAFE_LOCALS)
    except Exception:
        err_text = traceback.format_exc()
    finally:
        sys.stdout = _old_stdout
    printed = _stdout_buf.getvalue().strip()

    # Extract possible answers set by the generated code
    answer = (
        SAFE_LOCALS.get("answer_text")
        or SAFE_LOCALS.get("answer_rows")
        or SAFE_LOCALS.get("answer_json")
    )

    return {
        "code": code,
        "stdout": printed,
        "error": err_text,
        "answer": answer,
        "transactions_tbl": transactions_tbl.all(),
        "inventory_tbl": inventory_tbl.all(),
    }
