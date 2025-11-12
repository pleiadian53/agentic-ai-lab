"""
Tool Functions for LLM Tool Calling

This module provides a collection of tool functions that can be exposed
to LLMs via AISuite for agentic workflows. Each function includes proper
docstrings that help the LLM understand when and how to use the tool.

Design Principles:
    - Clear, descriptive docstrings for LLM understanding
    - Type hints for parameter validation
    - Minimal external dependencies where possible
    - Graceful error handling with informative messages
"""

from datetime import datetime
from typing import Optional
import requests
import qrcode
from qrcode.image.styledpil import StyledPilImage


def get_current_time() -> str:
    """
    Returns the current time as a string in HH:MM:SS format.
    
    Returns:
        str: Current time formatted as "HH:MM:SS"
    
    Example:
        >>> get_current_time()
        "14:30:45"
    """
    return datetime.now().strftime("%H:%M:%S")


def get_weather_from_ip() -> str:
    """
    Gets the current, high, and low temperature in Fahrenheit for the user's
    location based on their IP address.
    
    This function:
    1. Detects location coordinates from IP address
    2. Fetches weather data from Open-Meteo API
    3. Returns formatted temperature information
    
    Returns:
        str: Formatted string with current, high, and low temperatures
        
    Raises:
        requests.RequestException: If API calls fail
        
    Example:
        >>> get_weather_from_ip()
        "Current: 72.5°F, High: 78.0°F, Low: 65.0°F"
    """
    try:
        # Get location coordinates from the IP address
        location_response = requests.get('https://ipinfo.io/json')
        location_response.raise_for_status()
        lat, lon = location_response.json()['loc'].split(',')

        # Set parameters for the weather API call
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m",
            "daily": "temperature_2m_max,temperature_2m_min",
            "temperature_unit": "fahrenheit",
            "timezone": "auto"
        }

        # Get weather data
        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast", 
            params=params
        )
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        # Format and return the simplified string
        return (
            f"Current: {weather_data['current']['temperature_2m']}°F, "
            f"High: {weather_data['daily']['temperature_2m_max'][0]}°F, "
            f"Low: {weather_data['daily']['temperature_2m_min'][0]}°F"
        )
    except requests.RequestException as e:
        return f"Error fetching weather data: {str(e)}"
    except (KeyError, ValueError) as e:
        return f"Error parsing weather data: {str(e)}"


def write_txt_file(file_path: str, content: str) -> str:
    """
    Write a string into a .txt file (overwrites if exists).
    
    Args:
        file_path (str): Destination path for the file
        content (str): Text content to write to the file
        
    Returns:
        str: Path to the written file
        
    Raises:
        IOError: If file cannot be written
        
    Example:
        >>> write_txt_file("notes.txt", "Remember to call John")
        "notes.txt"
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path
    except IOError as e:
        return f"Error writing file: {str(e)}"


def generate_qr_code(
    data: str, 
    filename: str, 
    image_path: Optional[str] = None
) -> str:
    """
    Generate a QR code image from data, with optional image embedding.
    
    This function creates a QR code that encodes the provided data (typically
    a URL or text). Optionally, an image can be embedded in the center of the
    QR code for branding purposes.
    
    Args:
        data (str): Text or URL to encode in the QR code
        filename (str): Name for the output PNG file (without .png extension)
        image_path (str, optional): Path to an image to embed in the QR code.
            If None, creates a standard QR code without embedded image.
            
    Returns:
        str: Confirmation message with filename and truncated data preview
        
    Raises:
        FileNotFoundError: If image_path is provided but file doesn't exist
        
    Example:
        >>> generate_qr_code("https://example.com", "my_qr", "logo.png")
        "QR code saved as my_qr.png containing: https://example.com..."
    """
    try:
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr.add_data(data)
        
        # Create QR code with or without embedded image
        if image_path:
            img = qr.make_image(
                image_factory=StyledPilImage, 
                embedded_image_path=image_path
            )
        else:
            img = qr.make_image()
            
        output_file = f"{filename}.png"
        img.save(output_file)
        
        # Truncate data preview for readability
        data_preview = data[:50] + "..." if len(data) > 50 else data
        return f"QR code saved as {output_file} containing: {data_preview}"
        
    except FileNotFoundError:
        return f"Error: Image file '{image_path}' not found"
    except Exception as e:
        return f"Error generating QR code: {str(e)}"


# Tool registry for easy access
AVAILABLE_TOOLS = [
    get_current_time,
    get_weather_from_ip,
    write_txt_file,
    generate_qr_code,
]


def get_tool_schemas() -> list[dict]:
    """
    Generate tool schemas for manual tool definition with AISuite.
    
    Returns a list of tool schemas that can be passed directly to the
    AISuite client when you want to manually define tools instead of
    relying on automatic function introspection.
    
    Returns:
        list[dict]: List of tool schema dictionaries
        
    Example:
        >>> schemas = get_tool_schemas()
        >>> # Use with AISuite client
        >>> response = client.chat.completions.create(
        ...     model="openai:gpt-4o",
        ...     messages=messages,
        ...     tools=schemas
        ... )
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "Returns the current time as a string in HH:MM:SS format.",
                "parameters": {}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_weather_from_ip",
                "description": (
                    "Gets the current, high, and low temperature in Fahrenheit "
                    "for the user's location based on their IP address."
                ),
                "parameters": {}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_txt_file",
                "description": "Write a string into a .txt file (overwrites if exists).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Destination path for the file"
                        },
                        "content": {
                            "type": "string",
                            "description": "Text content to write to the file"
                        }
                    },
                    "required": ["file_path", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_qr_code",
                "description": (
                    "Generate a QR code image from data, with optional image embedding. "
                    "Creates a PNG file with the QR code."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "string",
                            "description": "Text or URL to encode in the QR code"
                        },
                        "filename": {
                            "type": "string",
                            "description": "Name for the output PNG file (without extension)"
                        },
                        "image_path": {
                            "type": "string",
                            "description": "Optional path to an image to embed in the QR code"
                        }
                    },
                    "required": ["data", "filename"]
                }
            }
        }
    ]
