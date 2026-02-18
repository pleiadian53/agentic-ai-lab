#!/usr/bin/env python
"""
End-to-end test script for C1M3_Ungraded_Lab_1.ipynb
Converted from notebook cells to diagnose and fix all errors before they hit the user.
"""
import sys
import os
import time
import traceback

# Track errors for diagnostic report
errors_log = []

def log_step(step_name):
    print(f"\n{'='*60}")
    print(f"  STEP: {step_name}")
    print(f"{'='*60}")

def log_ok(msg="OK"):
    print(f"  ✓ {msg}")

def log_error(step, exc):
    tb = traceback.format_exc()
    errors_log.append({"step": step, "error": str(exc), "traceback": tb})
    print(f"  ✗ ERROR: {exc}")
    print(tb)

# ============================================================
# Cell 4: Environment + Imports
# ============================================================
log_step("Cell 4: Load environment and imports")
try:
    from dotenv import load_dotenv
    from agentic_core.paths import load_project_env

    load_project_env()
    log_ok("load_project_env()")

    # Verify critical env vars
    env_vars = ["VECTORDB_MODEL_CACHE"]
    for var in env_vars:
        val = os.environ.get(var)
        if val:
            log_ok(f"{var} is set ({val[:30]}...)")
        else:
            print(f"  ⚠ WARNING: {var} is NOT set in .env")

    from weaviate.classes.config import Configure, Property, DataType
    from weaviate.classes.query import Filter
    from typing import List
    from tqdm import tqdm
    import joblib
    import weaviate
    import re
    from weaviate.util import generate_uuid5
    from pprint import pprint
    log_ok("All imports succeeded")
except Exception as e:
    log_error("Cell 4: imports", e)
    print("\nFATAL: Cannot continue without basic imports. Exiting.")
    sys.exit(1)

# ============================================================
# Cell 5: Utils + Flask app
# ============================================================
log_step("Cell 5: Load utils and flask_app")
try:
    # We need to be in the notebook directory for relative imports
    notebook_dir = os.path.dirname(os.path.abspath(__file__))
    if notebook_dir not in sys.path:
        sys.path.insert(0, notebook_dir)

    from utils import (
        suppress_subprocess_output,
        generate_with_single_input,
        print_object_properties,
        kill_processes_on_ports
    )
    log_ok("utils imports succeeded")

    # Kill processes on the ports we'll use
    result = kill_processes_on_ports([5000, 9500, 8080, 8097, 50050, 50051])
    log_ok(f"kill_processes_on_ports: targeted={result['pids_targeted']}, no_match={result['ports_with_no_match']}")

    # Give the system a moment to release the ports
    time.sleep(1)

    import flask_app
    log_ok("flask_app imported (Flask server starting on port 9500)")

    # Give Flask a moment to start
    time.sleep(3)

    # Verify Flask is responding
    import requests
    try:
        resp = requests.get("http://127.0.0.1:9500/.well-known/ready", timeout=5)
        log_ok(f"Flask readiness check: {resp.status_code} {resp.text.strip()}")
    except Exception as e:
        log_error("Cell 5: Flask readiness check", e)
        print("\nFATAL: Flask server not responding. Exiting.")
        sys.exit(1)

except Exception as e:
    log_error("Cell 5: utils/flask_app", e)
    print("\nFATAL: Flask server not running. Exiting.")
    sys.exit(1)

# ============================================================
# Cell 8: Weaviate embedded client
# ============================================================
log_step("Cell 8: Connect to embedded Weaviate")
client = None
try:
    with suppress_subprocess_output():
        client = weaviate.connect_to_embedded(
            persistence_data_path=os.path.join(notebook_dir, ".collections"),
            environment_variables={
                "ENABLE_API_BASED_MODULES": "true",
                "ENABLE_MODULES": "text2vec-transformers, reranker-transformers",
                "TRANSFORMERS_INFERENCE_API": "http://127.0.0.1:9500/",
                "RERANKER_INFERENCE_API": "http://127.0.0.1:9500/"
            }
        )
    log_ok(f"Weaviate client connected: {client.is_ready()}")
except Exception as e:
    log_error("Cell 8: weaviate client", e)
    print("\nFATAL: Cannot continue without Weaviate. Exiting.")
    sys.exit(1)

