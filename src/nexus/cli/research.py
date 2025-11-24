#!/usr/bin/env python3
"""
Research Agent CLI
==================

Command-line interface for the Nexus Research Agent.

Usage:
    nexus-research "your research topic" [options]

After installation with `pip install -e .`, this module is registered
as the `nexus-research` command and can be invoked from anywhere.
"""

from nexus.agents.research.run import main


if __name__ == "__main__":
    main()
