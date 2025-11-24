# Nexus Research System Architecture

**Visual guide to the Nexus superintelligent research system**

---

## 🏗️ System Overview

```mermaid
graph TB
    subgraph "🎯 Nexus Research System"
        subgraph "User Interfaces"
            CLI[🖥️ CLI Interface<br/>nexus-research]
            WEB[🌐 Web Interface<br/>localhost:8004]
        end
        
        subgraph "Core Pipeline"
            PLANNER[📋 Planner Agent<br/>Research strategy]
            RESEARCHER[🔍 Researcher Agent<br/>Knowledge gathering]
            WRITER[✍️ Writer Agent<br/>Content generation]
            EDITOR[📝 Editor Agent<br/>Quality refinement]
        end
        
        subgraph "Intelligence Layer"
            FORMAT[🎨 Format Decision<br/>LaTeX/Markdown/PDF]
            MANIFEST[📊 Manifest Tracker<br/>Metadata & versions]
            SLUG[🏷️ Smart Slugs<br/>Topic organization]
        end
        
        subgraph "Output Generation"
            LATEX[📄 LaTeX Engine<br/>XeLaTeX compilation]
            PDF[📕 PDF Generator<br/>Publication quality]
            MD[📝 Markdown<br/>Web-friendly]
        end
    end
    
    subgraph "🤝 Supporting Agents"
        CHART[📊 Chart Agent<br/>Visualizations]
        SQL[🗄️ SQL Agent<br/>Data queries]
        SPLICE[🧬 Splice Agent<br/>Genomics]
    end
    
    subgraph "🔧 Knowledge Sources"
        TAVILY[🌐 Tavily<br/>Web search]
        ARXIV[📚 arXiv<br/>Preprints]
        PUBMED[🏥 PubMed<br/>Biomedical]
        EUROPEPMC[🔬 Europe PMC<br/>Life sciences]
        WIKI[📖 Wikipedia<br/>General knowledge]
    end
    
    subgraph "💾 Storage"
        REPORTS[📁 Research Reports<br/>output/research_reports/]
        PAPERS[📄 Example Papers<br/>data/papers/]
    end
    
    CLI --> PLANNER
    WEB --> PLANNER
    
    PLANNER --> RESEARCHER
    RESEARCHER --> WRITER
    WRITER --> EDITOR
    
    PLANNER -.-> FORMAT
    PLANNER -.-> MANIFEST
    PLANNER -.-> SLUG
    
    RESEARCHER --> TAVILY
    RESEARCHER --> ARXIV
    RESEARCHER --> PUBMED
    RESEARCHER --> EUROPEPMC
    RESEARCHER --> WIKI
    
    WRITER --> FORMAT
    EDITOR --> FORMAT
    
    FORMAT --> LATEX
    FORMAT --> MD
    LATEX --> PDF
    
    PDF --> REPORTS
    MD --> REPORTS
    
    MANIFEST --> REPORTS
    
    CHART -.-> WRITER
    SQL -.-> RESEARCHER
    SPLICE -.-> RESEARCHER
    
    PAPERS -.-> WRITER
    
    style CLI fill:#e1f5ff
    style WEB fill:#e1f5ff
    style PLANNER fill:#fff4e1
    style RESEARCHER fill:#fff4e1
    style WRITER fill:#fff4e1
    style EDITOR fill:#fff4e1
    style FORMAT fill:#f0e1ff
    style LATEX fill:#e1ffe1
    style PDF fill:#e1ffe1
    style CHART fill:#ffe1f0
    style SQL fill:#ffe1f0
    style SPLICE fill:#ffe1f0
```

---

## 🔄 Research Workflow

