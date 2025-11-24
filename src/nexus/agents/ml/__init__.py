"""
Machine Learning Agent
======================

Flexible machine learning workflows for predictions and analysis.

Sub-Agents:
    - Splice Predictor: Per-nucleotide splice site scoring using OpenSpliceAI
    - Cancer Classifier: Cancer type classification from omics data
    - Drug Response: Drug response and sensitivity prediction
    - Custom Models: User-defined ML workflows and model training

This agent provides a unified interface for various ML tasks, from
pre-trained model inference to custom model training and deployment.

Example:
    >>> from nexus.agents.ml import MLAgent
    >>> from nexus.agents.ml.splice_predictor import SplicePredictorAgent
    >>> 
    >>> # Use pre-trained OpenSpliceAI
    >>> splice_agent = SplicePredictorAgent(model="openspliceai")
    >>> scores = splice_agent.predict(sequence="ATCG...", positions=[100, 200])
    >>> 
    >>> # Train custom cancer classifier
    >>> from nexus.agents.ml.cancer_classifier import CancerClassifierAgent
    >>> cancer_agent = CancerClassifierAgent()
    >>> cancer_agent.train(data=expression_data, labels=cancer_types)
    >>> predictions = cancer_agent.predict(new_samples)
"""

__all__ = ["MLAgent"]
