from flask import Flask, request, jsonify
import threading
import json
from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np
import torch
import logging
import os

# ---------------------------------------------------------------------------
# Initialize models globally (loaded once at import time)
# ---------------------------------------------------------------------------
_cache_dir = os.environ.get("VECTORDB_MODEL_CACHE", None)

# Embedding model — used by Weaviate's text2vec-transformers module
embedder = SentenceTransformer('BAAI/bge-base-en-v1.5', cache_folder=_cache_dir, device='cpu')

# Reranker model — used by Weaviate's reranker-transformers module
reranker = CrossEncoder('BAAI/bge-reranker-base', device='cpu')

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------
app = Flask(__name__)

@app.route('/.well-known/ready', methods=['GET'])
def readiness_check():
    return "Ready", 200

@app.route('/meta', methods=['GET'])
def meta():
    return jsonify({'status': 'Ready'}), 200

@app.route('/vectors', methods=['POST'])
def vectorize():
    """
    Weaviate text2vec-transformers sends:
        POST /vectors  {"text": "some text to embed", ...}
    and expects:
        {"text": "...", "vector": [0.1, 0.2, ...], "dim": 768}
    """
    try:
        # Use force=True to parse JSON regardless of Content-Type header
        data = request.get_json(force=True)
        if data is None:
            data = json.loads(request.data.decode("utf-8"))

        text = data.get("text", "")
        if isinstance(text, list):
            text = " ".join(text)

        vector = embedder.encode(text).tolist()
        return jsonify({"text": text, "vector": vector, "dim": len(vector)})

    except Exception as e:
        print(f"[/vectors] ERROR: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/rerank', methods=['POST'])
def rerank():
    """
    Weaviate reranker-transformers sends:
        POST /rerank  {"query": "...", "documents": ["doc1", "doc2", ...]}
    and expects:
        {"scores": [{"document": "doc1", "score": 0.9}, ...]}
    """
    try:
        # Use force=True to parse JSON regardless of Content-Type header
        data = request.get_json(force=True)
        if data is None:
            data = json.loads(request.data.decode("utf-8"))

        query = data.get('query', '')
        documents = data.get('documents', [])

        if not documents:
            return jsonify({'scores': []})

        pairs = [(query, doc) for doc in documents]
        scores = reranker.predict(pairs)
        scores_list = scores.tolist() if hasattr(scores, 'tolist') else (scores if isinstance(scores, list) else [scores])

        results = [
            {"document": doc, "score": float(s)}
            for doc, s in zip(documents, scores_list)
        ]
        return jsonify({'scores': results})

    except Exception as e:
        print(f"[/rerank] ERROR: {e}")
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------------------------
# Suppress Flask request logs
# ---------------------------------------------------------------------------
app.logger.disabled = True
logging.getLogger('werkzeug').setLevel(logging.ERROR)

def run_app():
    app.run(host='0.0.0.0', port=9500, debug=False)

flask_thread = threading.Thread(target=run_app, daemon=True)
flask_thread.start()
