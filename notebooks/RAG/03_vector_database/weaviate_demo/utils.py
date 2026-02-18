from flask import Flask, request, jsonify
import threading
from sentence_transformers import SentenceTransformer
import json
import requests
from typing import Union
import os
from contextlib import redirect_stdout, redirect_stderr
import logging
from typing import Dict, List
import together
import torch
import os
import subprocess
import signal
import sys
import logging
import httpx
from openai import OpenAI, DefaultHttpxClient
from together import Together


# Custom transport to bypass SSL verification
transport = httpx.HTTPTransport(local_address="0.0.0.0", verify=False)

# Create a DefaultHttpxClient instance with the custom transport
http_client = DefaultHttpxClient(transport=transport)

# Define utility functions and classes
def kill_processes_on_ports(
    ports: List[int],
    *,
    force: bool = True,
    timeout: float = 5.0
) -> Dict[str, any]:
    """
    Kill processes bound to any port in `ports`.

    Uses lsof (macOS/Linux) instead of psutil.net_connections() to avoid
    the PermissionError that psutil raises on macOS without elevated privileges.

    Args:
        ports: List of port numbers to check and kill processes on
        force: Send SIGKILL if not gone after timeout
        timeout: Seconds to wait after SIGTERM before SIGKILL

    Returns:
        Dict with details:
        {
            'pids_targeted': [int],
            'terminated': [int],
            'killed': [int],
            'errors': [{'pid': int, 'error': str}],
            'ports_with_no_match': [int]
        }

    Example:
        kill_processes_on_ports([5000, 8080, 3000])
    """
    import time

    target_ports = {int(p) for p in ports}
    results = {
        'pids_targeted': [],
        'terminated': [],
        'killed': [],
        'errors': [],
        'ports_with_no_match': []
    }

    # Use lsof to find PIDs listening on the target ports (no elevated privileges needed)
    pids = set()
    matched_ports = set()
    for port in target_ports:
        try:
            out = subprocess.check_output(
                ["lsof", "-ti", f"tcp:{port}"],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            for line in out.splitlines():
                pid = int(line.strip())
                pids.add(pid)
                matched_ports.add(port)
        except (subprocess.CalledProcessError, ValueError):
            # No process on this port, or parse error
            pass

    results['pids_targeted'] = sorted(pids)
    results['ports_with_no_match'] = sorted(target_ports - matched_ports)

    # Terminate (SIGTERM), wait, then force-kill (SIGKILL) if requested
    for pid in list(pids):
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            continue
        except PermissionError as e:
            results['errors'].append({'pid': pid, 'error': f'Access denied: {e}'})
            continue

    # Wait for processes to exit
    deadline = time.time() + timeout
    remaining = set(pids)
    while remaining and time.time() < deadline:
        time.sleep(0.2)
        still_alive = set()
        for pid in remaining:
            try:
                os.kill(pid, 0)  # Check if still running
                still_alive.add(pid)
            except ProcessLookupError:
                results['terminated'].append(pid)
        remaining = still_alive

    # Force-kill survivors
    if remaining and force:
        for pid in remaining:
            try:
                os.kill(pid, signal.SIGKILL)
                results['killed'].append(pid)
            except ProcessLookupError:
                results['terminated'].append(pid)
            except PermissionError as e:
                results['errors'].append({'pid': pid, 'error': f'Access denied on kill: {e}'})

    return results
def get_proxy_url():
    """
    Get the proxy URL from environment variable or fall back to Together.ai endpoint.
    Uses TOGETHER_BASE_URL environment variable set in Dockerfile.
    Defaults to https://api.together.xyz/ if not set.
    """
    return os.environ.get('TOGETHER_BASE_URL', 'https://api.together.xyz/')

def get_proxy_headers():
    """
    Get the appropriate headers for API calls based on the platform.
    Returns Authorization header with Together API key if available.
    """
    return {"Authorization": os.environ.get("TOGETHER_API_KEY", "")}

def get_together_key():
    """
    Get the Together API key from environment variables.
    """
    return os.environ.get("TOGETHER_API_KEY", "")

def generate_embedding(prompt: str, model: str = "BAAI/bge-base-en-v1.5", together_api_key = None, **kwargs):
    payload = {
        "model": model,
        "input": prompt,
        **kwargs
    }
    if (not together_api_key) and ('TOGETHER_API_KEY' not in os.environ):
        client = OpenAI(
            api_key = '', # Set any as dlai proxy does not use it. Set the together api key if using the together endpoint
            base_url=get_proxy_url(), # Platform-agnostic proxy URL
            http_client=http_client, # ssl bypass to make it work via proxy calls, remove it if running with together.ai endpoint
        )
        try:
            json_dict = client.embeddings.create(**payload).model_dump()
            return json_dict['data'][0]['embedding']
        except Exception as e:
            raise Exception(f"Failed to get correct output from LLM call.\nException: {e}")
    else:
        if together_api_key is None:
            together_api_key = os.environ['TOGETHER_API_KEY']
        from together import Together
        client = Together(api_key=together_api_key)
        try:
            json_dict = client.embeddings.create(**payload).model_dump()
            return json_dict['data'][0]['embedding']
        except Exception as e:
            raise Exception(f"Failed to get correct output from LLM call.\nException: {e}")


def generate_with_single_input(prompt: str,
                               role: str = 'user',
                               top_p: float = None,
                               temperature: float = None,
                               max_tokens: int = 500,
                               model: str ="meta-llama/Llama-3.2-3B-Instruct-Turbo",
                               together_api_key = None,
                              **kwargs):

    # Remove None parameters for Together API - don't set to string 'none'
    if top_p is None:
        payload_top_p = None
    else:
        payload_top_p = top_p
    if temperature is None:
        payload_temperature = None
    else:
        payload_temperature = temperature

    payload = {
        "model": model,
        "messages": [{'role': role, 'content': prompt}],
        "max_tokens": max_tokens,
        **kwargs
    }
    # Only add temperature and top_p if they're not None
    if payload_temperature is not None:
        payload["temperature"] = payload_temperature
    if payload_top_p is not None:
        payload["top_p"] = payload_top_p

    if (not together_api_key) and ('TOGETHER_API_KEY' not in os.environ):
        url = os.path.join(get_proxy_url(), 'v1/chat/completions')
        response = requests.post(url, json = payload, verify=False)
        if not response.ok:
            raise Exception(f"Error while calling LLM: {response.text}")
        try:
            json_dict = json.loads(response.text)
        except Exception as e:
            raise Exception(f"Failed to get correct output from LLM call.\nException: {e}\nResponse: {response.text}")
    else:
        if together_api_key is None:
            together_api_key = os.environ['TOGETHER_API_KEY']
        from together import Together
        client = Together(api_key =  together_api_key)
        json_dict = client.chat.completions.create(**payload).model_dump()
        json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()
    try:
        output_dict = {'role': json_dict['choices'][-1]['message']['role'], 'content': json_dict['choices'][-1]['message']['content']}
    except Exception as e:
        raise Exception(f"Failed to get correct output dict. Please try again. Error: {e}")
    return output_dict


def generate_with_multiple_input(messages: List[Dict],
                               top_p: float = None,
                               temperature: float = None,
                               max_tokens: int = 500,
                               model: str ="meta-llama/Llama-3.2-3B-Instruct-Turbo",
                                together_api_key = None,
                                **kwargs):
    # Remove None parameters for Together API
    if top_p is None:
        payload_top_p = None
    else:
        payload_top_p = top_p
    if temperature is None:
        payload_temperature = None
    else:
        payload_temperature = temperature

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        **kwargs
    }
    # Only add temperature and top_p if they're not None
    if payload_temperature is not None:
        payload["temperature"] = payload_temperature
    if payload_top_p is not None:
        payload["top_p"] = payload_top_p

    if (not together_api_key) and ('TOGETHER_API_KEY' not in os.environ):
        url = os.path.join(get_proxy_url(), 'v1/chat/completions')
        response = requests.post(url, json = payload, verify=False)
        if not response.ok:
            raise Exception(f"Error while calling LLM: {response.text}")
        try:
            json_dict = json.loads(response.text)
        except Exception as e:
            raise Exception(f"Failed to get correct output from LLM call.\nException: {e}\nResponse: {response.text}")
    else:
        if together_api_key is None:
            together_api_key = os.environ['TOGETHER_API_KEY']
        from together import Together
        client = Together(api_key =  together_api_key)
        json_dict = client.chat.completions.create(**payload).model_dump()
        json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()
    try:
        output_dict = {'role': json_dict['choices'][-1]['message']['role'], 'content': json_dict['choices'][-1]['message']['content']}
    except Exception as e:
        raise Exception(f"Failed to get correct output dict. Please try again. Error: {e}")
    return output_dict




