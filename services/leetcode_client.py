import requests
from config import Config

def make_leetcode_request(query, variables=None):
    """
    Generic wrapper to send GraphQL queries to LeetCode.
    """
    payload = {
        "query": query,
        "variables": variables or {}
    }
    
    headers = {
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.post(Config.LEETCODE_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to LeetCode: {e}")
        return None