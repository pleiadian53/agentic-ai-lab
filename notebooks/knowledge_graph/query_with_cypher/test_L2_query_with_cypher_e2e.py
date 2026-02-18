#!/usr/bin/env python
"""
End-to-end test script for L2-query_with_cypher.ipynb

Run from repo root or from this directory. Requires .env in this directory
with NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE (e.g. Neo4j sandbox).
"""
import os
import sys
import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

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
# Step 1: Imports and env
# ---------------------------------------------------------------------------
log_step("Imports and load env")
try:
    from dotenv import load_dotenv, find_dotenv
    import warnings
    warnings.filterwarnings("ignore")
    # find_dotenv() walks up to the project-level .env automatically
    load_dotenv(find_dotenv(), override=True)
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")
    if not all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD]):
        raise RuntimeError("Missing Neo4j env: set NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD (and optionally NEO4J_DATABASE) in .env")
    log_ok("Env loaded")
except Exception as e:
    log_error("Imports and load env", e)
    print("\n  Skipping remaining steps (Neo4j not configured).")
    print(f"\n  SUMMARY: 1 error (env/imports). Fix .env and re-run.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Step 2: Neo4j graph client
# ---------------------------------------------------------------------------
log_step("Connect to Neo4j (Neo4jGraph)")
try:
    from langchain_neo4j import Neo4jGraph
    kg = Neo4jGraph(
        url=NEO4J_URI,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
        database=NEO4J_DATABASE,
    )
    log_ok("Neo4jGraph initialized")
except Exception as e:
    log_error("Connect to Neo4j", e)
    print("\n  FATAL: Cannot continue without Neo4j.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Step 3: MATCH (n) RETURN count(n)
# ---------------------------------------------------------------------------
log_step("MATCH (n) RETURN count(n)")
try:
    cypher = """
  MATCH (n)
  RETURN count(n) AS numberOfNodes
  """
    result = kg.query(cypher)
    assert isinstance(result, list) and len(result) >= 1
    assert "numberOfNodes" in result[0]
    log_ok(f"numberOfNodes = {result[0]['numberOfNodes']}")
except Exception as e:
    log_error("MATCH (n) RETURN count(n)", e)

# ---------------------------------------------------------------------------
# Step 4: MATCH Movie, Person counts
# ---------------------------------------------------------------------------
log_step("MATCH (m:Movie) and (people:Person) counts")
try:
    r1 = kg.query("MATCH (m:Movie) RETURN count(m) AS numberOfMovies")
    r2 = kg.query("MATCH (people:Person) RETURN count(people) AS numberOfPeople")
    assert r1[0]["numberOfMovies"] >= 0 and r2[0]["numberOfPeople"] >= 0
    log_ok("Movie and Person counts OK")
except Exception as e:
    log_error("MATCH Movie/Person counts", e)

# ---------------------------------------------------------------------------
# Step 5: MATCH specific person and movie
# ---------------------------------------------------------------------------
log_step("MATCH Tom Hanks and Cloud Atlas")
try:
    r_person = kg.query('MATCH (tom:Person {name:"Tom Hanks"}) RETURN tom')
    r_movie = kg.query('MATCH (cloudAtlas:Movie {title:"Cloud Atlas"}) RETURN cloudAtlas')
    assert len(r_person) >= 1 and len(r_movie) >= 1
    log_ok("Tom Hanks and Cloud Atlas matched")
except Exception as e:
    log_error("MATCH Tom Hanks / Cloud Atlas", e)

# ---------------------------------------------------------------------------
# Step 6: RETURN properties (released, tagline)
# ---------------------------------------------------------------------------
log_step("RETURN cloudAtlas.released and tagline")
try:
    r = kg.query("""
  MATCH (cloudAtlas:Movie {title:"Cloud Atlas"})
  RETURN cloudAtlas.released, cloudAtlas.tagline
  """)
    assert len(r) >= 1
    log_ok("Properties returned")
except Exception as e:
    log_error("RETURN properties", e)

# ---------------------------------------------------------------------------
# Step 7: WHERE nineties (1990–1999)
# ---------------------------------------------------------------------------
log_step("WHERE nineties movies")
try:
    cypher = """
  MATCH (nineties:Movie)
  WHERE nineties.released >= 1990
    AND nineties.released < 2000
  RETURN nineties.title
  """
    result = kg.query(cypher)
    assert isinstance(result, list)
    log_ok(f"{len(result)} titles returned")
except Exception as e:
    log_error("WHERE nineties", e)

# ---------------------------------------------------------------------------
# Step 8: Pattern ACTED_IN, Tom Hanks movies, co-actors
# ---------------------------------------------------------------------------
log_step("ACTED_IN pattern and Tom Hanks co-actors")
try:
    r1 = kg.query("""
  MATCH (actor:Person)-[:ACTED_IN]->(movie:Movie)
  RETURN actor.name, movie.title LIMIT 10
  """)
    r2 = kg.query("""
  MATCH (tom:Person {name: "Tom Hanks"})-[:ACTED_IN]->(tomHanksMovies:Movie)
  RETURN tom.name, tomHanksMovies.title
  """)
    r3 = kg.query("""
  MATCH (tom:Person {name:"Tom Hanks"})-[:ACTED_IN]->(m)<-[:ACTED_IN]-(coActors)
  RETURN coActors.name, m.title
  """)
    assert isinstance(r1, list) and isinstance(r2, list) and isinstance(r3, list)
    log_ok("ACTED_IN and co-actor queries OK")
except Exception as e:
    log_error("ACTED_IN patterns", e)

# ---------------------------------------------------------------------------
# Step 9: Emil Eifrem ACTED_IN (query then DELETE)
# ---------------------------------------------------------------------------
log_step("Emil Eifrem ACTED_IN query and DELETE")
try:
    r_before = kg.query("""
MATCH (emil:Person {name:"Emil Eifrem"})-[actedIn:ACTED_IN]->(movie:Movie)
RETURN emil.name, movie.title
""")
    kg.query("""
MATCH (emil:Person {name:"Emil Eifrem"})-[actedIn:ACTED_IN]->(movie:Movie)
DELETE actedIn
""")
    r_after = kg.query("""
MATCH (emil:Person {name:"Emil Eifrem"})-[actedIn:ACTED_IN]->(movie:Movie)
RETURN emil.name, movie.title
""")
    assert isinstance(r_after, list) and len(r_after) == 0
    log_ok("DELETE actedIn succeeded")
except Exception as e:
    log_error("Emil Eifrem DELETE", e)

# ---------------------------------------------------------------------------
# Step 10: CREATE Andreas, MERGE WORKS_WITH
# ---------------------------------------------------------------------------
log_step("CREATE Andreas and MERGE WORKS_WITH Emil")
try:
    # Create Andreas if not exists (MERGE for idempotent re-runs)
    kg.query("""
MERGE (andreas:Person {name:"Andreas"})
RETURN andreas
""")
    r = kg.query("""
MATCH (andreas:Person {name:"Andreas"}), (emil:Person {name:"Emil Eifrem"})
MERGE (andreas)-[hasRelationship:WORKS_WITH]->(emil)
RETURN andreas, hasRelationship, emil
""")
    assert isinstance(r, list) and len(r) >= 1
    log_ok("CREATE and MERGE OK")
except Exception as e:
    log_error("CREATE Andreas / MERGE WORKS_WITH", e)

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
