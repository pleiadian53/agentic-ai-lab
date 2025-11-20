"""Data access layer for the customer service example.

This module currently provides a TinyDB-backed implementation, but the
interface is designed so that future backends (e.g., SQLite, MySQL) can
be added without changing the agent logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Tuple

import duckdb
import pandas as pd
import sqlite3
from tinydb import TinyDB, Query

from . import tinydb_data, relational_data


class CustomerServiceStore(ABC):
    """Abstract interface for customer-service data access.

    Concrete backends (TinyDB, SQLite, etc.) must implement these methods.
    """

    @abstractmethod
    def seed_demo_data(self) -> None:
        """(Re)initialize demo data for inventory and transactions."""

    @abstractmethod
    def get_inventory_rows(self) -> list[dict[str, Any]]:
        """Return all inventory rows as dictionaries."""

    @abstractmethod
    def get_transaction_rows(self) -> list[dict[str, Any]]:
        """Return all transaction rows as dictionaries."""

    @abstractmethod
    def get_current_balance(self) -> float:
        """Return the current balance after the last transaction."""

    @abstractmethod
    def next_transaction_id(self, prefix: str = "TXN") -> str:
        """Return a new transaction id with the given prefix."""

    @abstractmethod
    def update_inventory_quantity(self, item_id: str, new_qty: int) -> None:
        """Update quantity_in_stock for the given item_id."""

    @abstractmethod
    def insert_transaction(self, row: dict[str, Any]) -> None:
        """Insert a new transaction row."""

    @abstractmethod
    def get_raw_handles(self) -> Tuple[Any, Any, Any]:
        """Return low-level handles needed by TinyDB-based execution.

        For the current single-agent implementation, we still execute
        code that expects ``db``, ``inventory_tbl`` and ``transactions_tbl``
        objects. This method exposes those handles when available.
        """


class TinyDBStore(CustomerServiceStore):
    """TinyDB-backed implementation using the existing inv_utils module."""

    def __init__(self, path: str = "store_db.json") -> None:
        # inv_utils.seed_db will create and/or initialize the DB file.
        self._db_path = path
        self._db: TinyDB | None = None
        self._inventory_tbl = None
        self._transactions_tbl = None
        self._ensure_db()

    # ---- Internal helpers ----
    def _ensure_db(self) -> None:
        if self._db is None:
            db, inventory_tbl, transactions_tbl = tinydb_data.seed_db(self._db_path)
            self._db = db
            self._inventory_tbl = inventory_tbl
            self._transactions_tbl = transactions_tbl

    # ---- CustomerServiceStore API ----
    def seed_demo_data(self) -> None:
        """Recreate demo inventory and transactions in place."""

        self._ensure_db()
        tinydb_data.create_inventory(self._db)
        tinydb_data.create_transactions(self._db)

    def get_inventory_rows(self) -> list[dict[str, Any]]:
        self._ensure_db()
        return list(self._inventory_tbl.all())

    def get_transaction_rows(self) -> list[dict[str, Any]]:
        self._ensure_db()
        return list(self._transactions_tbl.all())

    def get_current_balance(self) -> float:
        self._ensure_db()
        return tinydb_data.get_current_balance(self._transactions_tbl)

    def next_transaction_id(self, prefix: str = "TXN") -> str:
        self._ensure_db()
        return tinydb_data.next_transaction_id(self._transactions_tbl, prefix)

    def update_inventory_quantity(self, item_id: str, new_qty: int) -> None:
        self._ensure_db()
        tbl = self._inventory_tbl
        q = Query()
        tbl.update({"quantity_in_stock": int(new_qty)}, q.item_id == item_id)

    def insert_transaction(self, row: dict[str, Any]) -> None:
        self._ensure_db()
        self._transactions_tbl.insert(dict(row))

    def get_raw_handles(self) -> Tuple[Any, Any, Any]:
        """Expose TinyDB objects for the current executor implementation."""

        self._ensure_db()
        return self._db, self._inventory_tbl, self._transactions_tbl


class DuckDBStore(CustomerServiceStore):
    """DuckDB-backed implementation using pandas DataFrames.

    This mirrors the M5_lab1 multi-agent lab pattern, where inventory
    and transactions live in pandas DataFrames registered into a DuckDB
    connection. It does *not* integrate with the current TinyDB-based
    code executor, but it can be used by future tools-only or
    multi-agent workflows.
    """

    def __init__(self, db_path: str | None = None) -> None:
        # If db_path is None, DuckDB keeps data in-memory. Otherwise it
        # persists to the given file.
        self._con = duckdb.connect(database=db_path or ":memory:")
        self._inventory_df = relational_data.create_inventory_dataframe()
        self._transaction_df = relational_data.create_transaction_dataframe()
        self._register_frames()

    def _register_frames(self) -> None:
        self._con.register("inventory_df", self._inventory_df)
        self._con.register("transaction_df", self._transaction_df)

    # ---- CustomerServiceStore API ----
    def seed_demo_data(self) -> None:
        self._inventory_df = relational_data.create_inventory_dataframe()
        self._transaction_df = relational_data.create_transaction_dataframe()
        self._register_frames()

    def get_inventory_rows(self) -> list[dict[str, Any]]:
        return self._inventory_df.to_dict(orient="records")

    def get_transaction_rows(self) -> list[dict[str, Any]]:
        return self._transaction_df.to_dict(orient="records")

    def get_current_balance(self) -> float:
        if self._transaction_df.empty:
            return 0.0
        return float(self._transaction_df["balance_after_transaction"].iloc[-1])

    def next_transaction_id(self, prefix: str = "TXN") -> str:
        if self._transaction_df.empty:
            return f"{prefix}001"
        last_id = str(self._transaction_df["transaction_id"].iloc[-1])
        import re as _re

        m = _re.findall(r"(\d+)$", last_id)
        n = int(m[0]) if m else 0
        return f"{prefix}{n+1:03d}"

    def update_inventory_quantity(self, item_id: str, new_qty: int) -> None:
        df = self._inventory_df.copy()
        df["item_id"] = df["item_id"].astype(str)
        mask = df["item_id"] == str(item_id)
        if not mask.any():
            return
        df.loc[mask, "quantity_in_stock"] = int(new_qty)
        self._inventory_df = df
        self._register_frames()

    def insert_transaction(self, row: dict[str, Any]) -> None:
        new_row = pd.DataFrame([row])
        self._transaction_df = pd.concat([self._transaction_df, new_row], ignore_index=True)
        self._register_frames()

    def get_raw_handles(self) -> Tuple[Any, Any, Any]:
        """Expose DuckDB connection and DataFrames.

        The current TinyDB-based code executor will not use these
        directly, but tools-only / multi-agent flows can.
        """

        return self._con, self._inventory_df, self._transaction_df


class SQLiteStore(CustomerServiceStore):
    """SQLite-backed implementation using a simple schema.

    This is a forward-looking store intended for future workflows. It
    initializes two tables (inventory, transactions) in a SQLite
    database and operates on them via SQL. The current single-agent
    executor remains TinyDB-specific; SQLiteStore is meant for
    higher-level, tools-only agents.
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        self._db_path = db_path
        self._con = sqlite3.connect(db_path)
        self._init_schema()
        self.seed_demo_data()

    def _init_schema(self) -> None:
        cur = self._con.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS inventory (
                item_id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                quantity_in_stock INTEGER,
                price REAL
            )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                customer_name TEXT,
                transaction_summary TEXT,
                transaction_amount REAL,
                balance_after_transaction REAL,
                timestamp TEXT
            )"""
        )
        self._con.commit()

    # ---- CustomerServiceStore API ----
    def seed_demo_data(self) -> None:
        cur = self._con.cursor()
        cur.execute("DELETE FROM inventory")
        cur.execute("DELETE FROM transactions")

        inv_df = relational_data.create_inventory_dataframe()
        tx_df = relational_data.create_transaction_dataframe()

        inv_records = inv_df.to_dict(orient="records")
        tx_records = tx_df.to_dict(orient="records")

        cur.executemany(
            "INSERT INTO inventory (item_id, name, description, quantity_in_stock, price) "
            "VALUES (:item_id, :name, :description, :quantity_in_stock, :price)",
            inv_records,
        )
        cur.executemany(
            "INSERT INTO transactions (transaction_id, customer_name, transaction_summary, "
            "transaction_amount, balance_after_transaction) "
            "VALUES (:transaction_id, :customer_name, :transaction_summary, "
            ":transaction_amount, :balance_after_transaction)",
            tx_records,
        )
        self._con.commit()

    def get_inventory_rows(self) -> list[dict[str, Any]]:
        cur = self._con.cursor()
        cur.execute("SELECT item_id, name, description, quantity_in_stock, price FROM inventory")
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def get_transaction_rows(self) -> list[dict[str, Any]]:
        cur = self._con.cursor()
        cur.execute(
            "SELECT transaction_id, customer_name, transaction_summary, "
            "transaction_amount, balance_after_transaction, COALESCE(timestamp, '') AS timestamp "
            "FROM transactions ORDER BY transaction_id"
        )
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def get_current_balance(self) -> float:
        cur = self._con.cursor()
        cur.execute("SELECT balance_after_transaction FROM transactions ORDER BY transaction_id DESC LIMIT 1")
        row = cur.fetchone()
        return float(row[0]) if row is not None else 0.0

    def next_transaction_id(self, prefix: str = "TXN") -> str:
        cur = self._con.cursor()
        cur.execute("SELECT transaction_id FROM transactions ORDER BY transaction_id DESC LIMIT 1")
        row = cur.fetchone()
        last_id = row[0] if row is not None else None
        if not last_id:
            return f"{prefix}001"
        import re as _re

        m = _re.findall(r"(\d+)$", str(last_id))
        n = int(m[0]) if m else 0
        return f"{prefix}{n+1:03d}"

    def update_inventory_quantity(self, item_id: str, new_qty: int) -> None:
        cur = self._con.cursor()
        cur.execute(
            "UPDATE inventory SET quantity_in_stock = ? WHERE item_id = ?",
            (int(new_qty), str(item_id)),
        )
        self._con.commit()

    def insert_transaction(self, row: dict[str, Any]) -> None:
        cur = self._con.cursor()
        cur.execute(
            "INSERT INTO transactions (transaction_id, customer_name, transaction_summary, "
            "transaction_amount, balance_after_transaction, timestamp) "
            "VALUES (:transaction_id, :customer_name, :transaction_summary, :transaction_amount, "
            ":balance_after_transaction, :timestamp)",
            row,
        )
        self._con.commit()

    def get_raw_handles(self) -> Tuple[Any, Any, Any]:
        """Expose underlying SQLite connection.

        The current TinyDB-based executor does not use this, but agents
        that rely on explicit SQL/ORM layers can.
        """

        return self._con, None, None
