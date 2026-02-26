# Tool Orchestration Design for Rich Research Sources

## Problem Statement

As we expand from 4 tools to 6+ tools (and potentially 10+ in the future), we need better agentic patterns to:
1. **Select the right tools** for each query type
2. **Avoid tool overload** - don't call all tools for every query
3. **Synthesize diverse sources** - combine academic papers, community discussions, and web content
4. **Handle tool failures gracefully** - some tools may fail or return no results
5. **Optimize for cost and latency** - minimize unnecessary API calls

## Current Architecture (4 Tools)

```
Planner → Researcher → Writer → Editor
          ↓
    [Tavily, arXiv, Wikipedia, Europe PMC]
    (All tools available, agent decides which to use)
```

**Limitations:**
- No explicit tool selection strategy
- Agent may call all tools unnecessarily
- No prioritization based on query type
- Limited synthesis across diverse source types

## Proposed Improvements

### **Pattern 1: Tool Router Agent** 🎯 **RECOMMENDED**

Add a specialized **Tool Router** that analyzes the query and selects appropriate tools.

```
Planner → Tool Router → Researcher → Writer → Editor
          ↓
    [Academic] [Community] [Web] [Biomedical]
```

**How it works:**
1. **Planner** creates research plan with sections
2. **Tool Router** analyzes each section and selects tools:
   - "AGI consciousness" → Reddit + Semantic Scholar + Tavily
   - "CRISPR mechanisms" → arXiv + Europe PMC + Wikipedia
   - "Fractal ML" → Reddit + Semantic Scholar + arXiv
3. **Researcher** only uses selected tools for each section
4. **Writer** synthesizes diverse sources

**Benefits:**
- ✅ Reduces unnecessary API calls
- ✅ Matches tools to query type
- ✅ Explicit reasoning about tool selection
- ✅ Easy to add new tools

**Implementation:**
```python
class ToolRouter:
    def select_tools(self, query: str, topic_type: str) -> list[str]:
        """
        Select appropriate tools based on query characteristics.
        
        Args:
            query: Research question
            topic_type: "academic", "cutting_edge", "biomedical", "general"
        
        Returns:
            List of tool names to use
        """
        # Use LLM to analyze query and select tools
        prompt = f"""
        Given this research query: "{query}"
        Topic type: {topic_type}
        
        Available tools:
        - arxiv_search_tool: Academic papers (physics, CS, math)
        - semantic_scholar_search_tool: All academic disciplines, AI-ranked
        - europe_pmc_search_tool: Biomedical literature
        - reddit_search_tool: Community discussions, cutting-edge topics
        - tavily_search_tool: General web search
        - wikipedia_search_tool: Encyclopedia summaries
        
        Select 2-4 most appropriate tools. Return as JSON list.
        """
        # LLM returns: ["reddit_search_tool", "semantic_scholar_search_tool", "tavily_search_tool"]
```

---

### **Pattern 2: Hierarchical Tool Organization** 📊

Group tools by category and search hierarchically.

```
Query Type Detection
    ↓
┌─────────────┬──────────────┬─────────────┐
│  Academic   │  Community   │  Biomedical │
├─────────────┼──────────────┼─────────────┤
│ arXiv       │ Reddit       │ Europe PMC  │
│ Semantic    │ HackerNews   │             │
│ Scholar     │              │             │
└─────────────┴──────────────┴─────────────┘
         ↓
    Tavily (fallback)
    Wikipedia (context)
```

**Tool Categories:**

| Category | Tools | Use Cases |
|----------|-------|-----------|
| **Academic** | arXiv, Semantic Scholar | Peer-reviewed research, citations |
| **Community** | Reddit, HackerNews | Cutting-edge, AGI, experimental |
| **Biomedical** | Europe PMC | Medical, biological, pharmaceutical |
| **General** | Tavily, Wikipedia | Background, definitions, news |

**Search Strategy:**
1. Detect query type (academic, cutting-edge, biomedical, general)
2. Search primary category first
3. If insufficient results, expand to related categories
4. Always include Wikipedia for context

---

### **Pattern 3: Parallel Tool Execution with Synthesis** ⚡

Execute multiple tools in parallel, then synthesize results.

```
                    Researcher
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
    [Academic]     [Community]       [Web]
    (parallel)     (parallel)     (parallel)
        ↓               ↓               ↓
    Results A      Results B       Results C
        └───────────────┼───────────────┘
                        ↓
                  Synthesizer
                  (combines & ranks)
                        ↓
                     Writer
```

**Benefits:**
- ⚡ Faster (parallel execution)
- 🎯 Comprehensive (multiple perspectives)
- 📊 Better synthesis (explicit combination step)

**Implementation:**
```python
async def research_with_synthesis(query: str):
    # Execute tools in parallel
    tasks = [
        arxiv_search_tool(query),
        reddit_search_tool(query),
        semantic_scholar_search_tool(query),
        tavily_search_tool(query)
    ]
    results = await asyncio.gather(*tasks)
    
    # Synthesize results
    synthesized = synthesize_sources(results, query)
    return synthesized
```

---

### **Pattern 4: Adaptive Tool Selection** 🧠

Learn which tools work best for different query types over time.

```
Query → Tool Selector → Execute → Evaluate → Update Selector
         (ML model)                (quality)    (feedback)
```

