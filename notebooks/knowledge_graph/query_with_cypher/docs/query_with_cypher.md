# Querying a Knowledge Graph with Cypher

This tutorial walks through using the **Cypher** query language to interact with a Neo4j knowledge graph that contains data about actors and movies. It accompanies the notebook `L2-query_with_cypher.ipynb` and assumes you have a Neo4j instance (e.g. Neo4j Aura or Sandbox) loaded with the movie dataset.

---

## 1. Setup: Imports and Neo4j Connection

The notebook uses **python-dotenv** to load configuration and **LangChain’s Neo4j integration** to talk to the graph.

- **Neo4j URI**: connection string (host, port, protocol).
- **Username and password**: credentials for the database.
- **Database name**: optional; defaults to `neo4j` if not set.

Credentials are stored in the **project-level `.env`** at the `agentic-ai-lab/` repo root. The notebook calls `load_dotenv(find_dotenv(), override=True)`, which walks up the directory tree to locate that file automatically — regardless of Jupyter's working directory. See `.env.example` at the repo root for the required keys: `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, and optionally `NEO4J_DATABASE`. After loading them, you create a `Neo4jGraph` instance and run Cypher via `kg.query(cypher)`.

---

## 2. The Graph Schema: Nodes, Properties, and Relationships

The movie graph has two main node types and several relationship types.

### Nodes

- **Person**: people (actors, directors, reviewers, etc.).  
  Properties: `name`, `born` (year).
- **Movie**: films.  
  Properties: `title`, `tagline` (strings), `released` (year, integer).

### Relationships

- **Person → Movie**: `ACTED_IN`, `DIRECTED`, `WROTE` (and possibly others). A person can have multiple roles (e.g. acted in and directed the same movie).
- **Person → Person**: e.g. one person **follows** another (e.g. follower of a reviewer).

Which relationships exist for a given person or movie is determined by the data; the schema describes *possible* relationship types.

---

## 3. Cypher Basics: MATCH and RETURN

**Cypher** is Neo4j’s query language. It uses **pattern matching** to find subgraphs inside the database.

A minimal query matches all nodes and returns a count:

```cypher
MATCH (n)
RETURN count(n)
```

In Python, `kg.query(cypher)` returns a **list of dictionaries**. The keys of each dictionary come from the names used in the `RETURN` clause. Using an alias makes the result easier to use:

```cypher
MATCH (n)
RETURN count(n) AS numberOfNodes
```

Then `result[0]['numberOfNodes']` gives the count (e.g. 171). This is the same pattern used in the notebook to print: “There are X nodes in this graph.”

---

## 4. Filtering by Node Labels: Movie and Person

Nodes can have **labels** such as `Movie` or `Person`. To match only movies, use the label after a colon:

```cypher
MATCH (n:Movie)
RETURN count(n) AS numberOfMovies
```

Same idea for people:

```cypher
MATCH (people:Person)
RETURN count(people) AS numberOfPeople
```

Using meaningful variable names (e.g. `m` for movies, `people` for persons) improves readability. For example:

```cypher
MATCH (m:Movie)
RETURN count(m) AS numberOfMovies
```

The result is unchanged; only the variable name in the pattern changes.

---

## 5. Matching Specific Nodes by Property

To find a single node by a property value, use **inline property filters** in curly braces:

**Find a specific person (e.g. Tom Hanks):**

```cypher
MATCH (tom:Person {name: "Tom Hanks"})
RETURN tom
```

The result includes the full node (e.g. `name`, `born`).

**Find a specific movie (e.g. Cloud Atlas):**

```cypher
MATCH (cloudAtlas:Movie {title: "Cloud Atlas"})
RETURN cloudAtlas
```

You get the full node, including `title`, `tagline`, and `released` (e.g. 2012).

---

## 6. Returning Specific Properties

Instead of returning the whole node, return one or more properties:

**Only the release year of “Cloud Atlas”:**

```cypher
MATCH (cloudAtlas:Movie {title: "Cloud Atlas"})
RETURN cloudAtlas.released
```

**Release year and tagline:**

```cypher
MATCH (cloudAtlas:Movie {title: "Cloud Atlas"})
RETURN cloudAtlas.released, cloudAtlas.tagline
```

The Python result is again a list of dictionaries, with keys matching the return expressions (e.g. `cloudAtlas.released`, `cloudAtlas.tagline`).

---

## 7. Conditional Matching with WHERE

To filter by conditions (e.g. release year), use **WHERE** after **MATCH**:

```cypher
MATCH (nineties:Movie)
WHERE nineties.released >= 1990 AND nineties.released < 2000
RETURN nineties.title
```

