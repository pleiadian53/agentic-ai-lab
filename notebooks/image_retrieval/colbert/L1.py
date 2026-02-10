#!/usr/bin/env python
# coding: utf-8

# # L1 - Multi-vector Text Retrieval: ColBERT

# <p style="background-color:#fff6e4; padding:15px; border-width:3px; border-color:#f5ecda; border-style:solid; border-radius:6px"> ⏳ <b>Note <code>(Kernel Starting)</code>:</b> This notebook takes about 30 seconds to be ready to use. You may start and watch the video while you wait.</p>

# <div style="background-color:#fff6ff; padding:13px; border-width:3px; border-color:#efe6ef; border-style:solid; border-radius:6px">
# <p> 💻 &nbsp; <b>Access <code>requirements.txt</code> and <code>helper.py</code> files:</b> 1) click on the <em>"File"</em> option on the top menu of the notebook and then 2) click on <em>"Open"</em>.
# 
# <p> ⬇ &nbsp; <b>Download Notebooks:</b> 1) click on the <em>"File"</em> option on the top menu of the notebook and then 2) click on <em>"Download as"</em> and select <em>"Notebook (.ipynb)"</em>.</p>
# 
# <p> 📒 &nbsp; For more help, please see the <em>"Appendix – Tips, Help, and Download"</em> Lesson.</p>
# 
# </div>

# The following cell is not in the video and just ensures output later in this notebook will render properly.

# In[ ]:


import plotly.io as pio
pio.renderers.default = "notebook"


# #### Load ColBERT

# In[ ]:


from fastembed import LateInteractionTextEmbedding

colbert_model = LateInteractionTextEmbedding(
    model_name="colbert-ir/colbertv2.0"
)
colbert_model.embedding_size


# #### Create, Tokenize, and Embed Document

# In[ ]:


document = """This study examines the environmental benefits of 
electric bus fleets in three major metropolitan areas over a 
two-year period. Our analysis shows that electric buses reduce 
carbon emissions by an average of 65% compared to traditional 
diesel buses, while also decreasing noise pollution in urban 
centers by 40 decibels."""


# In[ ]:


from helper import tokenize_late_interaction

document_tokens = tokenize_late_interaction(colbert_model, document)
document_tokens


# In[ ]:


len(document_tokens)


# In[ ]:


document_embeddings = next(colbert_model.passage_embed([document]))
document_embeddings


# #### Create, Tokenize, and Embed Query

# In[ ]:


query = "advantages of EV cars"


# In[ ]:


query_embeddings = next(colbert_model.query_embed([query]))
query_embeddings.shape


# In[ ]:


query_tokens = tokenize_late_interaction(
    colbert_model, query, is_doc=False
)
query_tokens


# #### Calculate Similarity Matrix Between Query and Document

# In[ ]:


import numpy as np

similarity_matrix = np.dot(query_embeddings, document_embeddings.T)
similarity_matrix


# In[ ]:


maxsim_score = similarity_matrix.max(axis=1).sum()
maxsim_score


# In[ ]:


from helper import visualize_maxsim_matrix

fig = visualize_maxsim_matrix(
    similarity_matrix,
    query_tokens=query_tokens,
    document_tokens=document_tokens,
    width=600,
)
fig.show()


# #### Importing Text Embedding Model

# In[ ]:


from fastembed import TextEmbedding

dense_model = TextEmbedding("BAAI/bge-small-en-v1.5")


# #### Creating Collection in Qdrant

# In[ ]:


# Keep the collection and vector name for easy reference
collection_name = "colbert-tests"
dense_vector_name = "BAAI-bge-small-en-v1.5"
colbert_vector_name = "colbert-ir-colbertv2.0"


# In[ ]:


from qdrant_client import QdrantClient, models

