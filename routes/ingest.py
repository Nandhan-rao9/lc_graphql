from flask import Blueprint, jsonify, current_app
from datetime import datetime
from utils.db import db

ingest_bp = Blueprint("ingest", __name__)
problems_col = db["problems_master"]

PROBLEMSET_QUERY = """
query problemsetQuestionList(
  $categorySlug: String,
  $limit: Int!,
  $skip: Int!,
  $filters: QuestionListFilterInput
) {
  questionList(
    categorySlug: $categorySlug
    limit: $limit
    skip: $skip
    filters: $filters
  ) {
    totalNum
    data {
      acRate
      difficulty
      questionFrontendId
      isPaidOnly
      title
      titleSlug
      hasSolution
      hasVideoSolution
      topicTags {
        name
        slug
      }
    }
  }
}
"""

@ingest_bp.route("/api/ingest/problems", methods=["POST"])
def ingest_all_problems():
    leetcode_client = current_app.config["LEETCODE_CLIENT"]

    limit = 100
    skip = 0
    total = None
    synced = 0

    while total is None or skip < total:
        data = leetcode_client.fetch(
            PROBLEMSET_QUERY,
            {
                "categorySlug": "",
                "limit": limit,
                "skip": skip,
                "filters": {}
            }
        )

        if not data or "data" not in data:
            return jsonify({"error": "LeetCode fetch failed"}), 500

        plist = data["data"]["questionList"]
        total = plist["totalNum"]

        for q in plist["data"]:
            doc = {
                "_id": q["titleSlug"],

                "frontendQuestionId": int(q["questionFrontendId"]),
                "title": q["title"],
                "difficulty": q["difficulty"],
                "acRate": round(q["acRate"], 2),
                "paidOnly": q["isPaidOnly"],

                "hasSolution": q["hasSolution"],
                "hasVideoSolution": q["hasVideoSolution"],

                "topics": [t["slug"] for t in q["topicTags"]],
                "topic_meta": q["topicTags"],

                "companies": [],
                "by_company": {},
                "num_occur": 0,

                "last_updated": datetime.utcnow()
            }

            problems_col.update_one(
                {"_id": doc["_id"]},
                {"$set": doc},
                upsert=True
            )

            synced += 1

        skip += limit

    return jsonify({
        "status": "success",
        "total_synced": synced
    })
