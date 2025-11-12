# Word Count Philosophy for Research Agent

## The Problem We Solved

Previously, the research agent would:
1. Generate a comprehensive initial draft (e.g., 1148 words on AGI)
2. Receive feedback to "streamline repetition"
3. Aggressively cut content (down to 830 words)
4. Lose valuable depth and examples

**Root Cause**: The revision prompt emphasized "conciseness" without balancing it with "comprehensiveness."

## Our Solution

### 1. Updated Default Word Counts

**Old Defaults:**
- Min: 500 words
- Max: 2000 words

**New Defaults (Conference Paper Standard):**
- Min: 800 words
- Max: 6000 words

### 2. Revised Prompts to Respect LLM Judgment

**Draft Prompt Changes:**
```
- Target word count: {min_words}-{max_words} words
  * Use your judgment—complex topics deserve comprehensive treatment
  * Provide sufficient depth and examples to thoroughly address the topic
  * Don't artificially pad or restrict length; let the topic guide the scope
```

**Revision Prompt Changes:**
```
- When removing repetition, REPLACE with deeper analysis, concrete examples, 
  or new perspectives—don't just delete.
- Target word count: {min_words}-{max_words} words (use your judgment—complex 
  topics deserve comprehensive treatment).
- Balance conciseness with comprehensiveness—trim only what truly adds no value.
- For technical topics, provide sufficient detail and examples to thoroughly 
  explain concepts.
```

### 3. Philosophy

**We trust the LLM's judgment.** 

- ✅ Complex topics like AGI naturally require 4000-6000+ words
- ✅ Simple topics may only need 1000-2000 words
- ✅ "Streamlining" means reorganizing and deepening, not deleting
- ✅ Quality feedback improves structure, not just reduces length
- ❌ We don't artificially force word counts up or down

## Word Count Guidelines

| Topic Type | Recommended Range | Rationale |
|------------|-------------------|-----------|
| Simple/Practical | 800-1500 words | Recipes, how-tos, straightforward topics |
| Moderate Complexity | 1500-3000 words | Multiple perspectives, some depth needed |
| Complex | 3000-5000 words | Technical details, examples, counterarguments |
| Highly Complex | 4000-6000+ words | Deep technical content, comprehensive coverage |

## Conference Paper Standards

For reference, typical academic paper lengths:

| Paper Type | Word Count | Page Count (double-spaced) |
|------------|------------|---------------------------|
| Short paper | 3,000-4,000 | 4-6 pages |
| Full paper | 5,000-8,000 | 8-12 pages |
| Extended paper | 8,000-12,000 | 12-15 pages |

Our default of **6,000 words** aligns with a **full conference paper**, which is appropriate for comprehensive technical topics.

## Example: AGI Technical Ingredients

**Topic Complexity**: Highly Complex

**Why it needs 4000-6000+ words:**
- 7+ major technical components (reasoning, world model, planning, memory, tool use, multimodality, self-reflection)
- Each component requires:
  - Definition and explanation
  - Technical details
  - Examples and use cases
  - Challenges and current approaches
  - Connections to other components
- Ethical considerations
- Future directions

**Previous Issue**: 
- Draft: 1148 words → Revision: 830 words ❌
- Lost depth on several components

**With New Settings**:
- Draft: ~2500-3500 words → Revision: ~3000-4500 words ✅
- Maintains comprehensive coverage while improving quality

## Usage

### Default (Recommended)
```bash
python scripts/run_reflection_research_agent.py "Your topic"
# Uses 1000-6000 word range
```

### Custom Range
```bash
python scripts/run_reflection_research_agent.py "Your topic" \
    --min-words 2000 \
    --max-words 8000
```

### For Simple Topics
```bash
python scripts/run_reflection_research_agent.py "Benefits of exercise" \
    --min-words 1000 \
    --max-words 2500
```

### For Highly Complex Topics
```bash
python scripts/run_reflection_research_agent.py \
    "Comprehensive analysis of AGI technical requirements" \
    --min-words 4000 \
    --max-words 8000 \
    --max-iterations 3
```

## Key Takeaways

1. **Trust the model**: LLMs are good at judging appropriate depth
2. **Quality over arbitrary limits**: 800 words of fluff < 4000 words of substance
3. **Revision ≠ Reduction**: Improving an essay doesn't mean making it shorter
4. **Topic-driven length**: Let the complexity of the topic guide the scope
5. **Conference paper standard**: 6000 words is a reasonable default for technical topics

## Technical Implementation

All changes are in:
- `reflection/research_agent/config.py`: Default word counts (1000-6000)
- `reflection/research_agent/prompts.py`: Updated draft and revision prompts
- `reflection/research_agent/llm.py`: Word count parameters passed through
- `reflection/research_agent/workflow.py`: Word counts used in revision
- `scripts/run_reflection_research_agent.py`: CLI defaults updated

## Testing

Try the updated system:

```bash
python scripts/run_reflection_research_agent.py \
    "Describe the main technical ingredients needed for AGI systems — such as reasoning, world model, planning, memory, tool use, multimodality, and self-reflection" \
    --generate-pdf \
    --max-iterations 3 \
    --output-dir ./essays/agi_systems \
    --essay-basename agi_comprehensive
```

Expected result: 3000-5000 word comprehensive essay that maintains depth through revisions.
