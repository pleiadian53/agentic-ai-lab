"""Tests for the customer service tool registry.

This module tests the tool registry API with different CustomerServiceStore
backends to ensure DB abstraction works correctly.
"""

import pytest
from multiagent.customer_service.data_access import (
    TinyDBStore,
    DuckDBStore,
    SQLiteStore,
)
from multiagent.customer_service.tool_registry import (
    TOOL_REGISTRY,
    TOOL_SIGNATURES,
    canonicalize_args,
    missing_required,
    resolve_args,
    run_tools_for_step,
    run_tool_validation,
)


# =========================
# Fixtures
# =========================
@pytest.fixture(params=["tinydb", "duckdb", "sqlite"])
def store(request, tmp_path):
    """Parametrized fixture providing all store backends."""
    if request.param == "tinydb":
        db_path = str(tmp_path / "test_store.json")
        s = TinyDBStore(path=db_path)
    elif request.param == "duckdb":
        s = DuckDBStore(db_path=None)  # in-memory
    elif request.param == "sqlite":
        s = SQLiteStore(db_path=":memory:")
    else:
        raise ValueError(f"Unknown store type: {request.param}")
    
    s.seed_demo_data()
    return s


@pytest.fixture
def context(store):
    """Create a context dict with store handle."""
    return {"__store__": store}


# =========================
# Registry structure tests
# =========================
def test_tool_registry_contains_expected_tools():
    """Verify TOOL_REGISTRY has all expected tool names."""
    expected = [
        "get_inventory_data",
        "get_transaction_data",
        "lookup_product",
        "update_inventory",
        "append_transaction",
        "propose_transaction",
        "project_inventory",
        "compute_total",
        "compute_refund",
        "assert_true",
        "assert",
        "assert_non_null",
        "assert_gt",
        "assert_nonnegative_stock",
    ]
    
    for tool_name in expected:
        assert tool_name in TOOL_REGISTRY, f"Missing tool: {tool_name}"


def test_tool_signatures_match_registry():
    """Verify TOOL_SIGNATURES keys match TOOL_REGISTRY keys."""
    assert set(TOOL_SIGNATURES.keys()) == set(TOOL_REGISTRY.keys())


# =========================
# READ tool tests
# =========================
def test_get_inventory_data_all(store):
    """Test get_inventory_data with no filters returns all items."""
    result = TOOL_REGISTRY["get_inventory_data"](store=store)
    
    assert "rows" in result
    assert "match_count" in result
    assert "item" in result
    
    assert result["match_count"] > 0
    assert len(result["rows"]) == result["match_count"]
    # No single item when returning all
    assert result["item"] is None


def test_get_inventory_data_by_name(store):
    """Test get_inventory_data with product_name filter."""
    # Seed data includes "Aviator"
    result = TOOL_REGISTRY["get_inventory_data"](store=store, product_name="Aviator")
    
    assert result["match_count"] == 1
    assert len(result["rows"]) == 1
    assert result["item"] is not None
    assert result["item"]["name"] == "Aviator"


def test_get_inventory_data_case_insensitive(store):
    """Test get_inventory_data is case-insensitive."""
    result = TOOL_REGISTRY["get_inventory_data"](store=store, product_name="aviator")
    
    assert result["match_count"] == 1
    assert result["item"]["name"] == "Aviator"


def test_get_inventory_data_by_item_id(store):
    """Test get_inventory_data with item_id filter."""
    # Get first item's ID
    all_items = store.get_inventory_rows()
    first_id = all_items[0]["item_id"]
    
    result = TOOL_REGISTRY["get_inventory_data"](store=store, item_id=first_id)
    
    assert result["match_count"] == 1
    assert result["item"]["item_id"] == first_id


def test_get_transaction_data_last_balance(store):
    """Test get_transaction_data returns last balance."""
    result = TOOL_REGISTRY["get_transaction_data"](store=store, mode="last_balance")
    
    assert result["mode"] == "last_balance"
    assert "last_txn_id" in result
    assert "last_balance" in result
    assert isinstance(result["last_balance"], float)


