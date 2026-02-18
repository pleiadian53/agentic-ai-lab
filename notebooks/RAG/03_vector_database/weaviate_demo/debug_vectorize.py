#!/usr/bin/env python
"""Debug script to test what Weaviate sends to the /vectors endpoint."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentic_core.paths import load_project_env
load_project_env()

from flask import request as freq
import flask_app

# Add request logging
@flask_app.app.before_request
def log_request():
    print(f"[REQ] {freq.method} {freq.path}", flush=True)
    if freq.data:
        print(f"[BODY] {freq.data[:500]}", flush=True)

@flask_app.app.after_request
def log_response(response):
    body = response.get_data(as_text=True)
    print(f"[RESP] {response.status_code} len={len(body)}", flush=True)
    if len(body) < 300:
        print(f"[RESP_BODY] {body}", flush=True)
    return response

time.sleep(2)
print("Flask ready on port 9500", flush=True)

import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.util import generate_uuid5

client = weaviate.connect_to_embedded(
    persistence_data_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".collections_debug"),
    environment_variables={
        "ENABLE_API_BASED_MODULES": "true",
        "ENABLE_MODULES": "text2vec-transformers, reranker-transformers",
        "TRANSFORMERS_INFERENCE_API": "http://127.0.0.1:9500/",
        "RERANKER_INFERENCE_API": "http://127.0.0.1:9500/"
    }
)
print(f"Weaviate ready: {client.is_ready()}", flush=True)

if client.collections.exists("debug_test"):
    client.collections.delete("debug_test")

coll = client.collections.create(
    name="debug_test",
    vectorizer_config=[Configure.NamedVectors.text2vec_transformers(
        name="vector",
        source_properties=["text"],
        vectorize_collection_name=False,
        inference_url="http://127.0.0.1:9500",
    )],
    properties=[Property(name="text", data_type=DataType.TEXT)]
)

coll.data.insert({"text": "hello world"}, uuid=generate_uuid5({"text": "hello world"}))
print("Inserted 1 doc", flush=True)
time.sleep(1)

try:
    result = coll.query.near_text(query="hello", limit=1)
    print(f"QUERY OK: {len(result.objects)} results", flush=True)
except Exception as e:
    print(f"QUERY ERROR: {e}", flush=True)

client.close()
print("DONE", flush=True)