# ============================================================
# Cell 11: Load data
# ============================================================
log_step("Cell 11: Load data")
data = None
try:
    data = joblib.load(os.path.join(notebook_dir, "data.joblib"))
    print_object_properties(data[0])
    log_ok(f"Loaded {len(data)} records")
except Exception as e:
    log_error("Cell 11: load data", e)
    print("\nFATAL: Cannot continue without data. Exiting.")
    sys.exit(1)

# ============================================================
# Cell 14: Vectorizer config
# ============================================================
log_step("Cell 14: Vectorizer config")
vectorizer_config = None
try:
    vectorizer_config = [Configure.NamedVectors.text2vec_transformers(
        name="vector",
        source_properties=['place', 'state', 'description', 'best_season_to_visit', 'attractions', 'budget'],
        vectorize_collection_name=False,
        inference_url="http://127.0.0.1:9500",
    )]
    log_ok("vectorizer_config created")
except Exception as e:
    log_error("Cell 14: vectorizer config", e)
    print("\nFATAL: Cannot continue without vectorizer config. Exiting.")
    sys.exit(1)

# ============================================================
# Cells 16-17: Create collection
# ============================================================
log_step("Cells 16-17: Create collection")
collection = None
try:
    # Cell 16: Delete if exists (note: original notebook has typo "example_collectiom")
    if client.collections.exists("example_collection"):
        client.collections.delete("example_collection")
        log_ok("Deleted existing 'example_collection'")

    # Cell 17: Create
    if not client.collections.exists('example_collection'):
        collection = client.collections.create(
            name='example_collection',
            vectorizer_config=vectorizer_config,
            reranker_config=Configure.Reranker.transformers(),
            properties=[
                Property(name="place", vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name="state", vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name="description", vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name="best_season_to_visit", vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name="attractions", vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name="budget", vectorize_property_name=True, data_type=DataType.TEXT),
                Property(name="user_ratings", data_type=DataType.NUMBER),
                Property(name="last_updated", data_type=DataType.DATE),
            ]
        )
        log_ok("Collection 'example_collection' created")
    else:
        collection = client.collections.get("example_collection")
        log_ok("Collection 'example_collection' already exists, retrieved it")
except Exception as e:
    log_error("Cells 16-17: create collection", e)
    print("\nFATAL: Cannot continue without collection. Exiting.")
    sys.exit(1)

# ============================================================
# Cell 19: Print collection
# ============================================================
log_step("Cell 19: Print collection")
try:
    print(collection)
    log_ok()
except Exception as e:
    log_error("Cell 19: print collection", e)

# ============================================================
# Cell 21: Duplicate creation (expected error)
# ============================================================
log_step("Cell 21: Duplicate creation (expected error)")
try:
    try:
        dup = client.collections.create(
            name='example_collection',
            vectorizer_config=vectorizer_config,
            properties=[
                Property(name="place", vectorize_property_name=True, data_type=DataType.TEXT),
            ]
        )
    except Exception as e:
        log_ok(f"Expected error caught: {str(e)[:80]}...")
except Exception as e:
    log_error("Cell 21: duplicate creation", e)

# ============================================================
# Cell 23: List collections
# ============================================================
log_step("Cell 23: List collections")
try:
    keys = client.collections.list_all().keys()
    log_ok(f"Collections: {list(keys)}")
except Exception as e:
    log_error("Cell 23: list collections", e)

# ============================================================
# Cell 26: Batch insert data
# ============================================================
log_step("Cell 26: Batch insert data")
try:
    initial_count = len(collection)
    log_ok(f"Initial collection size: {initial_count}")
    
    if initial_count == 0:
        print("  Inserting data (this may take a few moments)...")
        with collection.batch.fixed_size(batch_size=1, concurrent_requests=1) as batch:
            for document in tqdm(data, desc="  Inserting"):
                uuid = generate_uuid5(document)
                batch.add_object(
                    properties=document,
                    uuid=uuid,
                )
        log_ok(f"Inserted data. New collection size: {len(collection)}")
    else:
        log_ok(f"Collection already has data ({initial_count} items), skipping insert")
except Exception as e:
    log_error("Cell 26: batch insert", e)

# ============================================================
# Cell 28: Collection length
# ============================================================
log_step("Cell 28: Collection length")
try:
    log_ok(f"len(collection) = {len(collection)}")
except Exception as e:
    log_error("Cell 28: collection length", e)