**How it works:**
1. Track which tools provide useful results for each query type
2. Build a simple classifier or use LLM with few-shot examples
3. Continuously improve tool selection based on result quality

**Example Heuristics:**
- "AGI" + "consciousness" → Reddit (0.9), Semantic Scholar (0.7), arXiv (0.3)
- "protein folding" → Europe PMC (0.9), arXiv (0.8), Semantic Scholar (0.7)
- "quantum computing" → arXiv (0.9), Semantic Scholar (0.8), Reddit (0.5)

---

## Recommended Implementation Plan

### **Phase 1: Tool Router (Immediate)** ✅

**Goal:** Intelligent tool selection based on query type

**Changes:**
1. Add `ToolRouter` class to `agents.py`
2. Update `Planner` to classify query type
3. Update `Researcher` to use selected tools only
4. Add tool selection reasoning to output

**Code Location:**
- `src/nexus/agents/research/agents.py` - Add ToolRouter
- `src/nexus/agents/research/pipeline.py` - Integrate router

**Estimated Effort:** 2-3 hours

---

### **Phase 2: Parallel Execution (Next)** ⚡

**Goal:** Faster research through parallel tool calls

**Changes:**
1. Make tool calls async
2. Add `asyncio.gather()` for parallel execution
3. Add timeout handling for slow tools
4. Add result caching to avoid duplicate calls

**Code Location:**
- `src/nexus/agents/research/tools.py` - Make async
- `src/nexus/agents/research/agents.py` - Parallel execution

**Estimated Effort:** 3-4 hours

---

### **Phase 3: Source Synthesis (Future)** 📊

**Goal:** Better combination of diverse sources

**Changes:**
1. Add `Synthesizer` agent between Researcher and Writer
2. Rank sources by relevance and credibility
3. Identify contradictions and consensus
4. Create structured knowledge base

**Code Location:**
- `src/nexus/agents/research/agents.py` - Add Synthesizer
- `src/nexus/agents/research/synthesis.py` - New module

**Estimated Effort:** 4-6 hours

---

## Tool Selection Matrix

| Query Type | Primary Tools | Secondary Tools | Rationale |
|------------|--------------|-----------------|-----------|
| **AGI/AI Safety** | Reddit, Semantic Scholar | Tavily, arXiv | Community discussions + academic papers |
| **Experimental ML** | Reddit, Semantic Scholar | arXiv, Tavily | Cutting-edge + research papers |
| **Biomedical** | Europe PMC, Semantic Scholar | Wikipedia, Tavily | Medical literature + context |
| **Physics/Math** | arXiv, Semantic Scholar | Wikipedia, Tavily | Academic papers + background |
| **Fringe Science** | Reddit, Tavily | Wikipedia | Community + web sources |
| **General Tech** | Tavily, Wikipedia | Semantic Scholar, Reddit | Web + encyclopedia + discussions |

---

## Example: AGI Research Query

**Query:** "Recent developments in AGI consciousness and sentience"

**Current Behavior (No Router):**
```
Researcher calls ALL tools:
- arXiv: ❌ Few results (too academic)
- Tavily: ⚠️ Mixed quality
- Wikipedia: ⚠️ Conservative, outdated
- Europe PMC: ❌ Not relevant
- Reddit: ✅ Rich discussions
- Semantic Scholar: ✅ Recent papers
```
**Result:** 6 API calls, 2 useful sources

**With Tool Router:**
```
Router analyzes query:
- Topic: AGI, consciousness (cutting-edge)
- Type: Speculative, experimental
- Selected tools: Reddit, Semantic Scholar, Tavily

Researcher calls ONLY selected tools:
- Reddit: ✅ r/singularity, r/artificial discussions
- Semantic Scholar: ✅ Recent AI consciousness papers
- Tavily: ✅ News and blog posts
```
**Result:** 3 API calls, 3 useful sources ✨

---

## Metrics to Track

1. **Tool Efficiency**
   - % of tool calls that return useful results
   - Average results per tool per query type

2. **Cost Optimization**
   - API calls per research report
   - Cost per report (with tool selection vs without)

3. **Quality Metrics**
   - Source diversity (academic vs community vs web)
   - Citation count of papers found
   - User satisfaction with results

4. **Performance**
   - Time to complete research (with parallel execution)
   - Cache hit rate

---

## Next Steps

1. **Implement Tool Router** (Phase 1)
   - Start with simple heuristics
   - Add LLM-based selection later

2. **Test with Diverse Queries**
   - AGI topics
   - Biomedical topics
   - Experimental ML topics
   - Fringe science topics

3. **Measure Improvements**
   - Compare tool selection accuracy
   - Measure cost reduction
   - Evaluate result quality

4. **Iterate**
   - Refine tool selection logic
   - Add more tools as needed
   - Improve synthesis quality

---

## Conclusion

The **Tool Router pattern** is the best starting point because it:
- ✅ Solves the immediate problem (too many tools)
- ✅ Easy to implement (2-3 hours)
- ✅ Provides clear benefits (cost, speed, quality)
- ✅ Extensible (can add more sophisticated logic later)

Once the router is working, we can add:
- Parallel execution for speed
- Better synthesis for quality
- Adaptive selection for continuous improvement

This positions Nexus to handle 10+ tools effectively while maintaining high quality and reasonable costs.
