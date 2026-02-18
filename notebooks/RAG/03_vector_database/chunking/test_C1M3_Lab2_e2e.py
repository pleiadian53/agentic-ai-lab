#!/usr/bin/env python
"""
End-to-end test script for C1M3_Ungraded_Lab_2.ipynb (Chunking)
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
# Cell 4: Imports
# ============================================================
log_step("Cell 4: Basic imports")
try:
    from typing import List
    import requests
    import re
    import weaviate
    from weaviate.classes.config import Configure, Property, DataType, Tokenization
    from weaviate.util import generate_uuid5
    import tqdm
    from weaviate.classes.query import Filter
    log_ok("All basic imports succeeded")
except Exception as e:
    log_error("Cell 4: imports", e)
    print("\nFATAL: Cannot continue without basic imports. Exiting.")
    sys.exit(1)

# ============================================================
# Cell 5: Utils + Flask app
# ============================================================
log_step("Cell 5: Load utils and flask_app")
try:
    notebook_dir = os.path.dirname(os.path.abspath(__file__))
    if notebook_dir not in sys.path:
        sys.path.insert(0, notebook_dir)

    from utils import (
        generate_with_single_input, 
        suppress_subprocess_output,
        kill_processes_on_ports
    )
    log_ok("utils imports succeeded")

    result = kill_processes_on_ports([5000, 9500, 8080, 8097, 50050, 50051])
    log_ok(f"kill_processes_on_ports: targeted={result['pids_targeted']}, no_match={result['ports_with_no_match']}")

    time.sleep(1)

    import flask_app
    log_ok("flask_app imported (Flask server starting)")

    time.sleep(3)

    import requests as req
    try:
        resp = req.get("http://127.0.0.1:9500/.well-known/ready", timeout=5)
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
# Cell 7: Download sample text
# ============================================================
log_step("Cell 7: Download sample text")
source_text = None
try:
    url = "https://raw.githubusercontent.com/progit/progit2/main/book/01-introduction/sections/what-is-git.asc"
    source_text = requests.get(url).text
    log_ok(f"Downloaded text ({len(source_text)} characters)")
except Exception as e:
    log_error("Cell 7: download text", e)
    print("\nFATAL: Cannot continue without source text. Exiting.")
    sys.exit(1)

# ============================================================
# Cell 8-9: Display and analyze text
# ============================================================
log_step("Cell 8-9: Display and analyze text")
try:
    print(source_text[:500])
    word_count = len(source_text.split())
    log_ok(f"{word_count} words, ~{round(word_count*1.3)} tokens")
except Exception as e:
    log_error("Cell 8-9: text analysis", e)

# ============================================================
# Cell 11-14: Fixed-size chunking
# ============================================================
log_step("Cell 11-14: Fixed-size chunking")
try:
    def get_chunks_fixed_size(text: str, chunk_size: int) -> List[str]:
        text_words = text.split()
        chunks = []
        for i in range(0, len(text_words), chunk_size):
            chunk_words = text_words[i: i + chunk_size]
            chunk = " ".join(chunk_words)
            chunks.append(chunk)
        return chunks

    fixed_size_chunks = get_chunks_fixed_size(source_text, chunk_size=100)
    log_ok(f"Created {len(fixed_size_chunks)} fixed-size chunks")
    log_ok(f"Sample chunks: {len(fixed_size_chunks[0:3])} shown")
except Exception as e:
    log_error("Cell 11-14: fixed-size chunking", e)

# ============================================================
# Cell 16-17: Chunking with overlap
# ============================================================
log_step("Cell 16-17: Chunking with overlap")
try:
    def get_chunks_fixed_size_with_overlap(text: str, chunk_size: int, overlap_fraction: float) -> List[str]:
        text_words = text.split()
        overlap_int = int(chunk_size * overlap_fraction)
        chunks = []
        for i in range(0, len(text_words), chunk_size):
            chunk_words = text_words[max(i - overlap_int, 0): i + chunk_size]
            chunk = " ".join(chunk_words)
            chunks.append(chunk)
        return chunks

    for chosen_size in [5, 25, 100]:
        chunks = get_chunks_fixed_size_with_overlap(source_text, chosen_size, overlap_fraction=0.2)
        log_ok(f"Size {chosen_size}: {len(chunks)} chunks")
except Exception as e:
    log_error("Cell 16-17: overlap chunking", e)

# ============================================================
# Cell 21-24: Variable-size chunking
# ============================================================
log_step("Cell 21-24: Variable-size chunking")
try:
    def get_chunks_by_paragraph(source_text: str) -> List[str]:
        return source_text.split("\n\n")

    def get_chunks_by_asciidoc_sections(source_text: str) -> List[str]:
        return source_text.split("\n==")

    for marker in ["\n\n", "\n=="]:
        chunks = source_text.split(marker)
        log_ok(f"Marker {repr(marker)}: {len(chunks)} chunks")
except Exception as e:
    log_error("Cell 21-24: variable-size chunking", e)

# ============================================================
# Cell 27-28: Mixed chunking
# ============================================================
log_step("Cell 27-28: Mixed chunking")
try:
    def mixed_chunking(source_text):
        chunks = source_text.split("\n==")
        new_chunks = []
        chunk_buffer = ""
        min_length = 25

        for chunk in chunks:
            new_buffer = chunk_buffer + chunk
            new_buffer_words = new_buffer.split(" ")
            if len(new_buffer_words) < min_length:
                chunk_buffer = new_buffer
            else:
                new_chunks.append(new_buffer)
                chunk_buffer = ""

        if len(chunk_buffer) > 0:
            new_chunks.append(chunk_buffer)

        return new_chunks

    mixed_chunks = mixed_chunking(source_text)
    log_ok(f"Mixed chunking: {len(mixed_chunks)} chunks")
except Exception as e:
    log_error("Cell 27-28: mixed chunking", e)

# ============================================================
# Cell 31-32: Get book text
# ============================================================
log_step("Cell 31-32: Get book text objects")
book_text_objs = None
try:
    def get_book_text_objects():
        text_objs = list()
        api_base_url = 'https://api.github.com/repos/progit/progit2/contents/book'
        chapter_urls = ['/01-introduction/sections', '/02-git-basics/sections']

        for chapter_url in chapter_urls:
            response = requests.get(api_base_url + chapter_url)

            for file_info in response.json():
                if file_info['type'] == 'file':
                    file_response = requests.get(file_info['download_url'])

                    chapter_title = file_info['download_url'].split('/')[-3]
                    filename = file_info['download_url'].split('/')[-1]
                    text_obj = {
                        "body": file_response.text,
                        "chapter_title": chapter_title,
                        "filename": filename
                    }
                    text_objs.append(text_obj)
        return text_objs

    book_text_objs = get_book_text_objects()
    log_ok(f"Downloaded {len(book_text_objs)} book sections")
except Exception as e:
    log_error("Cell 31-32: get book text", e)
    print("\nFATAL: Cannot continue without book text. Exiting.")
    sys.exit(1)

# ============================================================
# Cell 35-36: Build chunk objects
# ============================================================
log_step("Cell 35-36: Build chunk objects")
chunk_obj_sets = None
try:
    def build_chunk_objs(book_text_obj, chunks):
        chunk_objs = list()
        for i, c in enumerate(chunks):
            chunk_obj = {
                "chapter_title": book_text_obj["chapter_title"],
                "filename": book_text_obj["filename"],
                "chunk": c,
                "chunk_index": i
            }
            chunk_objs.append(chunk_obj)
        return chunk_objs

    chunk_obj_sets = dict()
    for book_text_obj in book_text_objs:
        text = book_text_obj["body"]

        for strategy_name, chunks in [
            ["fixed_size_25", get_chunks_fixed_size_with_overlap(text, 25, 0.2)],
            ["fixed_size_100", get_chunks_fixed_size_with_overlap(text, 100, 0.2)],
            ["para_chunks", get_chunks_by_paragraph(text)],
            ["para_chunks_min_25", mixed_chunking(text)]
        ]:
            chunk_objs = build_chunk_objs(book_text_obj, chunks)

            if strategy_name not in chunk_obj_sets.keys():
                chunk_obj_sets[strategy_name] = list()

            chunk_obj_sets[strategy_name] += chunk_objs

    log_ok(f"Chunking strategies: {list(chunk_obj_sets.keys())}")
    for strategy in chunk_obj_sets.keys():
        log_ok(f"  {strategy}: {len(chunk_obj_sets[strategy])} chunks")
except Exception as e:
    log_error("Cell 35-36: build chunk objects", e)

# ============================================================
# Cell 40: Weaviate client
# ============================================================
log_step("Cell 40: Connect to Weaviate")
client = None
try:
    kill_processes_on_ports([8080, 8079, 50050, 50051])

    collection_base = os.getenv('COLLECTION_M3', './')
    persistence_path = os.path.join(collection_base, 'ungraded_lab_2')

    with suppress_subprocess_output():
        try:
            client = weaviate.connect_to_embedded(
                persistence_data_path=persistence_path,
                environment_variables={
                    "ENABLE_API_BASED_MODULES": "true",
                    "ENABLE_MODULES": 'text2vec-transformers',
                    "TRANSFORMERS_INFERENCE_API": "http://127.0.0.1:9500/",
                }
            )
        except Exception as e:
            print(f"  Failed to connect to embedded Weaviate: {e}")
            print("  Falling back to local Weaviate connection...")
            try:
                client = weaviate.connect_to_local(port=8079, grpc_port=50050)
            except Exception as e2:
                print(f"  Failed to connect to local Weaviate: {e2}")
                print("  Trying alternative ports...")
                client = weaviate.connect_to_local(port=8080, grpc_port=50051)

    log_ok(f"Weaviate client connected: {client.is_ready()}")
except Exception as e:
    log_error("Cell 40: weaviate client", e)
    print("\nFATAL: Cannot continue without Weaviate. Exiting.")
    sys.exit(1)

# ============================================================
# Cell 41: Create/get collection
# ============================================================
log_step("Cell 41: Create/get collection")
collection = None
try:
    if not client.collections.exists("chunking_example"):
        collection = client.collections.create(
            name='chunking_example',

            vectorizer_config=[Configure.NamedVectors.text2vec_transformers(
                name="vector",
                vectorize_collection_name=False,
                inference_url="http://127.0.0.1:9500",
            )],

            properties=[
                Property(name="chunk", data_type=DataType.TEXT),
                Property(name="chapter_title", data_type=DataType.TEXT),
                Property(name="filename", data_type=DataType.TEXT),
                Property(name="chunking_strategy", data_type=DataType.TEXT, tokenization=Tokenization.FIELD),
                Property(name="chunk_index", data_type=DataType.INT),
            ]
        )
        log_ok("Created 'chunking_example' collection")
    else:
        collection = client.collections.get("chunking_example")
        log_ok("Retrieved existing 'chunking_example' collection")
except Exception as e:
    log_error("Cell 41: create collection", e)
    print("\nFATAL: Cannot continue without collection. Exiting.")
    sys.exit(1)

# ============================================================
# Cell 42: Add data (skipped if already populated)
# ============================================================
log_step("Cell 42: Add data to collection (if empty)")
try:
    initial_count = collection.aggregate.over_all().total_count
    log_ok(f"Collection has {initial_count} items")

    if initial_count == 0:
        print("  Inserting chunks (this may take several minutes)...")
        with collection.batch.fixed_size(batch_size=1, concurrent_requests=20) as batch:
            for chunking_strategy, chunk_objects in tqdm.tqdm(chunk_obj_sets.items()):
                for chunk_obj in chunk_objects:
                    chunk_obj["chunking_strategy"] = chunking_strategy
                    batch.add_object(
                        properties=chunk_obj,
                        uuid=generate_uuid5(chunk_obj)
                    )
        final_count = collection.aggregate.over_all().total_count
        log_ok(f"Inserted data. Collection now has {final_count} items")
    else:
        log_ok("Collection already populated, skipping insert")
except Exception as e:
    log_error("Cell 42: add data", e)

# ============================================================
# Cell 43: Count by strategy
# ============================================================
log_step("Cell 43: Count objects by strategy")
try:
    total = collection.aggregate.over_all().total_count
    log_ok(f"Total count: {total}")
    for chunking_strategy in chunk_obj_sets.keys():
        where_filter = Filter.by_property('chunking_strategy').equal(chunking_strategy)
        count = collection.aggregate.over_all(filters=where_filter).total_count
        log_ok(f"{chunking_strategy}: {count} chunks")
except Exception as e:
    log_error("Cell 43: count by strategy", e)

# ============================================================
# Cell 45: Semantic search test 1
# ============================================================
log_step("Cell 45: Semantic search - 'history of git'")
try:
    search_string = "history of git"
    for chunking_strategy in chunk_obj_sets.keys():
        where_filter = Filter.by_property('chunking_strategy').equal(chunking_strategy)
        response = collection.query.near_text(search_string, filters=where_filter, limit=2)
        log_ok(f"{chunking_strategy}: {len(response.objects)} results")
        if response.objects:
            print(f"    Sample: {response.objects[0].properties['chunk'][:100]}...")
except Exception as e:
    log_error("Cell 45: semantic search 1", e)

# ============================================================
# Cell 47: Semantic search test 2
# ============================================================
log_step("Cell 47: Semantic search - 'add url of remote repository'")
try:
    search_string = "how to add the url of a remote repository"
    for chunking_strategy in chunk_obj_sets.keys():
        where_filter = Filter.by_property('chunking_strategy').equal(chunking_strategy)
        response = collection.query.near_text(search_string, filters=where_filter, limit=2)
        log_ok(f"{chunking_strategy}: {len(response.objects)} results")
except Exception as e:
    log_error("Cell 47: semantic search 2", e)

# ============================================================
# Cell 51: RAG system integration
# ============================================================
log_step("Cell 51: RAG system integration")
try:
    PROMPT = "Using this information and only this information, please explain {search_string} in a few short points.\nContext: {context}"

    n_chunks_by_strat = dict()
    n_chunks_by_strat['fixed_size_25'] = 8
    n_chunks_by_strat['para_chunks'] = 8
    n_chunks_by_strat['fixed_size_100'] = 2
    n_chunks_by_strat['para_chunks_min_25'] = 2

    search_string = "history of git"

    for chunking_strategy in chunk_obj_sets.keys():
        where_filter = Filter.by_property('chunking_strategy').equal(chunking_strategy)
        response = collection.query.near_text(search_string, filters=where_filter, limit=n_chunks_by_strat[chunking_strategy])
        context_string = ""
        for obj in response.objects:
            context_string += obj.properties['chunk'] + '\n'
        prompt = PROMPT.format(search_string=search_string, context=context_string)
        response = generate_with_single_input(prompt, role='assistant')
        log_ok(f"{chunking_strategy} RAG response generated ({len(response['content'])} chars)")
except Exception as e:
    log_error("Cell 51: RAG integration", e)

# ============================================================
# Cell 52: Close client
# ============================================================
log_step("Cell 52: Close client")
try:
    client.close()
    log_ok("Client closed")
except Exception as e:
    log_error("Cell 52: close client", e)

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
