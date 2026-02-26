#!/usr/bin/env python
"""
End-to-end test script for C1M4_Ungraded_Lab_2.ipynb (Prompt Engineering)
Tests: text classification, parameter-based generation, and structured JSON output.
"""
import sys
import os
import traceback

# ---------------------------------------------------------------------------
# Load .env from project root so TOGETHER_API_KEY is available
# ---------------------------------------------------------------------------
def load_dotenv(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

load_dotenv(os.path.join(os.path.dirname(__file__), "../../../../.env"))

# Change to notebook directory so utils.py can be imported
os.chdir(os.path.dirname(os.path.abspath(__file__)))

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
# Cell 2: Import from utils
# ---------------------------------------------------------------------------
log_step("Cell 2: Import utils functions")
try:
    from utils import (
        generate_with_single_input,
        generate_with_multiple_input,
        generate_params_dict,
    )
    log_ok("utils imports succeeded (generate_with_single_input, generate_with_multiple_input, generate_params_dict)")
except Exception as e:
    log_error("Cell 2: utils import", e)
    print("\nFATAL: Cannot continue without utils. Exiting.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Cell 2b: Check TOGETHER_API_KEY is available
# ---------------------------------------------------------------------------
log_step("Pre-check: TOGETHER_API_KEY")
try:
    key = os.environ.get("TOGETHER_API_KEY", "")
    assert key, "TOGETHER_API_KEY is not set"
    log_ok(f"TOGETHER_API_KEY present (ends ...{key[-6:]})")
except Exception as e:
    log_error("Pre-check: TOGETHER_API_KEY", e)
    print("\nFATAL: API key required. Exiting.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Section 1 — Text Classification
# ---------------------------------------------------------------------------

# Cell 4: Define check_if_outfit_or_supplement
log_step("Cell 4: Define check_if_outfit_or_supplement")
try:
    def check_if_outfit_or_supplement(query):
        prompt = f"""
Determine the category of the following query as either "nutritional" or "outfit" related.
- Nutritional queries: These are related to nutrition products, such as whey protein, vitamins, supplements, dietary products, and health-related food and beverages.
  - Outfit queries: These pertain to clothing and fashion, including items like shirts, dresses, shoes, accessories, and jewelry.
Examples:

1. Query: "Where can I buy high-protein snacks?" Expected answer: Nutritional
2. Query: "Best shirt styles for summer 2023" Expected answer: Outfit
3. Query: "Are there any shoes designed for running?" Expected answer: Outfit
4. Query: "What multivitamins should I take daily?" Expected answer: Nutritional
5. Query: "Best weight loss products that are stylish" Expected answer: Nutritional
6. Query: "Athletic wear that boosts performance" Expected answer: Outfit 

Query: {query}

Instructions: Respond with "Nutritional" if the query pertains to nutritional products or "Outfit" if it pertains to clothing or fashion products.
Answer only one single word.
"""
        return prompt
    log_ok("check_if_outfit_or_supplement defined")
except Exception as e:
    log_error("Cell 4: define check_if_outfit_or_supplement", e)

# Cell 5: Single query classification (LLM call)
log_step("Cell 5: Single query classification via LLM")
try:
    query = "Give me the available vitamins supplement you have in your catalogue."
    result = generate_with_single_input(check_if_outfit_or_supplement(query), max_tokens=2)
    assert "content" in result, f"Unexpected response structure: {result}"
    log_ok(f"Classification result: '{result['content']}'")
except Exception as e:
    log_error("Cell 5: single query classification", e)

# Cell 7: Batch classification loop (test 3 of 9 queries to stay fast)
log_step("Cell 7: Batch classification (3-query sample)")
try:
    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"

    queries_sample = [
        {"query": "Where can I buy whey protein?", "label": "Nutritional"},
        {"query": "Latest fashion for women's dresses", "label": "Outfit"},
        {"query": "Low-carb diet food options", "label": "Nutritional"},
    ]
    passed = 0
    for item in queries_sample:
        prompt = check_if_outfit_or_supplement(item["query"])
        response = generate_with_single_input(prompt, max_tokens=2)
        result = response["content"]
        color = GREEN if result == item["label"] else RED
        print(f"  Query: {item['query']}\n  Result: {result}  Expected: {color}{item['label']}{RESET}\n")
        if result == item["label"]:
            passed += 1
    log_ok(f"{passed}/{len(queries_sample)} queries classified correctly")
except Exception as e:
    log_error("Cell 7: batch classification", e)

# ---------------------------------------------------------------------------
# Section 2 — Parameter Setting Based on Tasks
# ---------------------------------------------------------------------------

# Cell 9: Define decide_if_technical_or_creative
log_step("Cell 9: Define decide_if_technical_or_creative")
try:
    def decide_if_technical_or_creative(query):
        PROMPT = f"""Decide if the following query is a creative query or a technical query.
    Creative queries ask you to create content, while technical queries are related to documentation or technical requests, like information about procedures.
    Answer only 'creative' or 'technical'.
    Query: {query}
    """
        result = generate_with_single_input(PROMPT)
        label = result["content"]
        return label
    log_ok("decide_if_technical_or_creative defined")
except Exception as e:
    log_error("Cell 9: define decide_if_technical_or_creative", e)

# Cell 10: Test decide_if_technical_or_creative on 2 queries
log_step("Cell 10: Label two queries (technical vs creative)")
try:
    test_queries = ["What is Pi-hole?", "Suggest to me three places to visit in South America"]
    for q in test_queries:
        label = decide_if_technical_or_creative(q)
        log_ok(f"'{q}' → {label}")
except Exception as e:
    log_error("Cell 10: decide_if_technical_or_creative", e)

# Cell 11: Define answer_query
log_step("Cell 11: Define answer_query")
try:
    def answer_query(query):
        label = decide_if_technical_or_creative(query).lower()
        if label == "technical":
            kwargs = generate_params_dict(query, temperature=0, top_p=0.1)
        elif label == "creative":
            kwargs = generate_params_dict(query, temperature=1.1, top_p=0.4)
        else:
            kwargs = generate_params_dict(query, temperature=0.5, top_p=0.5)
        response = generate_with_single_input(**kwargs)
        return response["content"]
    log_ok("answer_query defined")
except Exception as e:
    log_error("Cell 11: define answer_query", e)

# Cell 12: Test answer_query on 2 queries
log_step("Cell 12: answer_query end-to-end")
try:
    for q in ["What is Pi-hole?", "Suggest to me three places to visit in South America"]:
        result = answer_query(q)
        assert result and len(result) > 5, "Empty or very short response"
        log_ok(f"'{q}' → response length {len(result)} chars")
except Exception as e:
    log_error("Cell 12: answer_query", e)

# ---------------------------------------------------------------------------
# Section 3 — Structured JSON Output
# ---------------------------------------------------------------------------

# Cell 14: Define generate_system_call
log_step("Cell 14: Define generate_system_call")
try:
    def generate_system_call(command):
        PROMPT = f"""
You are an assistant program that converts natural language commands into structured JSON for controlling smart home devices. The JSON should conform to a specific format describing the device, action, and parameters. Here's how you can do it:

**Available Devices and Actions:**

1. **Light**
   - Actions: "turn on", "turn off"
   - Parameters: color, intensity (percentage)

2. **Automatic Lock**
   - Actions: "lock", "unlock"
   - Parameters: None

3. **Sound System (Speaker)**
   - Actions: "play", "pause", "stop", "set volume"
   - Parameters: volume (integer), track (string), playlist_style (string)

4. **TV**
   - Actions: "turn on", "turn off", "change channel", "adjust volume"
   - Parameters: channel (string), volume (integer)

5. **Air Conditioner**
   - Actions: "turn on", "turn off", "set temperature", "adjust fan speed"
   - Parameters: temperature (integer), fan_speed (low/medium/high)

**Rooms and Devices:**
- **Office**
  - Lights: "office_light_1" (ID: 123), "office_light_2" (ID: 321)
  - Automatic Lock: "office_door_lock" (ID: 111)

- **Living Room**
  - Light: "living_room_light" (ID: 222)
  - Speaker: "living_room_speaker" (ID: 223)
  - Air Conditioner: "living_room_airconditioner" (ID: 556)

- **Kitchen**
  - Light: "kitchen_light" (ID: 333)

- **Bedroom**
  - Light: "bedroom_light" (ID: 444)
  - TV: "bedroom_tv" (ID: 445)

- **Bathroom**
  - Light: "bathroom_light" (ID: 555)

**Task:**
Convert the following natural language command into the structured JSON format based on the available devices:

**Input Examples:**

1. "Turn on the office light with ID 123 with blue color and 50% intensity."
   - JSON:
     [
     {{
       "room": "office",
       "object_id": "123",
       "object_name": "office_light_1",
       "action": "turn on",
       "parameters": {{"color": "blue", "intensity": "50%"}}
     }}
     ]

2. "Lock the office door."
   - JSON:
   [
     {{
       "room": "office",
       "object_id": "111",
       "object_name": "office_door_lock",
       "action": "lock",
       "parameters": {{}}
     }}
    ]

2. "Make my living room a cheerful place"
   - JSON:
   [
     {{
       "room": "living_room",
       "object_id": "222",
       "object_name": "living_room_light",
       "action": "turn on",
       "parameters": {{'intensity': '80%', 'color':'yellow'}}
     }},
     {{
       "room": "living_room",
       "object_id": "223",
       "object_name": "living_room_speaker",
       "action": "turn on",
       "parameters": {{'volume': '100', 'playlist_style':'party'}}
     }},
     
   ]

**Note:**
- Ensure that each JSON object correctly maps the natural command to the appropriate device and action using the listed device ID.
- Use the object ID to differentiate between devices when the room contains multiple similar items.
- You can add more than one parameter in the parameters dictionary.

Using this information, translate the following command into JSON: "{command}". Output a list with all the necessary JSONs. 
Always output a list even if there is only one command to be applied, do not output anything else but the desired structure.
"""
        kwargs = generate_params_dict(PROMPT, temperature=0.4, top_p=0.1)
        result = generate_with_single_input(**kwargs)
        return result["content"]
    log_ok("generate_system_call defined")
except Exception as e:
    log_error("Cell 14: define generate_system_call", e)

# Cell 15: Test generate_system_call
log_step("Cell 15: generate_system_call - play a chill playlist")
try:
    result = generate_system_call("Play a chill playlist very loud")
    assert result and len(result) > 5, "Empty or very short response"
    log_ok(f"Response (first 150 chars): {result[:150]}")
except Exception as e:
    log_error("Cell 15: generate_system_call playlist", e)

# Cell 16: Test generate_system_call with complex command
log_step("Cell 16: generate_system_call - cozy living room")
try:
    result = generate_system_call(
        "I'm tired today, please make my living room a very cozy ambient, it is really cold today too."
    )
    assert result and len(result) > 5, "Empty or very short response"
    log_ok(f"Response (first 150 chars): {result[:150]}")
except Exception as e:
    log_error("Cell 16: generate_system_call cozy room", e)

# ---------------------------------------------------------------------------
# Section 3.2 — Pydantic structured output
# ---------------------------------------------------------------------------

# Cell 18: Pydantic model definition
log_step("Cell 18: Pydantic VoiceNote model definition")
try:
    from pydantic import BaseModel, Field
    from typing import List
    import json

    class VoiceNote(BaseModel):
        title: str = Field(description="A title for the voice note")
        summary: str = Field(description="A short one sentence summary of the voice note.")
        actionItems: list[str] = Field(description="A list of action items from the voice note")

    schema = VoiceNote.model_json_schema()
    log_ok(f"VoiceNote schema generated: keys={list(schema.keys())}")
except Exception as e:
    log_error("Cell 18: Pydantic VoiceNote definition", e)
    print("  ⚠ Skipping Cell 19 (depends on VoiceNote)")

# Cell 19: Structured output LLM call
log_step("Cell 19: Structured output via response_format (json_schema)")
try:
    transcript = (
        "Good morning! It's 7:00 AM, and I'm just waking up. Today is going to be a busy day, "
        "so let's get started. First, I need to make a quick breakfast. I think I'll have some "
        "scrambled eggs and toast with a cup of coffee. While I'm cooking, I'll also check my "
        "emails to see if there's anything urgent."
    )

    messages = [
        {"role": "system", "content": "The following is a voice message transcript. Only answer in JSON."},
        {"role": "user", "content": transcript},
    ]

    response_format = {
        "type": "json_schema",
        "schema": VoiceNote.model_json_schema(),
    }

    result = generate_with_multiple_input(messages, response_format=response_format)
    assert "content" in result, f"Unexpected response structure: {result}"
    result_json = json.loads(result["content"])
    assert "title" in result_json, f"Missing 'title' in JSON output: {result_json}"
    assert "summary" in result_json, f"Missing 'summary' in JSON output: {result_json}"
    assert "actionItems" in result_json, f"Missing 'actionItems' in JSON output: {result_json}"
    log_ok(f"Structured output validated: title='{result_json['title']}'")
    log_ok(f"actionItems count: {len(result_json['actionItems'])}")
except Exception as e:
    log_error("Cell 19: structured output via response_format", e)

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
