"""Agent implementations for market research pipeline.

This module defines four specialized agents that work in sequence:
1. Market Research Agent - Analyzes trends and matches products
2. Graphic Designer Agent - Generates campaign visuals
3. Copywriter Agent - Creates marketing copy with multimodal input
4. Packaging Agent - Assembles executive reports
"""

import base64
import json
import os
import re
from datetime import datetime
from io import BytesIO
from typing import Any

import aisuite
import openai
import requests
from PIL import Image

from . import tools
from .llm_client import call_llm_json, call_llm_text, _normalize_model_name, _uses_responses_api


def market_research_agent(
    client: aisuite.Client,
    model: str = "gpt-4o-mini",
    return_messages: bool = False,
    verbose: bool = True
) -> str | tuple[str, list[dict]]:
    """Market Research Agent: Scan trends and match products.
    
    Uses two tools:
    1. tavily_search_tool: Search for external trends
    2. product_catalog_tool: Search internal database
    
    Supports both standard Chat API (via aisuite) and new Responses API
    (native OpenAI call) for GPT-5 models.
    
    Args:
        client: aisuite Client instance
        model: Model to use (default: gpt-4o-mini)
        return_messages: If True, return (content, messages) tuple
        verbose: If True, print progress updates
        
    Returns:
        Summary of trends and product matches
    """
    if verbose:
        print("\n🕵️‍♂️ Market Research Agent")
        print("=" * 60)
    
    prompt = f"""
You are a fashion market research agent tasked with preparing a trend analysis for a summer sunglasses campaign.

Your goal:
1. Explore current fashion trends related to sunglasses using web search.
2. Review the internal product catalog to identify items that align with those trends.
3. Recommend one or more products from the catalog that best match emerging trends.

IMPORTANT: You MUST use the 'tavily_search_tool' and 'product_catalog_tool' to find real data. Do not hallucinate trends or products.
"""
    
    # Normalize model name
    aisuite_model, openai_model = _normalize_model_name(model)
    
    messages = [{"role": "user", "content": prompt}]
    tools_list = tools.get_available_tools()
    
    # Check if we need to use responses API (GPT-5 models)
    use_responses_api = _uses_responses_api(openai_model)

    if use_responses_api:
        # Use OpenAI responses API directly with native tool support
        openai_client = openai.OpenAI()
        
        # Convert messages to initial input items (conversation state)
        input_items = list(messages)
        
        # Convert tools to responses API format
        responses_tools = []
        for tool_def in tools_list:
            func = tool_def["function"]
            # Responses API uses a flattened schema where name/description/parameters 
            # are at the top level, not nested under 'function'
            responses_tools.append({
                "type": "function",
                "name": func["name"],
                "description": func["description"],
                "parameters": func.get("parameters", {})
            })
        
        while True:
            try:
                # Responses API supports tools parameter with simpler format
                response = openai_client.responses.create(
                    model=openai_model,
                    input=input_items,
                    tools=responses_tools,  # Simplified tool format
                    tool_choice="auto", # Encourage tool usage
                )
                
                # 1. Add the FULL model response to conversation history
                # This is critical: it preserves 'reasoning' items that paired with 'function_call' items
                if hasattr(response, 'output'):
                    input_items.extend(response.output)

                # Check response output for tool calls (Responses API structure)
                tool_calls_found = []
                if hasattr(response, 'output'):
                    for item in response.output:
                        if hasattr(item, 'type') and item.type == 'function_call':
                            tool_calls_found.append(item)

                if tool_calls_found:
                    # Handle native tool calls from responses API
                    for tool_call in tool_calls_found:
                        tool_name = tool_call.name
                        tool_args = json.loads(tool_call.arguments)
                        
                        if verbose:
                            print(f"\n📞 Tool Call: {tool_name}")
                            print(f"   Arguments: {json.dumps(tool_args)}")
                        
                        # Execute tool
                        if tool_name == "tavily_search_tool":
                            result = tools.tavily_search_tool(**tool_args)
                        elif tool_name == "product_catalog_tool":
                            result = tools.product_catalog_tool(**tool_args)
                        else:
                            result = {"error": f"Unknown tool: {tool_name}"}
                        
                        if verbose:
                            print(f"   ✅ Result: {str(result)[:200]}...")
                        
                        # 2. Add the result as a function_call_output item
                        # Note: The function_call itself was already added via input_items.extend(response.output)
                        input_items.append({
                            "type": "function_call_output",
                            "call_id": tool_call.call_id,
                            "output": json.dumps(result)
                        })
                    
                    # Loop back to model with updated history
                    continue
                
                # Extract final response text
                response_text = getattr(response, "output_text", None)
                if response_text is None:
                    try:
                        # Iterate to find text content if multiple items exist
                        texts = []
                        if hasattr(response, 'output'):
                            for item in response.output:
                                if hasattr(item, 'content') and item.content:
                                    # Content might be string or object with text
                                    if isinstance(item.content, str):
                                        texts.append(item.content)
                                    elif hasattr(item.content, 'text'):
                                        texts.append(item.content.text)
                        
                        response_text = "\n".join(texts) if texts else str(response)
                    except Exception:
                        response_text = str(response)
                
                # Final answer
                if verbose:
                    print(f"\n✅ Analysis complete\n")
                    print(response_text)
                
                return (response_text, messages) if return_messages else response_text
                
            except Exception as e:
                error_msg = f"[⚠️ Error with responses API: {e}]"
                if verbose:
                    print(f"\n{error_msg}")
                return (error_msg, messages) if return_messages else error_msg
    
    else:
        # Use aisuite chat API (GPT-4 models)
        while True:
            response = client.chat.completions.create(
                model=aisuite_model,
                messages=messages,
                tools=tools_list,
                tool_choice="auto"
            )

            msg = response.choices[0].message

            if msg.content:
                if verbose:
                    print(f"\n✅ Analysis complete\n")
                    print(msg.content)
                return (msg.content, messages) if return_messages else msg.content

            if msg.tool_calls:
                for tool_call in msg.tool_calls:
                    if verbose:
                        print(f"\n📞 Tool Call: {tool_call.function.name}")
                        print(f"   Arguments: {tool_call.function.arguments}")
                    
                    result = tools.handle_tool_call(tool_call)
                    
                    if verbose:
                        print(f"   ✅ Result: {str(result)[:200]}...")

                    messages.append(msg)
                    messages.append(tools.create_tool_response_message(tool_call, result))
            else:
                warning = "[⚠️ Unexpected: No tool_calls or content returned]"
                if verbose:
                    print(f"\n{warning}")
                return (warning, messages) if return_messages else warning