# ============================================================
# Cell 31: Filter query
# ============================================================
log_step("Cell 31: Filter query")
try:
    result = collection.query.fetch_objects(
        limit=2,
        filters=Filter.by_property('user_ratings').greater_or_equal(3.5)
    )
    log_ok(f"Fetched {len(result.objects)} objects with user_ratings >= 3.5")
    for obj in result.objects:
        print_object_properties(obj.properties)
except Exception as e:
    log_error("Cell 31: filter query", e)

# ============================================================
# Cell 42: Semantic search (near_text)
# ============================================================
log_step("Cell 42: Semantic search")
try:
    result = collection.query.near_text(
        query='I want suggestions to travel during Winter. I want cheap places.',
        limit=4
    )
    log_ok(f"near_text returned {len(result.objects)} results")
    for obj in result.objects:
        print_object_properties(obj.properties)
except Exception as e:
    log_error("Cell 42: semantic search", e)

# ============================================================
# Cell 45: Semantic search + filter
# ============================================================
log_step("Cell 45: Semantic search + filter (budget=Low)")
try:
    result = collection.query.near_text(
        query='I want suggestions to travel during Winter. I want cheap places.',
        filters=Filter.by_property('budget').equal('Low'),
        limit=4
    )
    log_ok(f"near_text + filter returned {len(result.objects)} results")
    for obj in result.objects:
        print_object_properties(obj.properties)
except Exception as e:
    log_error("Cell 45: semantic search + filter", e)

# ============================================================
# Cell 48: Semantic search + contains_any filter
# ============================================================
log_step("Cell 48: Semantic search + contains_any filter")
try:
    result = collection.query.near_text(
        query='I want suggestions to travel during Winter. I want cheap places.',
        filters=Filter.by_property('budget').contains_any(['Low', 'Moderate']),
        limit=4
    )
    log_ok(f"near_text + contains_any returned {len(result.objects)} results")
    for obj in result.objects:
        print_object_properties(obj.properties)
except Exception as e:
    log_error("Cell 48: semantic search + contains_any", e)

# ============================================================
# Cell 51: BM25 search
# ============================================================
log_step("Cell 51: BM25 search")
try:
    result = collection.query.bm25(
        query='I want suggestions to travel during Winter. I want cheap places.',
        filters=Filter.by_property('budget').contains_any(['Low', 'Moderate']),
        limit=4
    )
    log_ok(f"bm25 returned {len(result.objects)} results")
    for obj in result.objects:
        print_object_properties(obj.properties)
except Exception as e:
    log_error("Cell 51: BM25 search", e)

# ============================================================
# Cell 54: Hybrid search
# ============================================================
log_step("Cell 54: Hybrid search")
try:
    result = collection.query.hybrid(
        query='I want suggestions to travel during Winter. I want cheap places.',
        filters=Filter.by_property('budget').contains_any(['Low', 'Moderate']),
        alpha=0.3,
        limit=4
    )
    log_ok(f"hybrid returned {len(result.objects)} results")
    for obj in result.objects:
        print_object_properties(obj.properties)
except Exception as e:
    log_error("Cell 54: hybrid search", e)

# ============================================================
# Cell 57: Reranking
# ============================================================
log_step("Cell 57: Reranking")
try:
    from weaviate.classes.query import Rerank
    response = collection.query.near_text(
        query="I want suggestions to travel during Winter. I want cheap and fun places.",
        limit=5,
        rerank=Rerank(
            prop="attractions",
            query="Fun places"
        )
    )
    log_ok(f"reranked near_text returned {len(response.objects)} results")
    for obj in response.objects:
        print_object_properties(obj.properties)
except Exception as e:
    log_error("Cell 57: reranking", e)

# ============================================================
# Cell 59: Close client
# ============================================================
log_step("Cell 59: Close client")
try:
    client.close()
    log_ok("Client closed")
except Exception as e:
    log_error("Cell 59: close client", e)

# ============================================================
# Summary
# ============================================================
print(f"\n{'='*60}")
print(f"  SUMMARY")
print(f"{'='*60}")
if errors_log:
    print(f"\n  {len(errors_log)} ERROR(S) FOUND:\n")
    for i, err in enumerate(errors_log, 1):
        print(f"  {i}. [{err['step']}]")
        print(f"     {err['error']}")
        print()
    sys.exit(1)
else:
    print("\n  ALL STEPS PASSED ✓\n")
    sys.exit(0)