def print_object_properties(obj: Union[dict, list]) -> None:
    t = ''
    if isinstance(obj, dict):
        for x,y in obj.items():
            if x == 'article_content':
                t += f'{x}: {y[:100]}...(truncated)\n'
            elif x == 'main_vector':
                t+= f'{x}: {y[:30]}...(truncated)\n'
            elif x == 'chunk':
                t+= f'{x}: {y[:100]}...(truncated)\n'

            else:
                t+= f'{x}: {y}\n'
    else:
        for l in obj:
            for x,y in l.items():
                if x == 'article_content':
                    t += f'{x}: {y[:100]}...(truncated)\n'
                elif x == 'main_vector':
                    t+= f'{x}: {y[:30]}...(truncated)\n'
                elif x == 'chunk':
                    t+= f'{x}: {y[:100]}...(truncated)\n'

                else:
                    t+= f'{x}: {y}\n'
            t += "\n\n"
        
    print(t)


def print_properties(item):
    print(
        json.dumps(
            item.properties,
            indent=2, sort_keys=True, default=str
        )
    )

import subprocess
from contextlib import contextmanager

@contextmanager
def suppress_subprocess_output():
    """
    Context manager that suppresses the standard output and error 
    of any subprocess.Popen calls within this context.
    """
    # Store the original Popen
    original_popen = subprocess.Popen

    def patched_popen(*args, **kwargs):
        # Redirect the stdout and stderr to subprocess.DEVNULL
        kwargs['stdout'] = subprocess.DEVNULL
        kwargs['stderr'] = subprocess.DEVNULL
        return original_popen(*args, **kwargs)

    try:
        # Apply the patch by replacing subprocess.Popen with patched_popen
        subprocess.Popen = patched_popen
        # Yield control back to the context
        yield
    finally:
        # Ensure that the original Popen method is restored
        subprocess.Popen = original_popen