# =========================
# WRITE tool tests
# =========================
def test_update_inventory_with_quantity_new(store):
    """Test update_inventory with absolute quantity."""
    all_items = store.get_inventory_rows()
    item_id = all_items[0]["item_id"]
    
    result = TOOL_REGISTRY["update_inventory"](
        store=store,
        item_id=item_id,
        quantity_new=100
    )
    
    assert "updated" in result
    assert result["updated"]["item_id"] == item_id
    assert result["updated"]["quantity_in_stock"] == 100
    
    # Verify in store
    updated_items = store.get_inventory_rows()
    updated_item = next(r for r in updated_items if r["item_id"] == item_id)
    assert updated_item["quantity_in_stock"] == 100


def test_update_inventory_with_delta(store):
    """Test update_inventory with delta."""
    all_items = store.get_inventory_rows()
    item = all_items[0]
    item_id = item["item_id"]
    original_qty = item["quantity_in_stock"]
    
    result = TOOL_REGISTRY["update_inventory"](
        store=store,
        item_id=item_id,
        delta=5
    )
    
    assert result["updated"]["quantity_in_stock"] == original_qty + 5


def test_update_inventory_missing_item(store):
    """Test update_inventory with non-existent item_id."""
    result = TOOL_REGISTRY["update_inventory"](
        store=store,
        item_id="NONEXISTENT",
        quantity_new=10
    )
    
    assert "error" in result
    assert result["error"] == "item_not_found"


def test_append_transaction(store):
    """Test append_transaction creates new transaction."""
    initial_balance = store.get_current_balance()
    
    result = TOOL_REGISTRY["append_transaction"](
        store=store,
        customer_name="Test Customer",
        summary="Test purchase",
        amount=100.0
    )
    
    assert "transaction" in result
    txn = result["transaction"]
    assert txn["customer_name"] == "Test Customer"
    assert txn["transaction_summary"] == "Test purchase"
    assert txn["transaction_amount"] == 100.0
    assert txn["balance_after_transaction"] == initial_balance + 100.0
    
    # Verify in store
    new_balance = store.get_current_balance()
    assert new_balance == initial_balance + 100.0


def test_propose_transaction_does_not_mutate(store):
    """Test propose_transaction doesn't change store state."""
    initial_balance = store.get_current_balance()
    initial_txn_count = len(store.get_transaction_rows())
    
    result = TOOL_REGISTRY["propose_transaction"](
        store=store,
        customer_name="Test Customer",
        summary="Test proposal",
        amount=50.0
    )
    
    assert result["balance_after_transaction"] == initial_balance + 50.0
    
    # Verify store unchanged
    assert store.get_current_balance() == initial_balance
    assert len(store.get_transaction_rows()) == initial_txn_count


def test_project_inventory(store):
    """Test project_inventory (alias for update with delta)."""
    all_items = store.get_inventory_rows()
    item = all_items[0]
    item_id = item["item_id"]
    original_qty = item["quantity_in_stock"]
    
    result = TOOL_REGISTRY["project_inventory"](
        store=store,
        item_id=item_id,
        delta=-3
    )
    
    assert result["updated"]["quantity_in_stock"] == original_qty - 3


# =========================
# Helper tool tests
# =========================
def test_compute_total():
    """Test compute_total calculates correctly."""
    result = TOOL_REGISTRY["compute_total"](qty=3, price=50.0)
    
    assert result["amount"] == 150.0


def test_compute_refund():
    """Test compute_refund returns negative amount."""
    result = TOOL_REGISTRY["compute_refund"](qty=2, price=25.0)
    
    assert result["amount"] == -50.0


# =========================
# Validation tool tests
# =========================
def test_assert_true():
    """Test assert_true validation."""
    assert TOOL_REGISTRY["assert_true"](value=True)["ok"] is True
    assert TOOL_REGISTRY["assert_true"](value=False)["ok"] is False
    assert TOOL_REGISTRY["assert_true"](value=1)["ok"] is True
    assert TOOL_REGISTRY["assert_true"](value=0)["ok"] is False


def test_assert_non_null():
    """Test assert_non_null validation."""
    assert TOOL_REGISTRY["assert_non_null"](value="something")["ok"] is True
    assert TOOL_REGISTRY["assert_non_null"](value=None)["ok"] is False