# Connect to Qdrant and create a collection
client = QdrantClient("http://localhost:6333")
client.delete_collection(collection_name)
client.create_collection(
    collection_name,
    vectors_config={
        dense_vector_name: models.VectorParams(
            size=dense_model.embedding_size,
            distance=models.Distance.COSINE,
        ),
        colbert_vector_name: models.VectorParams(
            # Size of an individual token vector
            size=colbert_model.embedding_size,
            # Distance function to be used for similarity
            distance=models.Distance.DOT,
            multivector_config=models.MultiVectorConfig(
                # Enable MaxSim comparison for the multivectors
                comparator=models.MultiVectorComparator.MAX_SIM,
            ),
            # Disable HNSW, as it won't be used either way
            hnsw_config=models.HnswConfigDiff(m=0),
        ),
    },
)


# #### Creating Documents and Adding to Qdrant Collection

# In[ ]:


documents = [
    "Qdrant is a vector database designed for similarity search applications",
    "SQL databases use structured tables with predefined schemas for data storage",
    "Using Qdrant you can store embeddings and perform efficient searches",
    "Traditional SQL queries filter data using exact matches and joins",
    "Qdrant supports multi-vector configurations for late interaction models like ColBERT",
    "SQL performs well for transactional workloads but lacks semantic search capabilities",
    "The Qdrant client allows you to create collections with custom distance metrics",
    "Migrating from SQL to vector databases enables similarity-based retrieval at scale",
    "Qdrant's MaxSim comparator enables token-level similarity scoring for multi-vectors",
    "SQL databases struggle with high-dimensional embeddings unlike specialized vector stores",
]


# In[ ]:


client.upsert(
    collection_name,
    points=[
        models.PointStruct(
            id=i,
            vector={
                dense_vector_name: next(
                    dense_model.passage_embed([document])
                ),
                colbert_vector_name: next(
                    colbert_model.passage_embed([document])
                ),
            },
            payload={"text": document},
        )
        for i, document in enumerate(documents, start=1)
    ],
)


# #### Helper Functions for ColBERT and Standard Query

# In[ ]:


import time


def colbert_query(q: str, limit: int = 5) -> list[dict]:
    start_time = time.monotonic()
    embedding = next(colbert_model.query_embed(q))
    end_time = time.monotonic()
    print("ColBERT vector generation time:", end_time - start_time)

    start_time = time.monotonic()
    result = client.query_points(
        collection_name,
        query=embedding,
        using=colbert_vector_name,
        limit=limit,
        with_payload=True,
    )
    end_time = time.monotonic()
    print("Query time:", end_time - start_time)

    return [point.payload for point in result.points]


# In[ ]:


def dense_query(q: str, limit: int = 5) -> list[dict]:
    start_time = time.monotonic()
    embedding = next(dense_model.query_embed(q))
    end_time = time.monotonic()
    print("Dense vector generation time:", end_time - start_time)

    start_time = time.monotonic()
    result = client.query_points(
        collection_name,
        query=embedding,
        using=dense_vector_name,
        limit=limit,
        with_payload=True,
    )
    end_time = time.monotonic()
    print("Query time:", end_time - start_time)

    return [point.payload for point in result.points]


# #### Creating a Sample Query

# In[ ]:


query = "search performance in Qdrant"


# In[ ]:


query_tokens = tokenize_late_interaction(
    colbert_model, query, is_doc=False
)
query_tokens


# #### Comparing Results from ColBERT and Dense Query

# In[ ]:


colbert_hits = colbert_query(query)
dense_hits = dense_query(query)


# In[ ]:


from helper import display_results_side_by_side

display_results_side_by_side(
    left_results=colbert_hits,
    right_results=dense_hits,
    left_title="ColBERT Results",
    right_title="Dense Results",
    query=query,
)


# #### Exploring ColBERT Scoring for Top Document Retrieved by ColBERT

# In[ ]:


# Get the best match from the ColBERT results and tokenize it
top_document = colbert_hits[0]["text"]
top_document_tokens = tokenize_late_interaction(
    colbert_model, top_document
)

# Calculate the ColBERT representation of the document and query
top_document_vector = next(colbert_model.passage_embed([top_document]))
query_vector = next(colbert_model.query_embed([query]))


# In[ ]:


similarity_matrix = np.dot(query_vector, top_document_vector.T)


# In[ ]:


fig = visualize_maxsim_matrix(
    similarity_matrix,
    query_tokens=query_tokens,
    document_tokens=top_document_tokens,
    width=600,
)
fig.show()

