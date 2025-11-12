"""
Email Agent Package

A self-contained agent demonstrating the tool use pattern for email management.
Includes email tools, server infrastructure, and educational notebooks.

Usage:
    from tool_use.email_agent import email_tools
    from tool_use.email_agent.email_tools import send_email, list_unread_emails
"""

from . import email_tools

__all__ = ['email_tools']
