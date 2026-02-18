from flask import Flask, request, jsonify
import threading
import json
import numpy as np
import torch
import threading
import logging
from utils import generate_embedding
# Initialize models globally to load them once

app = Flask(__name__)

@app.route('/.well-known/ready', methods=['GET'])
def readiness_check():
    return "Ready", 200

@app.route('/meta', methods=['GET'])
def readiness_check_2():
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
        
        text = data.get('text', '')
        if isinstance(text, list):
            text = " ".join(text)
        
        embeddings = generate_embedding([text] if isinstance(text, str) else text)

        return jsonify({'vector': embeddings})

    except Exception as e:
        print(f"[/vectors] ERROR: {e}")
        return jsonify({'error': str(e)}), 500
    
app.logger.disabled = True
# Get the Flask app's logger
log = logging.getLogger('werkzeug')
# Set logging level (ERROR or CRITICAL suppresses routing logs)
log.setLevel(logging.ERROR)
def run_app():
    app.run(host='0.0.0.0', port=9500, debug=False)

flask_thread = threading.Thread(target=run_app, daemon=True)
flask_thread.start()
