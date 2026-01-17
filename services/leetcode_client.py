# services/leetcode_client.py
import requests
from config import Config

def make_leetcode_request(query, variables=None):
    payload = {
        "query": query,
        "variables": variables or {}
    }
    
    # These headers are critical to bypass Cloudflare and LeetCode's WAF
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://leetcode.com/problemset/all/",
        "Origin": "https://leetcode.com",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        # Use a timeout of 10-15 seconds for larger queries like the problem list
        response = requests.post(
            Config.LEETCODE_URL, 
            json=payload, 
            headers=headers, 
            timeout=15 
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"--- Connection Error Log ---")
        print(f"Reason: {e}")
        return None