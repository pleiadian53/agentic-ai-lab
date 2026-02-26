# docs/applications/ — Shareable Application Documentation

This directory holds **shareable, publication-quality documentation** for applications
currently under development. Unlike the raw dev notes in `dev/applications/`, these docs
are written for external readers: collaborators, users, or future contributors.

## Structure

```
docs/applications/
└── nexus/            # Nexus Research Agent — KG + RAG + multi-agent system
```

## Writing Standard

Documents here should:
- Be written in tutorial or reference style (not session logs)
- Assume a technically literate reader with no project context
- Include working code examples and architecture diagrams
- Be updated when the corresponding feature stabilizes (not every iteration)

## Lifecycle

```
docs/applications/<app>/  ← polished, shareable docs (this directory)
        ↓ (on graduation)
docs/products/<app>/      ← product documentation
```

## Applications

| App | Status | Source |
|---|---|---|
| `nexus` | Active | `src/nexus/` |