def test_assert_gt():
    """Test assert_gt validation."""
    assert TOOL_REGISTRY["assert_gt"](value=10, threshold=5)["ok"] is True
    assert TOOL_REGISTRY["assert_gt"](value=5, threshold=10)["ok"] is False
    assert TOOL_REGISTRY["assert_gt"](value=5, threshold=5)["ok"] is False


def test_assert_nonnegative_stock(store):
    """Test assert_nonnegative_stock validation."""
    all_items = store.get_inventory_rows()
    item_id = all_items[0]["item_id"]
    
    result = TOOL_REGISTRY["assert_nonnegative_stock"](store=store, item_id=item_id)
    
    assert result["ok"] is True
    assert "qty" in result


# =========================
# Argument canonicalization tests
# =========================
def test_canonicalize_args_compute_total():
    """Test canonicalize_args maps quantity->qty, unit_price->price."""
    args = {"quantity": 5, "unit_price": 10.0}
    canonical = canonicalize_args("compute_total", args)
    
    assert canonical["qty"] == 5
    assert canonical["price"] == 10.0
    assert "quantity" not in canonical
    assert "unit_price" not in canonical


def test_canonicalize_args_get_inventory():
    """Test canonicalize_args maps name->product_name."""
    args = {"name": "Aviator"}
    canonical = canonicalize_args("get_inventory_data", args)
    
    assert canonical["product_name"] == "Aviator"
    assert "name" not in canonical


def test_canonicalize_args_update_inventory():
    """Test canonicalize_args maps change->delta."""
    args = {"item_id": "SG001", "change": -2}
    canonical = canonicalize_args("update_inventory", args)
    
    assert canonical["delta"] == -2
    assert "change" not in canonical


# =========================
# Missing required args tests
# =========================
def test_missing_required_compute_total():
    """Test missing_required detects missing args."""
    assert missing_required("compute_total", {}) == ["qty", "price"]
    assert missing_required("compute_total", {"qty": 3}) == ["price"]
    assert missing_required("compute_total", {"qty": 3, "price": 10}) == []


def test_missing_required_update_inventory():
    """Test missing_required for update_inventory (needs delta or quantity_new)."""
    # Missing item_id
    assert "item_id" in missing_required("update_inventory", {})
    
    # Has item_id but missing delta/quantity_new
    missing = missing_required("update_inventory", {"item_id": "SG001"})
    assert "delta|quantity_new" in missing
    
    # Has item_id and delta
    assert missing_required("update_inventory", {"item_id": "SG001", "delta": 5}) == []
    
    # Has item_id and quantity_new
    assert missing_required("update_inventory", {"item_id": "SG001", "quantity_new": 10}) == []


# =========================
# Context resolution tests
# =========================
def test_resolve_args_with_context():
    """Test resolve_args resolves context references."""
    ctx = {"product_result": {"item": {"price": 75.0}}}
    args = {"qty": 2, "price_from": "context.product_result.item.price"}
    
    resolved = resolve_args(args, ctx)
    
    assert resolved["qty"] == 2
    assert resolved["price"] == 75.0


def test_resolve_args_missing_context_path():
    """Test resolve_args handles missing context paths."""
    ctx = {"product_result": {"item": {}}}
    args = {"price_from": "context.product_result.item.price"}
    
    resolved = resolve_args(args, ctx)
    
    assert resolved["price"] is None


# =========================
# Step execution tests
# =========================
def test_run_tools_for_step_single_tool(context):
    """Test run_tools_for_step executes a single tool."""
    step = {
        "tools": [
            {
                "use": "get_inventory_data",
                "result_key": "inventory",
                "args": {"product_name": "Aviator"}
            }
        ]
    }
    
    results = run_tools_for_step(step, context)
    
    assert "inventory" in results
    assert results["inventory"]["match_count"] == 1
    assert "inventory" in context  # Result stored in context


def test_run_tools_for_step_multiple_tools(context):
    """Test run_tools_for_step executes multiple tools in sequence."""
    step = {
        "tools": [
            {
                "use": "get_inventory_data",
                "result_key": "product",
                "args": {"product_name": "Aviator"}
            },
            {
                "use": "compute_total",
                "result_key": "total",
                "args": {"qty": 3, "price_from": "context.product.item.price"}
            }
        ]
    }
    
    results = run_tools_for_step(step, context)
    
    assert "product" in results
    assert "total" in results
    
    # Verify compute_total used price from first tool result
    price = context["product"]["item"]["price"]
    assert results["total"]["amount"] == 3 * price