```mermaid
sequenceDiagram
    participant User
    participant CLI/Web
    participant Planner
    participant Researcher
    participant Writer
    participant Editor
    participant Format
    participant LaTeX
    participant Output
    
    User->>CLI/Web: Submit topic
    CLI/Web->>Planner: Initialize research
    
    Note over Planner: Analyze topic<br/>Create research plan<br/>Decide format
    
    Planner->>Format: Determine output format
    Format-->>Planner: LaTeX (equations needed)
    
    Planner->>Researcher: Execute research plan
    
    loop Knowledge Gathering
        Researcher->>Tavily/arXiv: Search papers
        Tavily/arXiv-->>Researcher: Results
        Note over Researcher: Synthesize findings
    end
    
    Researcher->>Writer: Provide research data
    
    Note over Writer: Generate content<br/>Include equations<br/>Follow format rules
    
    Writer->>Editor: Draft report
    
    Note over Editor: Refine content<br/>Verify equations<br/>Check quality
    
    Editor->>Format: Finalized content
    
    alt LaTeX Format
        Format->>LaTeX: Compile with XeLaTeX
        LaTeX->>Output: Generate PDF
    else Markdown Format
        Format->>Output: Save Markdown
    end
    
    Output->>User: Deliver report
```

---

## 🧩 Multi-Agent Collaboration

```mermaid
graph LR
    subgraph "Agent Roles"
        P[📋 Planner<br/>Strategy & Coordination]
        R[🔍 Researcher<br/>Knowledge Discovery]
        W[✍️ Writer<br/>Content Creation]
        E[📝 Editor<br/>Quality Assurance]
    end
    
    subgraph "Shared Context"
        TOPIC[📌 Research Topic]
        PLAN[📝 Research Plan]
        DATA[📊 Research Data]
        DRAFT[📄 Draft Report]
        FINAL[✅ Final Report]
    end
    
    P -->|Creates| PLAN
    TOPIC -->|Informs| P
    
    PLAN -->|Guides| R
    R -->|Produces| DATA
    
    DATA -->|Feeds| W
    PLAN -->|Constrains| W
    W -->|Generates| DRAFT
    
    DRAFT -->|Reviews| E
    PLAN -->|Validates| E
    E -->|Refines| FINAL
    
    style P fill:#fff4e1
    style R fill:#e1f5ff
    style W fill:#f0e1ff
    style E fill:#e1ffe1
```

---

## 🎨 Format Decision Intelligence

```mermaid
flowchart TD
    START([Topic Submitted])
    ANALYZE{Analyze Topic}
    
    MATH{Contains<br/>Math/Equations?}
    COMPLEX{Complex<br/>Formatting?}
    
    LATEX[📄 LaTeX Format<br/>+ Equations<br/>+ Professional PDF]
    MARKDOWN[📝 Markdown Format<br/>+ Web-friendly<br/>+ Simple layout]
    PDF_DIRECT[📕 Direct PDF<br/>+ Quick generation<br/>+ Basic formatting]
    
    START --> ANALYZE
    ANALYZE --> MATH
    
    MATH -->|Yes| LATEX
    MATH -->|No| COMPLEX
    
    COMPLEX -->|Yes| LATEX
    COMPLEX -->|No| MARKDOWN
    
    LATEX --> COMPILE[XeLaTeX Compilation]
    MARKDOWN --> SAVE[Save Markdown]
    PDF_DIRECT --> GENERATE[Generate PDF]
    
    COMPILE --> OUTPUT[📁 Output]
    SAVE --> OUTPUT
    GENERATE --> OUTPUT
    
    style LATEX fill:#e1ffe1
    style MARKDOWN fill:#e1f5ff
    style PDF_DIRECT fill:#fff4e1
    style OUTPUT fill:#ffe1f0
```

---

## 🔌 Tool Integration

