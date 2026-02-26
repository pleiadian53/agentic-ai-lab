#!/usr/bin/env python
"""
End-to-end test script for C1M2_Ungraded_Lab_2.ipynb (Retrieval Metrics)
Tests: dataset loading, embedding model, cosine similarity, precision@k, recall@k,
and full metric computation pipeline.
"""
import sys
import os
import traceback

# ---------------------------------------------------------------------------
# Load .env from project root (HF_TOKEN, etc.)
# ---------------------------------------------------------------------------
def load_dotenv(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

load_dotenv(os.path.join(os.path.dirname(__file__), "../../../../.env"))

# Change to notebook directory so embeddings.joblib resolves correctly
os.chdir(os.path.dirname(os.path.abspath(__file__)))

errors_log = []

def log_step(step_name):
    print(f"\n{'='*60}\n  STEP: {step_name}\n{'='*60}")

def log_ok(msg="OK"):
    print(f"  ✓ {msg}")

def log_error(step, exc):
    tb = traceback.format_exc()
    errors_log.append({"step": step, "error": str(exc), "traceback": tb})
    print(f"  ✗ ERROR: {exc}\n{tb}")

# ---------------------------------------------------------------------------
# Cell 4: Imports
# ---------------------------------------------------------------------------
log_step("Cell 4: Imports")
try:
    import pandas as pd
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")   # non-interactive backend for testing
    import matplotlib.pyplot as plt
    import joblib
    log_ok("All imports succeeded")
except Exception as e:
    log_error("Cell 4: imports", e)
    print("\nFATAL: Cannot continue without imports. Exiting.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Cell 6: Load 20 Newsgroups dataset
# ---------------------------------------------------------------------------
log_step("Cell 6: Load 20 Newsgroups dataset")
try:
    from sklearn.datasets import fetch_20newsgroups
    newsgroups_train = fetch_20newsgroups(
        subset='train', shuffle=True, random_state=42, data_home='./dataset'
    )
    df = pd.DataFrame({
        'text': newsgroups_train.data,
        'category': newsgroups_train.target
    })
    assert df.shape == (11314, 2), f"Unexpected shape: {df.shape}"
    assert len(newsgroups_train.target_names) == 20
    log_ok(f"Dataset loaded: {df.shape[0]} rows, {len(newsgroups_train.target_names)} categories")
except Exception as e:
    log_error("Cell 6: load dataset", e)
    print("\nFATAL: Cannot continue without dataset. Exiting.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Cell 7: Sample row display
# ---------------------------------------------------------------------------
log_step("Cell 7: Sample row access")
try:
    sample_text = df['text'][0]
    sample_category = newsgroups_train.target_names[df['category'][0]]
    assert len(sample_text) > 0
    log_ok(f"Sample category: {sample_category}")
except Exception as e:
    log_error("Cell 7: sample row", e)

# ---------------------------------------------------------------------------
# Cell 9: Load model and embeddings
# FIXED: use model_name directly (HF cache) instead of os.environ['MODELS']
# ---------------------------------------------------------------------------
log_step("Cell 9: Load SentenceTransformer model and embeddings.joblib")
try:
    model_name = "BAAI/bge-base-en-v1.5"
    # Use local MODELS path if available, otherwise fall back to HF cache
    if 'MODELS' in os.environ:
        model_path = os.path.join(os.environ['MODELS'], model_name)
    else:
        model_path = model_name   # resolved from ~/.cache/huggingface/hub
    model = SentenceTransformer(model_path)
    log_ok(f"Model loaded: {model_name}")

    assert os.path.exists('embeddings.joblib'), "embeddings.joblib not found in working directory"
    embedding_vectors = joblib.load('embeddings.joblib')
    log_ok(f"embeddings.joblib loaded: {len(embedding_vectors)} embeddings")
except Exception as e:
    log_error("Cell 9: load model and embeddings", e)
    print("\nFATAL: Cannot continue without model and embeddings. Exiting.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Cell 10: Check embedding count
# ---------------------------------------------------------------------------
log_step("Cell 10: Verify embedding count matches dataset")
try:
    n_emb = len(embedding_vectors)
    assert n_emb == len(df), f"Mismatch: {n_emb} embeddings vs {len(df)} documents"
    log_ok(f"Embedding count matches dataset: {n_emb}")
except Exception as e:
    log_error("Cell 10: embedding count check", e)

# ---------------------------------------------------------------------------
# Cell 12: Define helper functions
# ---------------------------------------------------------------------------
log_step("Cell 12: Define preprocess_text, cosine_similarity, top_k_greatest_indices")
try:
    def preprocess_text(text):
        return text.strip()

    def cosine_similarity(v1, array_of_vectors):
        if hasattr(v1, "detach"):
            v1 = v1.detach().cpu().numpy()
        v1 = np.asarray(v1, dtype=np.float32).ravel()
        if hasattr(array_of_vectors, "detach"):
            array_of_vectors = array_of_vectors.detach().cpu().numpy()
        A = np.asarray(array_of_vectors, dtype=np.float32)
        if A.ndim == 1:
            A = A.ravel()
            denom = np.linalg.norm(v1) * np.linalg.norm(A)
            return float(0.0 if denom == 0 else np.dot(v1, A) / denom)
        A = np.atleast_2d(A)
        v1_norm = np.linalg.norm(v1)
        A_norms = np.linalg.norm(A, axis=1)
        denom = v1_norm * A_norms
        with np.errstate(divide='ignore', invalid='ignore'):
            sims = (A @ v1) / np.where(denom == 0, 1.0, denom)
        sims[denom == 0] = 0.0
        return sims.tolist()

    def top_k_greatest_indices(lst, k):
        indexed_list = list(enumerate(lst))
        sorted_by_value = sorted(indexed_list, key=lambda x: x[1], reverse=True)
        return [index for index, value in sorted_by_value[:k]]

    # Unit-test cosine_similarity
    a = np.array([1.0, 0.0, 0.0])
    b = np.array([1.0, 0.0, 0.0])
    assert abs(cosine_similarity(a, b) - 1.0) < 1e-5, "Identical vectors should have sim=1.0"
    c = np.array([0.0, 1.0, 0.0])
    assert abs(cosine_similarity(a, c) - 0.0) < 1e-5, "Orthogonal vectors should have sim=0.0"

    # Unit-test top_k_greatest_indices
    assert top_k_greatest_indices([0.1, 0.9, 0.5], 2) == [1, 2]

    log_ok("Helper functions defined and unit-tested")
except Exception as e:
    log_error("Cell 12: helper function definitions", e)
    print("\nFATAL: Cannot continue without helper functions. Exiting.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Cell 14: Define and test retrieve_documents (1 query, top_k=2)
# ---------------------------------------------------------------------------
log_step("Cell 14: retrieve_documents on a sample query")
try:
    def retrieve_documents(query, embeddings, model, top_k=5):
        query_clean = preprocess_text(query)
        query_embedding = model.encode(query_clean, convert_to_tensor=False).astype(np.float32)
        cosine_scores = []
        for x in embeddings:
            if hasattr(x, "detach"):
                x = x.detach().cpu().numpy()
            x = np.asarray(x, dtype=np.float32)
            cosine_scores.append(float(cosine_similarity(query_embedding, x)))
        top_results = top_k_greatest_indices(cosine_scores, k=top_k)
        return top_results

    top_results = retrieve_documents("space exploration", embedding_vectors, model, top_k=2)
    assert len(top_results) == 2
    retrieved_cats = [newsgroups_train.target_names[df.iloc[i]['category']] for i in top_results]
    log_ok(f"retrieve_documents returned {len(top_results)} results: categories={retrieved_cats}")
except Exception as e:
    log_error("Cell 14: retrieve_documents", e)

# ---------------------------------------------------------------------------
# Cell 16: Define and test precision_at_k
# ---------------------------------------------------------------------------
log_step("Cell 16: precision_at_k definition and unit tests")
try:
    def precision_at_k(relevant_count, k):
        if relevant_count < 0 or k < 0:
            raise ValueError("All input values must be non-negative.")
        if k == 0:
            return 0.0
        return relevant_count / k

    assert precision_at_k(3, 5) == 0.6
    assert precision_at_k(0, 5) == 0.0
    assert precision_at_k(5, 5) == 1.0
    assert precision_at_k(0, 0) == 0.0
    log_ok("precision_at_k defined and unit-tested")
except Exception as e:
    log_error("Cell 16: precision_at_k", e)

# ---------------------------------------------------------------------------
# Cell 18: Define and test recall_at_k
# ---------------------------------------------------------------------------
log_step("Cell 18: recall_at_k definition and unit tests")
try:
    def recall_at_k(relevant_count, total_relevant):
        if relevant_count < 0 or total_relevant < 0:
            raise ValueError("All input values must be non-negative.")
        if total_relevant == 0:
            return 0.0
        return relevant_count / total_relevant

    assert recall_at_k(3, 10) == 0.3
    assert recall_at_k(0, 10) == 0.0
    assert recall_at_k(0, 0) == 0.0
    log_ok("recall_at_k defined and unit-tested")
except Exception as e:
    log_error("Cell 18: recall_at_k", e)

# ---------------------------------------------------------------------------
# Cell 20: Define test queries
# ---------------------------------------------------------------------------
log_step("Cell 20: Define test_queries")
try:
    test_queries = [
        {"query": "advancements in space exploration technology", "desired_category": "sci.space"},
        {"query": "real-time rendering techniques in computer graphics", "desired_category": "comp.graphics"},
        {"query": "latest findings in cardiovascular medical research", "desired_category": "sci.med"},
        {"query": "NHL playoffs and team performance statistics", "desired_category": "rec.sport.hockey"},
        {"query": "impacts of cryptography in online security", "desired_category": "sci.crypt"},
        {"query": "the role of electronics in modern computing devices", "desired_category": "sci.electronics"},
        {"query": "motorcycles maintenance tips for enthusiasts", "desired_category": "rec.motorcycles"},
        {"query": "high-performance baseball tactics for championships", "desired_category": "rec.sport.baseball"},
        {"query": "historical influence of politics on society", "desired_category": "talk.politics.misc"},
        {"query": "latest technology trends in the Windows operating system", "desired_category": "comp.os.ms-windows.misc"},
    ]
    assert len(test_queries) == 10
    log_ok(f"test_queries defined: {len(test_queries)} queries")
except Exception as e:
    log_error("Cell 20: define test_queries", e)

# ---------------------------------------------------------------------------
# Cell 21: Define compute_metrics
# ---------------------------------------------------------------------------
log_step("Cell 21: Define compute_metrics")
try:
    def compute_metrics(queries, embeddings, model, top_k=5):
        results = []
        np_embeddings = []
        for x in embeddings:
            if hasattr(x, "detach"):
                x = x.detach().cpu().numpy()
            np_embeddings.append(np.asarray(x, dtype=np.float32).ravel())
        E = np.vstack(np_embeddings)

        for item in queries:
            query = item["query"]
            desired_category = item["desired_category"]
            q_clean = preprocess_text(query)
            q_emb = model.encode(q_clean, convert_to_tensor=False)
            q_emb = np.asarray(q_emb, dtype=np.float32).ravel()
            cosine_scores = cosine_similarity(q_emb, E)
            top_results = top_k_greatest_indices(cosine_scores, k=top_k)
            retrieved_categories = [
                newsgroups_train.target_names[df.iloc[idx]["category"]] for idx in top_results
            ]
            relevant_in_top_k = sum(1 for cat in retrieved_categories if cat == desired_category)
            total_relevant_in_corpus = sum(
                1 for idx in range(len(df))
                if newsgroups_train.target_names[df.iloc[idx]["category"]] == desired_category
            )
            p = precision_at_k(relevant_in_top_k, top_k)
            r = recall_at_k(relevant_in_top_k, total_relevant_in_corpus)
            results.append({"query": query, "precision@k": p, "recall@k": r})
        return results

    log_ok("compute_metrics defined")
except Exception as e:
    log_error("Cell 21: define compute_metrics", e)
    print("\nFATAL: Cannot continue without compute_metrics. Exiting.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Cell 22: Run compute_metrics — test K=5 (full pipeline validation)
# K=20 and K=50 omitted here; same code path, just larger K
# ---------------------------------------------------------------------------
log_step("Cell 22: compute_metrics K=5 over all 10 queries")
try:
    results = compute_metrics(test_queries, embedding_vectors, model, top_k=5)
    assert len(results) == 10, f"Expected 10 results, got {len(results)}"
    for r in results:
        assert "precision@k" in r and "recall@k" in r
        assert 0.0 <= r["precision@k"] <= 1.0, f"precision out of range: {r}"
        assert 0.0 <= r["recall@k"] <= 1.0, f"recall out of range: {r}"
    avg_p = sum(r["precision@k"] for r in results) / len(results)
    avg_r = sum(r["recall@k"] for r in results) / len(results)
    log_ok(f"All 10 queries computed. Avg Precision@5={avg_p:.2f}, Avg Recall@5={avg_r:.4f}")
    for r in results:
        print(f"    {r['query'][:50]:<50}  P@5={r['precision@k']:.2f}  R@5={r['recall@k']:.4f}")
except Exception as e:
    log_error("Cell 22: compute_metrics K=5", e)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print(f"\n{'='*60}\n  SUMMARY\n{'='*60}")
if errors_log:
    print(f"\n  {len(errors_log)} ERROR(S) FOUND:\n")
    for i, err in enumerate(errors_log, 1):
        print(f"  {i}. [{err['step']}]\n     {err['error']}\n")
    sys.exit(1)
else:
    print("\n  ALL STEPS PASSED ✓\n")
    sys.exit(0)