def test_run_tools_for_step_unknown_tool(context):
    """Test run_tools_for_step raises error for unknown tool."""
    step = {
        "tools": [
            {
                "use": "nonexistent_tool",
                "result_key": "result",
                "args": {}
            }
        ]
    }
    
    with pytest.raises(ValueError, match="Unknown tool"):
        run_tools_for_step(step, context)


def test_run_tools_for_step_missing_required_args(context):
    """Test run_tools_for_step raises error for missing required args."""
    step = {
        "tools": [
            {
                "use": "compute_total",
                "result_key": "total",
                "args": {"qty": 3}  # Missing price
            }
        ]
    }
    
    with pytest.raises(ValueError, match="Missing required args"):
        run_tools_for_step(step, context)


# =========================
# Validation execution tests
# =========================
def test_run_tool_validation_success(context):
    """Test run_tool_validation with passing validation."""
    validation = {
        "name": "check_positive",
        "use_tool": "assert_gt",
        "args": {"value": 10, "threshold": 5}
    }
    
    result = run_tool_validation(validation, context)
    
    assert result["name"] == "check_positive"
    assert result["ok"] is True


def test_run_tool_validation_failure(context):
    """Test run_tool_validation with failing validation."""
    validation = {
        "name": "check_positive",
        "use_tool": "assert_gt",
        "args": {"value": 3, "threshold": 5}
    }
    
    result = run_tool_validation(validation, context)
    
    assert result["name"] == "check_positive"
    assert result["ok"] is False


def test_run_tool_validation_unknown_tool(context):
    """Test run_tool_validation with unknown tool."""
    validation = {
        "name": "test",
        "use_tool": "nonexistent_tool",
        "args": {}
    }
    
    result = run_tool_validation(validation, context)
    
    assert result["ok"] is False
    assert "unknown_tool" in result["error"]


def test_run_tool_validation_missing_args(context):
    """Test run_tool_validation with missing required args."""
    validation = {
        "name": "test",
        "use_tool": "assert_gt",
        "args": {"value": 10}  # Missing threshold
    }
    
    result = run_tool_validation(validation, context)
    
    assert result["ok"] is False
    assert "missing_required_args" in result["error"]


# =========================
# Integration test: complete workflow
# =========================
def test_complete_purchase_workflow(context):
    """Test a complete purchase workflow using multiple tools."""
    # Step 1: Look up product
    step1 = {
        "tools": [
            {
                "use": "lookup_product",
                "result_key": "product",
                "args": {"product_name": "Aviator"}
            }
        ]
    }
    run_tools_for_step(step1, context)
    
    assert context["product"]["match_count"] == 1
    item = context["product"]["item"]
    original_qty = item["quantity_in_stock"]
    price = item["price"]
    
    # Step 2: Compute total
    step2 = {
        "tools": [
            {
                "use": "compute_total",
                "result_key": "total",
                "args": {"qty": 2, "price": price}
            }
        ]
    }
    run_tools_for_step(step2, context)
    
    assert context["total"]["amount"] == 2 * price
    
    # Step 3: Update inventory
    step3 = {
        "tools": [
            {
                "use": "update_inventory",
                "result_key": "inv_update",
                "args": {"item_id": item["item_id"], "delta": -2}
            }
        ]
    }
    run_tools_for_step(step3, context)
    
    assert context["inv_update"]["updated"]["quantity_in_stock"] == original_qty - 2
    
    # Step 4: Append transaction
    step4 = {
        "tools": [
            {
                "use": "append_transaction",
                "result_key": "txn",
                "args": {
                    "customer_name": "John Doe",
                    "summary": "Purchase 2x Aviator",
                    "amount": context["total"]["amount"]
                }
            }
        ]
    }
    run_tools_for_step(step4, context)
    
    assert context["txn"]["transaction"]["customer_name"] == "John Doe"
    assert context["txn"]["transaction"]["transaction_amount"] == 2 * price
