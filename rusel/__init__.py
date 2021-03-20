"""Non-commercial product for personal use.

The main functionality is a task scheduler, notes, photo archive, and more.
"""

import sys
import asyncio

if sys.platform == "win32" and sys.version_info >= (3, 8, 0):
  asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())