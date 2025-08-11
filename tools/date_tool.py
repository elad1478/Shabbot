"""
Date Utility Tool
Provides a simple tool to get today's date (Gregorian) in ISO format.
"""
from datetime import date
from langchain_core.tools import tool


@tool
def get_today_date() -> str:
    """
    Return today's date (Gregorian) in YYYY-MM-DD format.
    """
    return date.today().isoformat()