def graphic_designer_agent(
    client: aisuite.Client,
    trend_insights: str,
    caption_style: str = "short punchy",
    size: str = "1024x1024",
    model: str = "gpt-4o-mini",
    output_dir: str | None = None,
    verbose: bool = True
) -> dict[str, Any]:
    """Graphic Designer Agent: Generate campaign visuals.
    
    Creates a visual concept based on trend insights using:
    1. LLM to generate prompt and caption
    2. DALL-E 3 to generate the image
    
    Args:
        client: aisuite Client instance
        trend_insights: Trend summary from market research agent
        caption_style: Style hint for caption generation
        size: Image resolution (e.g., '1024x1024')
        model: Model to use for prompt/caption generation
        verbose: If True, print progress updates
        
    Returns:
        Dict with image_url, prompt, caption, and image_path
    """
    if verbose:
        print("\n🎨 Graphic Designer Agent")
        print("=" * 60)

    # Step 1: Generate prompt and caption using aisuite
    system_message = (
        "You are a visual marketing assistant. Based on the input trend insights, "
        "write a creative and visual prompt for an AI image generation model, and also a short caption."
    )

    user_prompt = f"""
Trend insights:
{trend_insights}

Please output:
1. A vivid, descriptive prompt to guide image generation.
2. A marketing caption in style: {caption_style}.

Respond in JSON format with this structure:
{{"prompt": "...", "caption": "..."}}
"""

    # Use call_llm_json which supports both chat and responses API
    parsed = call_llm_json(
        client=client,
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )

    prompt = parsed.get("prompt", "")
    caption = parsed.get("caption", "")

    if verbose:
        print(f"\n📝 Generated Prompt: {prompt}")
        print(f"💬 Generated Caption: {caption}")

    # Step 2: Generate image directly using openai-python
    openai_client = openai.OpenAI()

    if verbose:
        print(f"\n🖼️  Generating image with DALL-E 3...")

    image_response = openai_client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality="standard",
        n=1,
        response_format="url"
    )

    image_url = image_response.data[0].url

    # Save image locally
    img_bytes = requests.get(image_url).content
    img = Image.open(BytesIO(img_bytes))

    filename = os.path.basename(image_url.split("?")[0])
    
    # Save to output_dir if provided, otherwise current directory
    if output_dir:
        from pathlib import Path
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        image_path = str(output_path / filename)
    else:
        image_path = filename
    
    img.save(image_path)

    if verbose:
        print(f"✅ Image saved: {image_path}")

    return {
        "image_url": image_url,
        "prompt": prompt,
        "caption": caption,
        "image_path": image_path
    }


