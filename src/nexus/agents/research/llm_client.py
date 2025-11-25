import json
import openai
from aisuite import Client
from typing import Any, Callable

from . import utils

def call_llm_text(client: Client, model: str, messages: list[dict[str, str]], temperature: float = 1.0) -> str:
    """
    Call LLM for text generation, supporting both Chat and Responses APIs.
    """
    aisuite_model, openai_model = utils.normalize_model_name(model)
    
    # === Path B: Responses API ===
    if utils.is_responses_model(openai_model):
        native_client = openai.OpenAI()
        try:
            # Use input list pattern (Canonical)
            # Note: Responses API handles list of messages as conversation history
            response = native_client.responses.create(
                model=openai_model,
                input=messages,
                temperature=temperature
            )
            
            # Extract text content
            texts = []
            if hasattr(response, 'output'):
                for item in response.output:
                    if hasattr(item, 'content'):
                        if isinstance(item.content, str): texts.append(item.content)
                        elif hasattr(item.content, 'text'): texts.append(item.content.text)
            
            # Fallback if no content in output
            if not texts and hasattr(response, 'output_text'):
                return response.output_text
                
            return "\n".join(texts)
            
        except Exception as e:
            return f"[LLM Error: {e}]"

    # === Path A: Chat API (aisuite) ===
    else:
        try:
            response = client.chat.completions.create(
                model=aisuite_model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[LLM Error: {e}]"


def call_llm_with_tools(
    client: Client, 
    model: str, 
    messages: list[dict[str, str]], 
    aisuite_tools: list[Callable], 
    responses_tool_defs: list[dict],
    tool_mapping: dict[str, Callable]
) -> str | tuple[str, list]:
    """
    Execute an agentic loop with tools, supporting both APIs.
    """
    aisuite_model, openai_model = utils.normalize_model_name(model)
    
    # === Path B: Responses API (Canonical Loop) ===
    if utils.is_responses_model(openai_model):
        print(f"🚀 Using Responses API for {openai_model}")
        native_client = openai.OpenAI()
        
        # Init history with messages
        input_items = list(messages)
        
        # Flatten schemas
        flattened_tools = []
        for td in responses_tool_defs:
            func = td["function"]
            flattened_tools.append({
                "type": "function",
                "name": func["name"],
                "description": func["description"],
                "parameters": func.get("parameters", {})
            })
            
        while True:
            try:
                response = native_client.responses.create(
                    model=openai_model,
                    input=input_items,
                    tools=flattened_tools,
                    tool_choice="auto"
                )
                
                # CRITICAL: Extend history with full output
                if hasattr(response, 'output'):
                    input_items.extend(response.output)
                
                # Check for tool calls
                tool_calls = [i for i in response.output if getattr(i, 'type', None) == 'function_call']
                
                if not tool_calls:
                    # Done, extract text
                    texts = []
                    for item in response.output:
                        if hasattr(item, 'content'):
                            if isinstance(item.content, str): texts.append(item.content)
                            elif hasattr(item.content, 'text'): texts.append(item.content.text)
                    return "\n".join(texts)
                
                # Execute tools
                for tc in tool_calls:
                    name = tc.name
                    args = json.loads(tc.arguments)
                    print(f"📞 Tool Call: {name}")
                    
                    if name in tool_mapping:
                        result = tool_mapping[name](**args)
                    else:
                        result = {"error": f"Unknown tool: {name}"}
                        
                    # Append result
                    input_items.append({
                        "type": "function_call_output",
                        "call_id": tc.call_id,
                        "output": json.dumps(result)
                    })
                    
            except Exception as e:
                return f"[Agent Error: {e}]"

    # === Path A: Chat API (OpenAI native with manual tool handling) ===
    else:
        try:
            # Use OpenAI client directly to avoid aisuite's auto-schema issues
            import openai
            native_client = openai.OpenAI()
            
            # Use our manually-defined schemas
            max_turns = 12
            for turn in range(max_turns):
                response = native_client.chat.completions.create(
                    model=openai_model,
                    messages=messages,
                    tools=responses_tool_defs,
                    tool_choice="auto"
                )
                
                message = response.choices[0].message
                
                # If no tool calls, we're done
                if not message.tool_calls:
                    return message.content
                
                # Add assistant message to history
                messages.append(message)
                
                # Execute tool calls
                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    
                    print(f"📞 Tool Call: {func_name}")
                    
                    if func_name in tool_mapping:
                        result = tool_mapping[func_name](**args)
                    else:
                        result = {"error": f"Unknown tool: {func_name}"}
                    
                    # Add tool response to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
            
            return message.content if message.content else "[Max turns reached]"
            
        except Exception as e:
            return f"[Agent Error: {e}]"
