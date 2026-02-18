"""
Shared Neo4j connection helper for the knowledge_graph sub-project.

Loads credentials from the project-level .env using find_dotenv(), so this
works regardless of whether the caller is a notebook in
notebooks/knowledge_graph/ or a script in knowledge_graph/.

Usage:
    from knowledge_graph.utils.neo4j_connection import get_neo4j_graph

    kg = get_neo4j_graph()
    result = kg.query("MATCH (n) RETURN count(n) AS n")
"""

import os
from dotenv import load_dotenv, find_dotenv


def load_neo4j_env(override: bool = True) -> None:
    """Load Neo4j env vars from the nearest .env walking up the directory tree."""
    dotenv_path = find_dotenv(usecwd=True)
    load_dotenv(dotenv_path, override=override)


def get_neo4j_credentials() -> dict:
    """
    Return a dict of Neo4j credentials from environment variables.

    Raises:
        RuntimeError: if any required variable is missing.
    """
    load_neo4j_env()
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    database = os.getenv("NEO4J_DATABASE")  # optional; defaults handled by driver

    missing = [k for k, v in {"NEO4J_URI": uri, "NEO4J_USERNAME": username, "NEO4J_PASSWORD": password}.items() if not v]
    if missing:
        raise RuntimeError(
            f"Missing Neo4j environment variable(s): {', '.join(missing)}. "
            "Add them to the project-level .env (see .env.example)."
        )

    return {"url": uri, "username": username, "password": password, "database": database}


def get_neo4j_graph():
    """
    Create and return a LangChain Neo4jGraph instance using project-level credentials.

    Returns:
        Neo4jGraph: configured graph client.
    """
    from langchain_neo4j import Neo4jGraph

    creds = get_neo4j_credentials()
    return Neo4jGraph(**creds)