def copywriter_agent(
    client: aisuite.Client,
    image_path: str,
    trend_summary: str,
    model: str = "gpt-4o-mini",
    verbose: bool = True
) -> dict[str, Any]:
    """Copywriter Agent: Create marketing copy with multimodal analysis.
    
    Analyzes the campaign image and trend summary to generate a
    short, elegant marketing quote with justification.
    
    Args:
        client: aisuite Client instance
        image_path: Path to campaign image
        trend_summary: Trend analysis from market research agent
        model: Model to use (must support vision)
        verbose: If True, print progress updates
        
    Returns:
        Dict with quote, justification, and image_path
    """
    if verbose:
        print("\n✍️  Copywriter Agent")
        print("=" * 60)

    # Step 1: Load local image and encode as base64
    with open(image_path, "rb") as f:
        img_bytes = f.read()

    b64_img = base64.b64encode(img_bytes).decode("utf-8")

    # Step 2: Build OpenAI-compliant multimodal message
    messages = [
        {
            "role": "system",
            "content": "You are a copywriter that creates elegant campaign quotes based on an image and a marketing trend summary."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{b64_img}",
                        "detail": "auto"
                    }
                },
                {
                    "type": "text",
                    "text": f"""
Here is a visual marketing image and a trend analysis:

Trend summary:
\"\"\"{trend_summary}\"\"\"

Please return a JSON object like:
{{
  "quote": "A short, elegant campaign phrase (max 12 words)",
  "justification": "Why this quote matches the image and trend"
}}"""
                }
            ]
        }
    ]

    # Step 3: Send request using call_llm_json (supports both chat and responses API)
    if verbose:
        print(f"\n📤 Sending multimodal request to {model}...")
    
    parsed = call_llm_json(
        client=client,
        model=model,
        messages=messages,
        temperature=0.3
    )
    
    if verbose:
        print(f"\n✅ Response received")

    if verbose and "quote" in parsed:
        print(f"\n💬 Quote: {parsed['quote']}")
        print(f"📋 Justification: {parsed['justification']}")

    parsed["image_path"] = image_path
    return parsed


def packaging_agent(
    client: aisuite.Client,
    trend_summary: str,
    image_url: str,
    quote: str,
    justification: str,
    output_path: str = "campaign_summary.md",
    model: str = "gpt-4o-mini",
    verbose: bool = True
) -> str:
    """Packaging Agent: Assemble executive-ready report.
    
    Combines all campaign assets into a polished markdown report
    with refined trend summary and formatted visuals.
    
    Args:
        client: aisuite Client instance
        trend_summary: Market research summary
        image_url: Path to campaign image
        quote: Marketing quote
        justification: Quote justification
        output_path: Path to save markdown report
        model: Model to use for summary refinement
        verbose: If True, print progress updates
        
    Returns:
        Path to saved markdown file
    """
    if verbose:
        print("\n📦 Packaging Agent")
        print("=" * 60)

    # Refine trend summary for executive audience using call_llm_text
    beautified_summary = call_llm_text(
        client=client,
        model=model,
        messages=[
            {"role": "system", "content": "You are a marketing communication expert writing elegant campaign summaries for executives."},
            {"role": "user", "content": f"""
Please rewrite the following trend summary to be clear, professional, and engaging for a CEO audience:

\"\"\"{trend_summary.strip()}\"\"\"
"""}
        ],
        temperature=0.3
    )

    if verbose:
        print(f"\n✅ Trend summary refined for executive audience")

    # Combine all parts into markdown
    styled_image_html = f"![Campaign Visual]({image_url})"

    markdown_content = f"""# 🕶️ Summer Sunglasses Campaign – Executive Summary

## 📊 Refined Trend Insights
{beautified_summary}

## 🎯 Campaign Visual
{styled_image_html}

## ✍️ Campaign Quote
{quote.strip()}

## ✅ Why This Works
{justification.strip()}

---

*Report generated on {datetime.now().strftime('%Y-%m-%d')}*
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    if verbose:
        print(f"✅ Report saved: {output_path}")

    return output_path
