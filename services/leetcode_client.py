import requests
import os
import time
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from services.queries import USER_SUBMISSION_LIST_QUERY, GET_PROBLEMS_QUERY

load_dotenv()

class LeetCodeClient:
    def __init__(self):
        self.session = requests.Session()
        self.url = "https://leetcode.com/graphql/"

        # Cookies
        self.session.cookies.set("LEETCODE_SESSION", os.getenv("LEETCODE_SESSION"), domain=".leetcode.com")
        self.session.cookies.set("csrftoken", os.getenv("LEETCODE_CSRF"), domain=".leetcode.com")

        # Headers
        self.headers = {
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com",
            "Origin": "https://leetcode.com",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "x-csrftoken": os.getenv("LEETCODE_CSRF")
        }

        # Retry + backoff
        retry = Retry(
            total=5,
            backoff_factor=1.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )

        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    def fetch(self, query, variables):
        r = self.session.post(
            self.url,
            json={"query": query, "variables": variables},
            headers=self.headers,
            timeout=60
        )
        r.raise_for_status()
        return r.json()

    # -------------------------------
    # STEP 1: FETCH ACCEPTED SLUGS
    # -------------------------------
    def fetch_all_accepted_slugs(self):
        offset = 0
        limit = 50
        solved = set()
        page = 1

        while True:
            print(f"[LC] Fetching submissions page {page} (offset={offset})")

            data = self.fetch(
                USER_SUBMISSION_LIST_QUERY,
                {"offset": offset, "limit": limit}
            )

            block = data["data"]["submissionList"]
            subs = block["submissions"]

            if not subs:
                break

            for s in subs:
                if s["statusDisplay"] == "Accepted":
                    solved.add(s["titleSlug"])

            if not block.get("hasNext"):
                break

            offset += limit
            page += 1
            time.sleep(0.6)

        print(f"[LC] Total unique accepted problems: {len(solved)}")
        return solved

    # -----------------------------------
    # STEP 2: HYDRATE METADATA (FAST)
    # -----------------------------------
    def fetch_problem_metadata(self, slugs):
        problems = []
        found = set()

        skip = 0
        limit = 50
        page = 1

        print(f"[LC] Hydrating metadata for {len(slugs)} problems")

        while True:
            print(f"[LC] Scanning problem list page {page} (skip={skip})")

            data = self.fetch(
                GET_PROBLEMS_QUERY,
                {
                    "categorySlug": "",
                    "skip": skip,
                    "limit": limit,
                    "filters": {}
                }
            )

            qs = data["data"]["problemsetQuestionList"]["questions"]
            if not qs:
                break

            for q in qs:
                slug = q["titleSlug"]
                if slug in slugs and slug not in found:
                    problems.append(q)
                    found.add(slug)

            if len(found) == len(slugs):
                print("[LC] All problem metadata found, stopping early")
                break

            skip += limit
            page += 1
            time.sleep(0.6)

        print(f"[LC] Metadata hydrated: {len(problems)}")
        return problems