```mermaid
graph TB
    subgraph "Research Agent"
        RA[🔍 Researcher Agent]
    end
    
    subgraph "Academic Sources"
        ARXIV[📚 arXiv API<br/>Preprints & papers]
        PUBMED[🏥 PubMed API<br/>Biomedical research]
        EUROPEPMC[🔬 Europe PMC API<br/>Life sciences]
    end
    
    subgraph "Web Sources"
        TAVILY[🌐 Tavily API<br/>Web search]
        WIKI[📖 Wikipedia API<br/>General knowledge]
    end
    
    subgraph "Future Tools"
        GITHUB[💻 GitHub API<br/>Code repositories]
        SEMANTIC[🎓 Semantic Scholar<br/>Citation graphs]
        DATASETS[📊 Dataset APIs<br/>Research data]
    end
    
    RA --> ARXIV
    RA --> PUBMED
    RA --> EUROPEPMC
    RA --> TAVILY
    RA --> WIKI
    
    RA -.->|Planned| GITHUB
    RA -.->|Planned| SEMANTIC
    RA -.->|Planned| DATASETS
    
    style RA fill:#fff4e1
    style ARXIV fill:#e1f5ff
    style PUBMED fill:#e1f5ff
    style EUROPEPMC fill:#e1f5ff
    style TAVILY fill:#e1ffe1
    style WIKI fill:#e1ffe1
    style GITHUB fill:#f0e1ff,stroke-dasharray: 5 5
    style SEMANTIC fill:#f0e1ff,stroke-dasharray: 5 5
    style DATASETS fill:#f0e1ff,stroke-dasharray: 5 5
```

---

## 🚀 Future Architecture (Roadmap)

```mermaid
graph TB
    subgraph "Enhanced Nexus"
        NEXUS[🎯 Nexus Core]
        
        subgraph "New Capabilities"
            STYLE[🎨 Style Transfer<br/>Learn from examples]
            P2C[💻 Paper2Code<br/>Implementation generation]
            GITHUB_DISC[🔍 GitHub Discovery<br/>Find implementations]
            UNCERTAINTY[📊 Uncertainty Quantification<br/>Confidence scores]
        end
        
        subgraph "Enhanced UI"
            PROGRESS[⏱️ Real-time Progress<br/>Granular updates]
            COST[💰 Cost Estimation<br/>Before generation]
            INTERACTIVE[🔄 Interactive Refinement<br/>User feedback loop]
        end
        
        subgraph "New Agents"
            EMAIL[📧 Email Agent<br/>Research updates]
            CODE[💻 Code Agent<br/>Generate & test]
            CITE[📚 Citation Agent<br/>Bibliography management]
            EXPERIMENT[🧪 Experiment Agent<br/>Track experiments]
        end
    end
    
    NEXUS --> STYLE
    NEXUS --> P2C
    NEXUS --> GITHUB_DISC
    NEXUS --> UNCERTAINTY
    
    NEXUS --> PROGRESS
    NEXUS --> COST
    NEXUS --> INTERACTIVE
    
    NEXUS -.-> EMAIL
    NEXUS -.-> CODE
    NEXUS -.-> CITE
    NEXUS -.-> EXPERIMENT
    
    style NEXUS fill:#fff4e1
    style STYLE fill:#e1ffe1
    style P2C fill:#e1ffe1
    style GITHUB_DISC fill:#e1ffe1
    style EMAIL fill:#ffe1f0,stroke-dasharray: 5 5
    style CODE fill:#ffe1f0,stroke-dasharray: 5 5
    style CITE fill:#ffe1f0,stroke-dasharray: 5 5
    style EXPERIMENT fill:#ffe1f0,stroke-dasharray: 5 5
```

---

## 📊 Data Flow

```mermaid
flowchart LR
    subgraph "Input"
        TOPIC[📌 Research Topic]
        CONTEXT[📝 Optional Context]
        MODEL[🤖 Model Selection]
        LENGTH[📏 Report Length]
    end
    
    subgraph "Processing"
        PLAN[📋 Research Plan]
        SEARCH[🔍 Knowledge Search]
        SYNTHESIS[🧠 Data Synthesis]
        GENERATION[✍️ Content Generation]
        REFINEMENT[📝 Quality Refinement]
    end
    
    subgraph "Output"
        REPORT[📄 Research Report]
        PDF_OUT[📕 PDF File]
        MANIFEST_OUT[📊 Manifest JSON]
        METADATA[🏷️ Metadata]
    end
    
    TOPIC --> PLAN
    CONTEXT --> PLAN
    MODEL --> PLAN
    LENGTH --> PLAN
    
    PLAN --> SEARCH
    SEARCH --> SYNTHESIS
    SYNTHESIS --> GENERATION
    GENERATION --> REFINEMENT
    
    REFINEMENT --> REPORT
    REPORT --> PDF_OUT
    REPORT --> MANIFEST_OUT
    REPORT --> METADATA
    
    style TOPIC fill:#e1f5ff
    style REPORT fill:#e1ffe1
    style PDF_OUT fill:#e1ffe1
```

