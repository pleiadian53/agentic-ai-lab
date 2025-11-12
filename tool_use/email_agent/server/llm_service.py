from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aisuite as ai
import markdown
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import configuration
from config import (
    DEFAULT_MODEL,
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    USER_EMAIL,
)

# Import from shared tool_use package (works with editable install)
from tool_use.display_functions import pretty_print_chat_completion_html

# Import email_tools from parent email_agent package
from email_agent import email_tools

# Initialize AISuite client for LLM interactions
client = ai.Client()

# Create FastAPI application instance with a descriptive title
app = FastAPI(title="LLM Email Prompt Executor")

# Add CORS (Cross-Origin Resource Sharing) middleware for security
# This controls which external domains can access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,           # Which domains can access (e.g., ["http://localhost:3000"])
    allow_credentials=CORS_ALLOW_CREDENTIALS,  # Allow cookies/auth headers
    allow_methods=["*"],                  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],                  # Allow all HTTP headers
)

# Define request schema using Pydantic for automatic validation
# This ensures incoming requests have the correct structure
class PromptInput(BaseModel):
    prompt: str  # The natural language instruction from the user

# Define API endpoint: POST /prompt
# This is where clients send natural language instructions
@app.post("/prompt")
async def handle_prompt(payload: PromptInput):
    """
    Handle natural language prompts and execute email operations via LLM.
    
    Args:
        payload: PromptInput containing the user's natural language instruction
        
    Returns:
        dict: Contains 'response' (markdown) and 'html_response' (formatted HTML)
    """
    prompt = payload.prompt

    # Build system prompt with instructions for the LLM
    # This tells the LLM how to behave and what context it has
    prompt_ = f"""
        - You are an AI assistant specialized in managing emails. 
        - You can perform various actions such as listing, searching, filtering, and manipulating emails. 
        - Use the provided tools to interact with the email system.
        - Never ask the user for confirmation before performing an action.
        - If needed, my email address is "{USER_EMAIL}" so you can use it to send emails or perform actions related to my account.
        {prompt}
        """

    # Call LLM with tool use enabled
    # The LLM will decide which tools to call and in what order
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt_}],
        tools=[
            # Register all available email tools
            # Each function becomes a "tool" the LLM can invoke
            email_tools.list_all_emails,
            email_tools.list_unread_emails,
            email_tools.search_emails,
            email_tools.filter_emails,
            email_tools.get_email,
            email_tools.mark_email_as_read,
            email_tools.mark_email_as_unread,
            email_tools.send_email,
            email_tools.delete_email,
            email_tools.search_unread_from_sender
        ],
        max_turns=20  # Maximum number of tool calls allowed in one request
    )

    # Format the response for display
    html_response = pretty_print_chat_completion_html(response)
    final_text = markdown.markdown(response.choices[0].message.content)

    # Return both plain and HTML formatted responses
    return {
        "response": final_text,
        "html_response": html_response
    }
