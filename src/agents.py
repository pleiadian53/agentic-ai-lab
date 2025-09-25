from datetime import datetime
from urllib import response
from aisuite import Client
from src.research_tools import (
    arxiv_search_tool,
    tavily_search_tool,
    wikipedia_search_tool,
)

client = Client()

# === Research Agent ===
def research_agent(prompt: str, model: str = "openai:gpt-4.1", return_messages: bool = False):
    print("==================================")
    print("🔍 Research Agent")
    print("==================================")

    full_prompt = f"""
You are a research assistant.

You have access to the following tools:
- `tavily_search_tool`: for general web search (e.g., news, blogs, websites)
- `arxiv_search_tool`: for academic publications **only** in the following domains:
  - Computer Science
  - Mathematics
  - Physics
  - Statistics
  - Quantitative Biology
  - Quantitative Finance
  - Electrical Engineering and Systems Science
  - Economics
- `wikipedia_search_tool`: for background information and encyclopedic definitions

🛠 TOOL USAGE RULES:
1. Decide which tools to use based on the research need.
2. Only use `arxiv_search_tool` for supported domains.
3. Use `tavily_search_tool` for recent/general/news.
4. Use `wikipedia_search_tool` for background/definitions.
5. Never use an unsuitable tool.

---
User request:
{prompt}

Today is {datetime.now().strftime('%Y-%m-%d')}.
""".strip()

    messages = [{"role": "user", "content": full_prompt}]
    tools = [arxiv_search_tool, tavily_search_tool, wikipedia_search_tool]

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_turns=12,
            temperature=0.0,  # Use deterministic output
        )

        content = resp.choices[0].message.content or ""

        # ---- Collect tool calls from intermediate_responses and intermediate_messages
        calls = []

        # A) From intermediate_responses
        for ir in getattr(resp, "intermediate_responses", []) or []:
            try:
                tcs = ir.choices[0].message.tool_calls or []
                for tc in tcs:
                    calls.append((tc.function.name, tc.function.arguments))
            except Exception:
                pass

        # B) From intermediate_messages on the final message
        for msg in getattr(resp.choices[0].message, "intermediate_messages", []) or []:
            # assistant message with tool_calls
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    calls.append((tc.function.name, tc.function.arguments))

        # Dedup while preserving order
        seen = set()
        dedup_calls = []
        for name, args in calls:
            key = (name, args)
            if key not in seen:
                seen.add(key)
                dedup_calls.append((name, args))

        # Pretty print args: JSON->dict if possible
        tool_lines = []
        for name, args in dedup_calls:
            arg_text = str(args)
            try:
                import json as _json
                parsed = _json.loads(args) if isinstance(args, str) else args
                if isinstance(parsed, dict):
                    kv = ", ".join(f"{k}={repr(v)}" for k, v in parsed.items())
                    arg_text = kv
            except Exception:
                # keep raw string if not JSON
                pass
            tool_lines.append(f"- {name}({arg_text})")

        if tool_lines:
            tools_html = "<h2 style='font-size:1.5em; color:#2563eb;'>📎 Tools used</h2>"
            tools_html += "<ul>" + "".join(f"<li>{line}</li>" for line in tool_lines) + "</ul>"
            content += "\n\n" + tools_html


        print("✅ Output:\n", content)
        return content, messages

    except Exception as e:
        print("❌ Error:", e)
        return f"[Model Error: {str(e)}]", messages



def writer_agent(
    prompt: str,
    model: str = "openai:gpt-4.1",
    min_words_total: int = 2400,            # mínimo de palabras para todo el informe
    min_words_per_section: int = 400,       # mínimo por sección
    max_tokens: int = 15000,                 # presupuesto de salida (ajústalo a tu modelo)
    retries: int = 1,                       # reintentos si queda corto
):
    print("==================================")
    print("✍️ Writer Agent")
    print("==================================")

    # 1) Instrucciones de longitud claras y medibles
    system_message = f"""
You are an academic writing agent.

Produce a complete, self-contained FINAL REPORT in Markdown. DO NOT summarize; WRITE THE FULL REPORT.

MANDATORY SECTIONS (each section MUST be at least {min_words_per_section} words):
- Introduction
- Background or Context
- Key Findings
- Discussion
- Conclusion
- References

LENGTH REQUIREMENTS:
- The TOTAL report MUST be at least {min_words_total} words.
- If needed, expand examples, equations, methods, limitations, and implications to meet the length.

CITATION RULES:
- Use numeric inline citations [1], [2], ... linked to the References.
- Every inline citation must have a matching References entry.
- Every item in References must be cited at least once.
- Preserve and merge any incoming references/sources/tools links (keep URLs).

OUTPUT:
- Markdown only.
- At the very end include:

USE THE COMPLIANCE CHECKLIST BUT DON'T ADD IT TO THE FINAL OUTPUT.

**Compliance checklist**
- [ ] Used all provided research
- [ ] Included inline citations
- [ ] Included a References section
- [ ] Preserved input references/sources/tools links
- [ ] Structured sections present
""".strip()

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt},
    ]

    def _call(messages_):
        resp = client.chat.completions.create(
            model=model,
            messages=messages_,
            temperature=0,
            max_tokens=max_tokens,            # << IMPORTANTE: darle “aire” a la salida
            # top_p=1,                         # opcional
            # presence_penalty=0,              # opcional
            # frequency_penalty=0,             # opcional
        )
        return resp.choices[0].message.content or ""

    def _word_count(md_text: str) -> int:
        import re
        words = re.findall(r"\b\w+\b", md_text)
        return len(words)

    # 2) Primer intento
    content = _call(messages)

    # 3) Verificación de longitud y reintento si hace falta
    tries = 0
    while tries < retries:
        total_words = _word_count(content)
        if total_words >= min_words_total:
            break  # suficiente
        # Si quedó corto, pedimos explícitamente expandir
        expand_msg = f"""
Your previous answer was too short ({total_words} words).
You MUST expand each section to at least {min_words_per_section} words and the TOTAL to at least {min_words_total} words.
Add more detail, examples, methodology, limitations, and implications. Keep all citations rules.
Only return the full expanded Markdown report (no explanations).
""".strip()
        messages.append({"role": "system", "content": expand_msg})
        content = _call(messages)
        tries += 1

    print("✅ Output:\n", content)
    return content, messages


def editor_agent(
    prompt: str,
    model: str = "openai:gpt-4.1",
    target_min_words: int = 2400,
):
    print("==================================")
    print("🧠 Editor Agent")
    print("==================================")

    system_message = f"""
You are an editor of academic writing.

Revise for clarity, flow, and structure WITHOUT reducing length.
If the text is below {target_min_words} words, EXPAND with clarifying detail, equations, examples, and transitions.
Preserve citations [1], [2], ... and the References section.
Return only the revised Markdown.
""".strip()

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt},
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        max_tokens=4000,   # dale aire aquí también
    )

    content = response.choices[0].message.content
    print("✅ Output:\n", content)
    return content, messages