---

## 🎓 Design Patterns Illustrated

### Reflection Pattern
```mermaid
graph LR
    A[Generate] --> B[Evaluate]
    B --> C{Good enough?}
    C -->|No| D[Refine]
    D --> A
    C -->|Yes| E[Output]
    
    style A fill:#fff4e1
    style B fill:#e1f5ff
    style D fill:#f0e1ff
    style E fill:#e1ffe1
```

### Tool Use Pattern
```mermaid
graph LR
    A[Agent] --> B{Need Info?}
    B -->|Yes| C[Select Tool]
    C --> D[Execute Tool]
    D --> E[Process Result]
    E --> A
    B -->|No| F[Continue]
    
    style A fill:#fff4e1
    style C fill:#e1f5ff
    style D fill:#f0e1ff
    style E fill:#e1ffe1
```

### Multiagent Pattern
```mermaid
graph TB
    O[Orchestrator] --> A1[Agent 1]
    O --> A2[Agent 2]
    O --> A3[Agent 3]
    A1 --> R[Results]
    A2 --> R
    A3 --> R
    R --> O
    
    style O fill:#fff4e1
    style A1 fill:#e1f5ff
    style A2 fill:#e1f5ff
    style A3 fill:#e1f5ff
    style R fill:#e1ffe1
```

---

## 🔐 Configuration & Security

```mermaid
graph TB
    subgraph "Configuration"
        ENV[🔧 Environment Variables]
        CONFIG[⚙️ NexusConfig]
        PATHS[📁 Path Management]
    end
    
    subgraph "API Keys"
        OPENAI[🔑 OpenAI API]
        ANTHROPIC[🔑 Anthropic API]
        GOOGLE[🔑 Google API]
        TAVILY_KEY[🔑 Tavily API]
    end
    
    subgraph "Security"
        DOTENV[📄 .env File<br/>Not in git]
        SECRETS[🔒 Secret Management]
    end
    
    ENV --> CONFIG
    CONFIG --> PATHS
    
    DOTENV --> OPENAI
    DOTENV --> ANTHROPIC
    DOTENV --> GOOGLE
    DOTENV --> TAVILY_KEY
    
    OPENAI --> SECRETS
    ANTHROPIC --> SECRETS
    GOOGLE --> SECRETS
    TAVILY_KEY --> SECRETS
    
    style DOTENV fill:#ffe1e1
    style SECRETS fill:#ffe1e1
```

---

## 📈 Performance & Scalability

```mermaid
graph TB
    subgraph "Model Selection"
        CHEAP[💰 gpt-4o-mini<br/>Fast & cheap]
        BALANCED[⚖️ gpt-4o<br/>Balanced quality]
        ADVANCED[🚀 gpt-5*<br/>Maximum quality]
    end
    
    subgraph "Optimization"
        CACHE[💾 Response Caching]
        PARALLEL[⚡ Parallel Processing]
        ADAPTIVE[🎯 Adaptive Iteration]
    end
    
    subgraph "Monitoring"
        COST_TRACK[💰 Cost Tracking]
        PERF[⏱️ Performance Metrics]
        QUALITY[✅ Quality Scores]
    end
    
    CHEAP --> CACHE
    BALANCED --> CACHE
    ADVANCED --> CACHE
    
    CACHE --> PARALLEL
    PARALLEL --> ADAPTIVE
    
    ADAPTIVE --> COST_TRACK
    ADAPTIVE --> PERF
    ADAPTIVE --> QUALITY
    
    style CHEAP fill:#e1ffe1
    style BALANCED fill:#fff4e1
    style ADVANCED fill:#ffe1f0
```

---

**Legend:**
- 🎯 Core System
- 🤝 Supporting Agents
- 🔧 External Tools
- 💾 Storage
- 🚀 Future/Planned (dashed lines)
- 🎨 Color coding by function type
