#!/usr/bin/env python3
"""Command-line interface for data synchronization.

Usage:
    python sync.py              # Sync latest data (yesterday or 2 days ago)
    python sync.py once         # Same as above
    python sync.py backfill 7   # Backfill last 7 days
    python sync.py range 2025-11-01 2025-11-15  # Sync specific date range
    python sync.py scheduler    # Run continuous scheduler (daily at 2 AM)
"""
import sys
from utils.scheduler import *

if __name__ == '__main__':
    # Forward to scheduler module
    pass  # The scheduler module's __main__ block will handle this
