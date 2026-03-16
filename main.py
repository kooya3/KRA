#!/usr/bin/env python3
"""
KRA Tax Filing System - Main Entry Point
"""

import sys
from src.cli import cli

if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)