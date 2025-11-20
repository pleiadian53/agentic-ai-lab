"""TinyDB-backed demo data helpers for the customer service package.

This module is intentionally decoupled from the M5_lab1 notebook code
so that the customer_service package can be reused independently.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Tuple

from tinydb import TinyDB


def create_inventory(db: TinyDB) -> list[dict[str, Any]]:
    """Create and store the initial sunglasses inventory in TinyDB.

    The schema matches the original lab: item_id, name, description,
    quantity_in_stock, and price.
    """

    import random

    random.seed(42)

    sunglasses_data = [
        {
            "item_id": "SG001",
            "name": "Aviator",
            "description": (
                "Originally designed for pilots, these teardrop-shaped lenses with "
                "thin metal frames offer timeless appeal. The large lenses provide "
                "excellent coverage while the lightweight construction ensures "
                "comfort during long wear."
            ),
            "quantity_in_stock": random.randint(3, 25),
            "price": 80,
        },
        {
            "item_id": "SG002",
            "name": "Wayfarer",
            "description": (
                "Featuring thick, angular frames that make a statement, these "
                "sunglasses combine retro charm with modern edge. The rectangular "
                "lenses and sturdy acetate construction create a confident look."
            ),
            "quantity_in_stock": random.randint(3, 25),
            "price": 95,
        },
        {
            "item_id": "SG003",
            "name": "Mystique",
            "description": (
                "Inspired by 1950s glamour, these frames sweep upward at the outer "
                "corners to create an elegant, feminine silhouette. The subtle "
                "curves and often embellished temples add sophistication to any "
                "outfit."
            ),
            "quantity_in_stock": random.randint(3, 25),
            "price": 70,
        },
        {
            "item_id": "SG004",
            "name": "Sport",
            "description": (
                "Designed for active lifestyles, these wraparound sunglasses "
                "feature a single curved lens that provides maximum coverage and "
                "wind protection. The lightweight, flexible frames include rubber "
                "grips."
            ),
            "quantity_in_stock": random.randint(3, 25),
            "price": 110,
        },
        {
            "item_id": "SG005",
            "name": "Classic",
            "description": (
                "Classic round profile with minimalist metal frames, offering a "
                "timeless and versatile style that fits both casual and formal "
                "wear."
            ),
            "quantity_in_stock": random.randint(3, 25),
            "price": 60,
        },
        {
            "item_id": "SG006",
            "name": "Moon",
            "description": (
                "Oversized round style with bold plastic frames, evoking retro "
                "aesthetics with a modern twist."
            ),
            "quantity_in_stock": random.randint(3, 25),
            "price": 120,
        },
    ]

    inventory_table = db.table("inventory")
    inventory_table.truncate()
    inventory_table.insert_multiple(sunglasses_data)
    return sunglasses_data


def create_transactions(db: TinyDB, opening_balance: float = 500.0) -> dict[str, Any]:
    """Create and store the initial transactions (opening balance)."""

    opening_transaction = {
        "transaction_id": "TXN001",
        "customer_name": "OPENING_BALANCE",
        "transaction_summary": "Daily opening register balance",
        "transaction_amount": opening_balance,
        "balance_after_transaction": opening_balance,
        "timestamp": datetime.now().isoformat(),
    }

    transactions_table = db.table("transactions")
    transactions_table.truncate()
    transactions_table.insert(opening_transaction)
    return opening_transaction


def seed_db(db_path: str = "store_db.json") -> Tuple[TinyDB, Any, Any]:
    """Seed a TinyDB database with inventory and transactions tables."""

    db = TinyDB(db_path)
    inventory_table = db.table("inventory")
    transactions_table = db.table("transactions")
    create_inventory(db)
    create_transactions(db)
    return db, inventory_table, transactions_table


def build_schema_for_table(tbl, table_name: str, k: int = 3) -> str:
    """Infer a simple schema description for a TinyDB table."""

    rows = tbl.all()
    if not rows:
        return f"TABLE: {table_name} (empty)"

    schema: dict[str, dict[str, Any]] = {}
    for r in rows:
        for key, value in r.items():
            if key not in schema:
                schema[key] = {"type": type(value).__name__, "examples": []}
            examples = schema[key]["examples"]
            if len(examples) < k and value not in examples:
                examples.append(str(value))

    lines = [f"TABLE: {table_name}", "COLUMNS:"]
    for col, info in schema.items():
        ex = f" | examples: {info['examples']}" if info["examples"] else ""
        lines.append(f"  - {col}: {info['type']}{ex}")
    lines.append(f"ROWS: {len(rows)}")
    lines.append(f"PREVIEW (first {min(k, len(rows))} rows): {rows[:k]}")
    return "\n".join(lines)


def build_schema_block(inventory_tbl, transactions_tbl) -> str:
    """Build the schema block used in the planning prompt."""

    inv = build_schema_for_table(inventory_tbl, "inventory_tbl")
    tx = build_schema_for_table(transactions_tbl, "transactions_tbl")
    notes = (
        "NOTES:\n"
        "- inventory_tbl.price is in USD.\n"
        "- inventory_tbl.quantity_in_stock > 0 means available stock.\n"
        "- inventory_tbl.name describes the style (e.g., 'Classic', 'Moon').\n"
        "- transactions_tbl.timestamp is ISO-8601.\n"
    )
    return f"{inv}\n\n{tx}\n\n{notes}"


def get_current_balance(transactions_tbl, default: float = 0.0) -> float:
    """Return the current balance from a TinyDB transactions table."""

    txns = transactions_tbl.all()
    return txns[-1].get("balance_after_transaction", default) if txns else default


def next_transaction_id(transactions_tbl, prefix: str = "TXN") -> str:
    """Return the next transaction id based on table length."""

    return f"{prefix}{len(transactions_tbl)+1:03d}"