This returns the titles of all movies released in the 1990s. The same idea extends to other numeric or string conditions.

---

## 8. Pattern Matching: Relationships (ACTED_IN)

Cypher patterns describe **paths** in the graph: nodes and the relationships between them.

**Actors and the movies they acted in (first 10):**

```cypher
MATCH (actor:Person)-[:ACTED_IN]->(movie:Movie)
RETURN actor.name, movie.title
LIMIT 10
```

- `(actor:Person)`: a node with label `Person`.
- `-[:ACTED_IN]->`: an outgoing `ACTED_IN` relationship.
- `(movie:Movie)`: a node with label `Movie`.

So this pattern reads as: “Person who ACTED_IN Movie.”

**Movies for one actor (e.g. Tom Hanks):**

```cypher
MATCH (tom:Person {name: "Tom Hanks"})-[:ACTED_IN]->(tomHanksMovies:Movie)
RETURN tom.name, tomHanksMovies.title
```

**Co-actors: people who acted in the same movie as Tom Hanks:**

```cypher
MATCH (tom:Person {name: "Tom Hanks"})-[:ACTED_IN]->(m)<-[:ACTED_IN]-(coActors)
RETURN coActors.name, m.title
```

Here, `(m)` is a movie that Tom Hanks acted in, and `coActors` are people who also have an `ACTED_IN` relationship to that same movie. The pattern is: Tom → movie ← co-actors.

---

## 9. Deleting Data: Removing a Relationship

The movie dataset includes **Emil Eifrem** (founder of Neo4j) as having `ACTED_IN` a movie (e.g. The Matrix). He is kept as a person node, but we can remove his `ACTED_IN` relationship so he no longer appears as an actor.

**Find Emil’s ACTED_IN roles:**

```cypher
MATCH (emil:Person {name: "Emil Eifrem"})-[actedIn:ACTED_IN]->(movie:Movie)
RETURN emil.name, movie.title
```

**Delete those ACTED_IN relationships:**

```cypher
MATCH (emil:Person {name: "Emil Eifrem"})-[actedIn:ACTED_IN]->(movie:Movie)
DELETE actedIn
```

This removes only the relationship(s); the `Person` and `Movie` nodes remain. The query returns no rows. Re-running the first query should then return no results for Emil’s acting roles.

---

## 10. Creating Data: Nodes and Relationships

### Creating a node (CREATE)

**Create a new person:**

```cypher
CREATE (andreas:Person {name: "Andreas"})
RETURN andreas
```

- `CREATE`: create the pattern if it doesn’t exist.
- `(andreas:Person {name: "Andreas"})`: one node with label `Person` and property `name`.

Each run of this query creates a *new* node unless you guard it (e.g. with `MERGE`).

### Creating a relationship (MERGE)

Relationships connect two nodes. To add a relationship:

1. **MATCH** (or create) the two nodes.
2. Use **MERGE** (or CREATE) to add the relationship between them.

**Example: link Andreas to Emil with a WORKS_WITH relationship:**

```cypher
MATCH (andreas:Person {name: "Andreas"}), (emil:Person {name: "Emil Eifrem"})
MERGE (andreas)-[hasRelationship:WORKS_WITH]->(emil)
RETURN andreas, hasRelationship, emil
```

- **MERGE**: create the relationship only if it does not already exist; avoids duplicates if you run the query multiple times.
- **CREATE** would create a new relationship every time.

So: **CREATE** for “always create,” **MERGE** for “create only if missing.”

---

## 11. Summary and Next Steps

In this lesson you:

- Connected to Neo4j via LangChain and ran Cypher with `kg.query(...)`.
- Used **MATCH** and **RETURN** to count nodes and filter by labels (`Movie`, `Person`).
- Matched specific nodes by properties `{name: "..."}` and returned selected properties.
- Used **WHERE** for conditional filters (e.g. release year).
- Wrote relationship patterns like `(Person)-[:ACTED_IN]->(Movie)` and queried co-actors.
- **DELETE**d a relationship (Emil’s `ACTED_IN`) and **CREATE**d a node and **MERGE**d a relationship.

For a **RAG application** over a knowledge graph, you typically need text (or embeddings) from the graph. The next step is to turn text fields in the graph into **vector embeddings** and store them so you can do **vector similarity search** alongside Cypher queries.

---

**Related files**

- Notebook: `L2-query_with_cypher.ipynb`
- E2E test: `test_L2_query_with_cypher_e2e.py`
- Troubleshooting: `docs/troubleshooting_L2_query_with_cypher.md`
