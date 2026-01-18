from flask import Blueprint, jsonify, current_app
from utils.db import problems_master, user_solved_col

user_ingest_bp = Blueprint("user_ingest", __name__)

def normalize_problem(p):
    return {
        "title": p["title"],
        "slug": p["titleSlug"],
        "difficulty": p["difficulty"],
        "all_topics": [t["name"].lower() for t in p.get("topicTags", [])],
        "link": f"https://leetcode.com/problems/{p['titleSlug']}/"
    }

@user_ingest_bp.route("/api/ingest/user/<username>", methods=["POST"])
def ingest_user(username):
    client = current_app.config["LEETCODE_CLIENT"]
    solved_col = user_solved_col(username)

    # STEP 1
    slugs = client.fetch_all_accepted_slugs()

    # STEP 2
    problems = client.fetch_problem_metadata(slugs)

    inserted = 0
    for p in problems:
        doc = normalize_problem(p)

        problems_master.update_one(
            {"slug": doc["slug"]},
            {"$setOnInsert": doc},
            upsert=True
        )

        res = solved_col.update_one(
            {"slug": doc["slug"]},
            {"$setOnInsert": {"slug": doc["slug"]}},
            upsert=True
        )

        if res.upserted_id:
            inserted += 1

    return jsonify({
        "status": "success",
        "user": username,
        "unique_solved": len(slugs),
        "newly_ingested": inserted,
        "cached_total": solved_col.count_documents({})
    })
