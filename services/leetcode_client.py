# services/leetcode_client.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class LeetCodeClient:
    def __init__(self):
        self.session = requests.Session()
        self.url = "https://leetcode.com/graphql"

        self.session_id = os.getenv("LEETCODE_SESSION")
        self.csrf_token = os.getenv("CSRF_TOKEN")

        if not self.session_id or not self.csrf_token:
            raise RuntimeError(
                "Missing LeetCode auth tokens. "
                "Set LEETCODE_SESSION and CSRF_TOKEN in .env"
            )

        # Cookies (browser-equivalent)
        self.session.cookies.set("LEETCODE_SESSION", self.session_id)
        self.session.cookies.set("csrftoken", self.csrf_token)

        # Headers
        self.headers = {
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "X-CSRFToken": self.csrf_token
        }

    def fetch(self, query, variables=None):
        payload = {
            "query": query,
            "variables": variables or {}
        }

        try:
            response = self.session.post(
                self.url,
                json=payload,
                headers=self.headers,
                timeout=15
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[LeetCodeClient] Request failed: {e}")
            return None
