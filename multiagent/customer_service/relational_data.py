"""Relational-style demo data helpers (pandas/SQL) for customer_service.

These helpers mirror the data used in the M5 labs but are defined
locally so that the customer_service package has no dependency on the
educational notebooks.
"""

from __future__ import annotations

import random
from typing import Any, Tuple

import pandas as pd


def create_inventory_dataframe() -> pd.DataFrame:
    """Create an initial pandas DataFrame containing sunglasses inventory."""

    random.seed(42)
    sunglasses_data = {
        "name": ["Aviator", "Wayfarer", "Mystique", "Sport", "Round"],
        "item_id": ["SG001", "SG002", "SG003", "SG004", "SG005"],
        "description": [
            "Originally designed for pilots, these teardrop-shaped lenses with thin metal frames offer timeless appeal. The large lenses provide excellent coverage while the lightweight construction ensures comfort during long wear.",
            "Featuring thick, angular frames that make a statement, these sunglasses combine retro charm with modern edge. The rectangular lenses and sturdy acetate construction create a confident look.",
            "Inspired by 1950s glamour, these frames sweep upward at the outer corners to create an elegant, feminine silhouette. The subtle curves and often embellished temples add sophistication to any outfit.",
            "Designed for active lifestyles, these wraparound sunglasses feature a single curved lens that provides maximum coverage and wind protection. The lightweight, flexible frames include rubber grips.",
            "Circular lenses set in minimalist frames create a thoughtful, artistic appearance. These sunglasses evoke a scholarly or creative vibe while remaining effortlessly stylish.",
        ],
        "quantity_in_stock": [random.randint(3, 25) for _ in range(5)],
        "price": [random.randint(75, 150) for _ in range(5)],
    }
    return pd.DataFrame(sunglasses_data)


def create_transaction_dataframe(opening_balance: float = 500.0) -> pd.DataFrame:
    """Create an initial transactions DataFrame with an opening balance."""

    opening_transaction = {
        "transaction_id": ["TXN001"],
        "customer_name": ["OPENING_BALANCE"],
        "transaction_summary": ["Daily opening register balance"],
        "transaction_amount": [opening_balance],
        "balance_after_transaction": [opening_balance],
    }
    return pd.DataFrame(opening_transaction)
